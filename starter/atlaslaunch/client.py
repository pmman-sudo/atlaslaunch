"""Small synchronous N-ATLAS client for OpenAI-compatible and TGI deployments."""
import os
import time
from urllib.parse import urlsplit
import httpx

LANGUAGES = {"English", "Yoruba", "Hausa", "Igbo"}
MODEL = "NCAIR1/N-ATLaS"

class AtlasError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

class AtlasClient:
    def __init__(self, endpoint, token="", model=MODEL, protocol="openai", timeout=45, transport=None):
        url = urlsplit(endpoint)
        if url.scheme not in {"https", "http"} or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise AtlasError("INVALID_ENDPOINT", "Set a full inference URL without embedded credentials, query parameters or fragments.")
        if url.scheme == "http" and url.hostname not in {"localhost", "127.0.0.1", "::1", "host.docker.internal"}:
            raise AtlasError("INVALID_ENDPOINT", "Remote inference endpoints must use HTTPS.")
        if protocol not in {"openai", "tgi"}:
            raise AtlasError("INVALID_PROTOCOL", "Choose openai or tgi.")
        if not model.strip():
            raise AtlasError("INVALID_MODEL", "Set the model name served by your deployment.")
        self.endpoint, self.token, self.model, self.protocol = endpoint, token, model, protocol
        self.timeout, self.transport = timeout, transport

    @classmethod
    def from_env(cls):
        return cls(os.getenv("NATLAS_ENDPOINT", ""), os.getenv("NATLAS_TOKEN", ""), os.getenv("NATLAS_MODEL", MODEL), os.getenv("NATLAS_PROTOCOL", "openai"))

    def generate(self, prompt, language="English", max_tokens=192):
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 6000:
            raise AtlasError("INVALID_PROMPT", "Use a prompt of 1–6,000 characters.")
        if language not in LANGUAGES or not isinstance(max_tokens, int) or not 1 <= max_tokens <= 512:
            raise AtlasError("INVALID_PARAMETERS", "Choose a supported language and 1–512 output tokens.")
        system = f"You are a helpful assistant. Respond in {language}. Be concise and state uncertainty when appropriate."
        if self.protocol == "openai":
            payload = {"model": self.model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.1, "stream": False}
        else:
            formatted = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            payload = {"inputs": formatted, "parameters": {"max_new_tokens": max_tokens, "temperature": 0.1, "return_full_text": False}}
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        start = time.perf_counter()
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=False, transport=self.transport) as client:
                with client.stream("POST", self.endpoint, headers=headers, json=payload) as response:
                    if not 200 <= response.status_code < 300:
                        messages = {
                            401: ("AUTHENTICATION_FAILED", "Check the endpoint token."),
                            403: ("ACCESS_DENIED", "Check model access and endpoint permissions."),
                            404: ("ENDPOINT_NOT_FOUND", "Check the URL path and API format."),
                            429: ("RATE_LIMITED", "Wait before retrying; check provider quota."),
                            503: ("MODEL_UNAVAILABLE", "Check whether the model is starting or unavailable."),
                        }
                        code, message = messages.get(response.status_code, ("UPSTREAM_ERROR", f"Inference service returned HTTP {response.status_code}. Redirects are not followed."))
                        raise AtlasError(code, message)
                    chunks, size = [], 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > 512000:
                            raise AtlasError("RESPONSE_TOO_LARGE", "Response exceeded 500 KB.")
                        chunks.append(chunk)
            import json
            data = json.loads(b"".join(chunks))
        except httpx.TimeoutException as error:
            raise AtlasError("TIMEOUT", "Inference timed out. Check deployment status.") from error
        except httpx.RequestError as error:
            raise AtlasError("NETWORK_ERROR", "Could not reach the inference endpoint.") from error
        except ValueError as error:
            raise AtlasError("INVALID_RESPONSE", "The endpoint returned invalid JSON.") from error
        text, reported_model, tokens = None, None, None
        if isinstance(data, list) and data and isinstance(data[0], dict):
            text = data[0].get("generated_text")
        elif isinstance(data, dict):
            text = data.get("generated_text")
            try:
                text = data["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError):
                pass
            reported_model = data.get("model")
            usage = data.get("usage")
            tokens = usage.get("total_tokens") if isinstance(usage, dict) else None
        if not isinstance(text, str) or not text.strip():
            raise AtlasError("INVALID_RESPONSE", "No usable text returned. Check the API format.")
        return {"text": text, "latency_ms": round((time.perf_counter()-start)*1000), "reported_model": reported_model if isinstance(reported_model, str) else None, "tokens": tokens if isinstance(tokens, int) else None, "configured_model": self.model, "mode": "live"}
