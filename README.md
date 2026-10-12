# AtlasLaunch

**Connect to N-ATLaS. Test across languages. Keep evidence you can review.**

AtlasLaunch is a developer workbench for trying an N-ATLaS deployment, running repeatable multilingual prompts, recording quality reviews, and exporting results. It combines a web interface, a Python starter, and a Modal deployment kit.

Developers integrating a model need to answer two separate questions: does the endpoint respond, and is the answer useful? AtlasLaunch puts connection diagnostics, response inspection, timings, reviewer notes, and exports in one workflow.

Built by **Paul Iyen**. Independent project; not an official NCAIR product.

## Current status

- A real N-ATLaS deployment on Modal answered the owner's first direct API test.
- The hosted workbench completed five live requests: one playground request and four language smoke tests on **11 October 2026**.
- All five requests completed without errors; this is transport success, **not 100% answer accuracy**.
- The exported report contains preliminary AI review notes. **Zero human quality scores and zero external developer tests** are included so far.
- [Northflank workbench](https://p01--drainwatch-api--v8qxqym2945f.code.run) — deployed 12 October 2026; no ChatGPT account needed. Enter the endpoint API key privately supplied by the owner for live inference.
- The earlier [ChatGPT-hosted workbench](https://atlaslaunch.pauliyen248.chatgpt.site) is a separate deployment with its own access controls.

See [evidence and limitations](docs/EVIDENCE.md). The report is an owner-supplied export, not independent verification of the served weights.

## What you can do

- Configure an OpenAI-compatible chat or TGI endpoint.
- Send prompts with English, Yoruba, Hausa, or Igbo response instructions.
- Run up to 20 editable test cases sequentially.
- Inspect response times, errors, reported model identifiers, and token usage when supplied.
- Record human scores and review notes; export JSON or CSV.
- Use an explicitly labelled local fixture to test UI behavior without a model call.
- Download or reuse the FastAPI/Python/Docker starter and Modal hosting kit.

There is no automatic fallback to a different model. A language selection is an instruction to the model, not a guarantee of correct output.

## Run the web app locally

Requirements: **Node.js 24**, npm, and Git. You do not need a GPU to run the web interface. A live request needs a separately hosted endpoint and its access key.

From the folder containing `package.json`:

```powershell
npm ci
npm run dev
```

Open **http://localhost:3000**. Choose **Local fixture** for a no-credential software demonstration, or configure your live endpoint:

| Field | Value for the included Modal deployment |
| --- | --- |
| Inference endpoint | Your Modal base URL plus `/v1/chat/completions` |
| API format | OpenAI-compatible chat |
| Served model name | `NCAIR1/N-ATLaS` |
| Access token | Your `ATLAS_API_KEY` from the Modal setup |

Click **Check connection**, then use **Playground** or **Test & review**. Connection checks make a real inference request and consume provider compute. Your Hugging Face token is used only by the model host to download gated weights; it is not the workbench access key.

Export results before refreshing or closing the tab. This prototype keeps results and credentials in tab memory, with no results database or import feature.

## Deploy the model on Modal

Follow [the Modal deployment guide](starter/modal_host/README.md). It covers gated-model access, budget settings, hidden token entry, deployment, and the first live test. The GPU runs on Modal; the laptop only runs the CLI.

The included configuration uses a T4, 4-bit NF4 quantization, a single maximum GPU container, and scaling to zero after inactivity. Startup and requests consume credits. Credits are a limited allowance, not unlimited free hosting. Verify current [Modal pricing](https://modal.com/pricing) and [budget settings](https://modal.com/docs/guide/budgets) before deployment.

If a browser request exceeds its cold-start timeout, run the included `check_endpoint.py` locally to warm the model before retrying. See [troubleshooting](docs/TROUBLESHOOTING.md).

## Repository guide

| Path | Purpose |
| --- | --- |
| `app/` | Web interface and server-side `/api/infer` route |
| `lib/natlas.ts` | Endpoint validation, protocol adapter, parsing, errors |
| `tests/` | Mocked inference adapter tests |
| `starter/` | Optional local FastAPI wrapper, Python SDK, Docker and test runner |
| `starter/modal_host/` | Authenticated CPU gateway and T4 model deployment |
| `docs/evidence/` | Owner's recorded responses and review notes |
| `docs/DEVELOPER_TEST.md` | Two-developer testing protocol and blank feedback form |
| `.github/workflows/ci.yml` | Web and Python checks; no paid deployments |

## Checks

```powershell
npm test
npm run typecheck
npm run build
```

Python tests (from the repository root, with uv installed):

```powershell
uv venv --python 3.12 .venv-tests
uv pip install --python .\.venv-tests\Scripts\python.exe -r starter/requirements-dev.txt
cd starter
..\.venv-tests\Scripts\python.exe -m pytest -q
```

Automated tests use mocked inference and require no model credentials or GPU. CI does not deploy infrastructure. To run a production build locally, use `npm run build` then `npm start`. Rebuild the downloadable ZIPs after starter edits with `python scripts/package-starter.py` (Git-tracked files only; stage new source files first).

## Hosting and security boundaries

This repository is a **standalone Next.js adaptation** of the working Sites/Vinext app. It retains the UI and inference adapter, replaces the Cloudflare environment binding with `process.env`, and excludes platform-specific deployment/authentication files. See [architecture](docs/ARCHITECTURE.md).

The local server binds to `127.0.0.1`. This standalone version does **not** include user login, rate limiting, or the hosted site's private-access protection. Add those controls before exposing it publicly. An origin check is not authentication. The app needs a server runtime for `/api/infer`; GitHub Pages alone cannot host the full application.

The proxy allows HTTPS hosts under `*.modal.run` and `*.endpoints.huggingface.cloud`, with optional trusted hosts in `NATLAS_ALLOWED_HOSTS`. It rejects redirects and credential-bearing URLs. A provider hostname is not proof of endpoint ownership: only send a key to an endpoint you trust. Access keys pass through the app server and are excluded from exports. Do not add request-body logging or commit secrets.

## Next milestones

- Collect independent feedback from two developers using distinct aliases.
- Arrange reviewer access and record a short demo.
- Obtain fluent-speaker reviews of language quality.
- Add persistence, comparison workflows, authentication, and request quotas before a wider launch.

Source: [pmman-sudo/atlaslaunch](https://github.com/pmman-sudo/atlaslaunch). See [Northflank deployment settings](docs/NORTHFLANK.md).

## Attribution and license status

N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy, and powered by Awarri Technologies. Model reference: [NCAIR1/N-ATLaS](https://huggingface.co/NCAIR1/N-ATLaS).

No model weights are included. Access and use of the model remain subject to its separate terms. Third-party packages retain their own licenses. A redistribution license for the AtlasLaunch application has not yet been selected; this preparation does not grant an open-source license.
