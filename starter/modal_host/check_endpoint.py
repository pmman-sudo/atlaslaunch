"""Authenticated warm-up; prompts for the API key without echoing it."""
import json
from datetime import datetime, timezone
from getpass import getpass
from urllib.parse import urlsplit, urljoin

import httpx

base = input("Modal base URL (https://...modal.run): ").strip().rstrip("/")
url = urlsplit(base)
if (url.scheme != "https" or not (url.hostname or "").endswith(".modal.run")
        or url.username or url.password or url.query or url.fragment
        or url.path or url.port not in (None, 443)):
    raise SystemExit("Enter only the HTTPS Modal base URL, without a path or credentials.")
key = getpass("AtlasLaunch API key (not your Hugging Face token): ").strip()
endpoint = base + "/v1/chat/completions"
payload = {"model": "NCAIR1/N-ATLaS", "messages": [
    {"role": "system", "content": "Answer clearly in English."},
    {"role": "user", "content": "Explain how solar panels work in two short sentences."},
], "max_tokens": 128, "temperature": 0, "stream": False}
print("Warming up N-ATLAS. The first download/load may take several minutes.")
with httpx.Client(timeout=900, follow_redirects=False) as client:
    response = client.post(endpoint, headers={"Authorization": "Bearer " + key}, json=payload)
    # Modal uses same-origin 303 result URLs when requests exceed 150 seconds.
    # Poll that result with GET; never repeat generation or forward a key to another host.
    for _ in range(6):
        if response.status_code != 303:
            break
        target = urljoin(str(response.url), response.headers.get("location", ""))
        parsed = urlsplit(target)
        if (not response.headers.get("location") or parsed.scheme != "https"
                or parsed.netloc != url.netloc or parsed.username or parsed.password):
            raise SystemExit("Refusing an unexpected redirect; check the endpoint in Modal.")
        print("Model still loading; waiting for the same request to complete...")
        response = client.get(target, headers={"Authorization": "Bearer " + key})
if response.status_code != 200:
    raise SystemExit(f"Endpoint returned HTTP {response.status_code}. Check Modal logs and credentials.")
result = response.json()
print(result["choices"][0]["message"]["content"])
record = {"exported_at_utc": datetime.now(timezone.utc).isoformat(),
          "endpoint": endpoint, "request": payload, "response": result}
with open("modal-first-live-run.json", "w", encoding="utf-8") as f:
    json.dump(record, f, ensure_ascii=False, indent=2)
print("Saved modal-first-live-run.json (no API key included).")
print("AtlasLaunch endpoint:", endpoint)
