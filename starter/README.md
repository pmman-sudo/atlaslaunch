# AtlasLaunch — N-ATLAS developer starter

A local FastAPI adapter, Python client, repeatable test runner and Docker/CI setup for an **existing N-ATLAS inference deployment**.

This package does not contain model weights and does not deploy the 8B model. You need access to a real deployment before generating model responses. The unit tests use mocked transports; they do not demonstrate N-ATLAS performance.

## 1. Get model access

Open https://huggingface.co/NCAIR1/N-ATLaS and review/accept the model's access conditions. The model repository URL is not an inference API.

Obtain an authorised endpoint that serves N-ATLAS through one of these supported interfaces:

| Interface | Typical full path | Setting |
| --- | --- | --- |
| OpenAI-compatible chat (for example a suitable vLLM/TGI deployment) | `/v1/chat/completions` | `NATLAS_PROTOCOL=openai` |
| Hugging Face Text Generation Inference | `/generate` | `NATLAS_PROTOCOL=tgi` |

The chat format does not mean this uses OpenAI's models: it is an API protocol. You must configure and verify that your deployment actually serves N-ATLAS. An organiser-provided custom API may need a new adapter. Never substitute another model and claim N-ATLAS integration.

Record the deployed repository, revision, serving software version, hardware and generation settings. A server-reported model name alone does not prove which weights are running. Check the model terms before commercial or large-scale deployment.

## 2. Start on Windows with Docker Desktop

Unzip this folder and open PowerShell **inside it**. Docker Desktop must be running.

```powershell
Copy-Item .env.example .env
notepad .env
```

Replace the placeholder endpoint with your **full** inference URL. Set `NATLAS_TOKEN` if your endpoint requires one. Keep `.env` private; do not paste tokens into chat or commit them to GitHub.

```powershell
docker compose up --build
```

Open http://localhost:8000/docs. `GET /health` checks the wrapper only. Use `POST /check` for an actual short inference request, then `POST /generate`:

```json
{"prompt":"Explain how solar panels work in two sentences.","language":"English","max_tokens":192}
```

Stop with Ctrl+C, then `docker compose down`. The Compose service is bound to your machine's loopback interface. Add authentication and usage controls before exposing it publicly.

If the model runs on your host PC, a Docker container reaches it through `host.docker.internal`, not `localhost`. For a local wrapper without Docker, use the normal localhost inference URL. Remote URLs require HTTPS.

## 3. Run without Docker

Python 3.12 recommended. No PowerShell execution-policy change is needed:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --no-access-log
```

On Linux/macOS replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`; use `python3 -m venv .venv` and `cp .env.example .env`.

## 4. Use the Python client

```python
from dotenv import load_dotenv
from atlaslaunch import AtlasClient, AtlasError

load_dotenv()
client = AtlasClient.from_env()
try:
    result = client.generate("Explain how solar panels work.", language="Hausa")
    print(result["text"])
except AtlasError as error:
    print(error.code, str(error))
```

## 5. Run repeatable real requests

Edit `cases.json`, then run from another terminal:

```powershell
.\.venv\Scripts\python.exe run_suite.py --cases cases.json --output report.json --tester tester-01
```

Or through Docker:

```powershell
docker compose exec api python run_suite.py --output /tmp/report.json --tester tester-01
docker compose cp api:/tmp/report.json ./report.json
```

The runner sends requests sequentially with no automatic retries. It saves completed rows after every case, including errors. Output timing includes network time. The four starter cases are a **smoke test**, not a validated benchmark. Ask fluent speakers to review language quality. Do not invent results, user counts or quality scores.

## 6. Test the software

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests cover request construction, parsing, authentication/permission errors, timeout handling and API validation using mocks. No credentials or GPU are required for these tests. Passing unit tests is not the same as passing a live-model integration test.

The full AtlasLaunch repository includes a root GitHub Actions workflow that runs these checks with `working-directory: starter`. The standalone starter download does not include its own workflow.

## Troubleshooting

| Code | Action |
| --- | --- |
| INVALID_ENDPOINT | Set the full API URL in `.env`; a model-page URL is not enough. |
| AUTHENTICATION_FAILED | Check the token and permissions. |
| ACCESS_DENIED | Confirm model access and endpoint permissions. |
| ENDPOINT_NOT_FOUND | Check the full path and selected protocol. |
| RATE_LIMITED | Wait and inspect provider limits. |
| MODEL_UNAVAILABLE / TIMEOUT | Check deployment readiness and compute resources. |
| INVALID_RESPONSE | Confirm the endpoint returns a supported JSON shape. |

## Files

- `atlaslaunch/client.py`: small reusable inference client.
- `app.py`: local `/health`, `/check` and `/generate` routes.
- `run_suite.py` and `cases.json`: reproducible smoke tests.
- `Dockerfile` and `compose.yaml`: containerised local API.
- `tests/`: mocked software tests; CI lives in the full repository at `.github/workflows/ci.yml`.
- `TESTER_WORKSHEET.md`: external developer validation template.

## Attribution

AtlasLaunch is an independent toolkit, not an official NCAIR product. No model weights are distributed with it.

N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy, and powered by Awarri Technologies.

Official references: https://huggingface.co/NCAIR1/N-ATLaS and https://ncair.nitda.gov.ng/naic/.

## Host your own model on Modal

See [modal_host/README.md](modal_host/README.md) for the GPU deployment kit. It requires your own account, secrets and spending controls.
