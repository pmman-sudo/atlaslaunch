# Troubleshooting

## Windows venv fails inside ensurepip

The owner encountered this with Python 3.14 and 3.12. Use uv to avoid pip bootstrapping:

```powershell
uv venv --python 3.12 .venv
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
```

Run inside `starter/modal_host`. Invoke the CLI as `.\.venv\Scripts\python.exe -m modal` rather than relying on activation or PATH. No execution-policy change is required.

## Hugging Face 401/403 during model startup

Check `HF_TOKEN` in the Modal Secret `atlaslaunch-secrets`. It must be the complete token belonging to an account with access to `NCAIR1/N-ATLaS`. Fine-grained tokens need gated-repository read permission. The masked value in the token list is not a usable credential.

Stop a crash-looping app while correcting the secret. Keep `ATLAS_API_KEY` unchanged when only correcting the Hugging Face token. Redeploy to start containers with the corrected secret. An HTTP 200 download of the pinned `config.json` confirms access for the token tested, but not necessarily the value saved in Modal.

## Endpoint returns 500 or 503

Inspect `python -m modal app logs atlaslaunch-natlas`. A successful deployment does not prove successful model startup. Do not repeatedly submit requests while the worker is failing to initialize. Never include keys in a shared error report.

## Cold start exceeds browser timeout

The web adapter waits up to 120 seconds for Modal; other endpoints use 45 seconds. The CLI warm-up script follows same-origin result redirects for a longer initial startup. A warm GPU is allowed to scale down after 60 idle seconds, so a later request can require another load. Cold-start time is not a fixed promise.

## No results after page reload

Results and the endpoint key are stored in tab memory. Export JSON/CSV before reload. There is currently no import or persistent-results feature.

## Private website cannot be opened by a tester

The owner must arrange website access separately. Alternatively run this repository locally with an authorized endpoint credential. Do not publish the owner's keys to make access easier.
