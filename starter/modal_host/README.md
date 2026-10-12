# AtlasLaunch on Modal

This deploys your own N-ATLAS weights as a small authenticated, non-streaming chat API.
No other model is substituted. The pinned model revision is
`e294476928aca9030e924ca27bb8e085e8581273`.

## 1. Account and budget (do this before deploying)

Create a Modal Starter account at https://modal.com/ and check Usage & Billing.
As checked on 11 October 2026, Starter includes $30/month compute credits and
requires a payment method. This is an allowance, not unlimited free hosting.
Verify the credits actually awarded to your workspace. Set the workspace **spend
limit to $0 out of pocket**, and set its usage budget to no more than the available
included credit (normally $30). Modal's usage budget is BEFORE credits; the spend
limit is AFTER credits. If your dashboard cannot save those settings, resolve that
before deploying. Shared Endpoints are separately billed and aren't used here.

GPU startup, loading weights, requests and the warm idle window consume credits.
One GPU container is the maximum; minimum is zero; idle window is 60 seconds.
This caps concurrency, NOT monthly cost. Protect your API key and monitor billing.

References:
- https://modal.com/pricing
- https://modal.com/docs/guide/billing
- https://modal.com/docs/guide/budgets

## 2. Install locally on Windows

Install uv from https://docs.astral.sh/uv/getting-started/installation/. From the repository root, run `cd starter/modal_host`, then run the commands below. For a downloaded ZIP, open the folder that actually contains `modal_app.py`.

```powershell
uv venv --python 3.12 .venv
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
.\.venv\Scripts\python.exe -m modal setup
```

Complete browser login for your Modal workspace. No model weights or GPU libraries
are installed on your laptop; they are installed on Modal during its image build.

## 3. Store secrets

```powershell
.\.venv\Scripts\python.exe setup_secrets.py
```

Paste your existing gated-read Hugging Face token into the hidden prompt. The script
creates a Modal Secret named `atlaslaunch-secrets` with `HF_TOKEN` and a randomly
generated `ATLAS_API_KEY`. It prints the new API key once for you to save securely.
Do not share either key in chat, screenshots, Git or reports. The new API key goes
into AtlasLaunch; the Hugging Face token stays in Modal for loading the model.
If the secret already exists, this script fails instead of replacing it. Manage
existing values in Modal's Secrets dashboard. Never rerun it to rotate a live key
without intentionally updating the secret and redeploying.

## 4. Deploy (consumes the workspace's compute allowance)

```powershell
.\.venv\Scripts\python.exe -m modal deploy modal_app.py
```

Wait for the image build. Copy the HTTPS web URL ending in `.modal.run` from the
output. There is no need to keep PowerShell or Colab open after deployment.
Model weights are cached in the private Modal Volume `atlaslaunch-model-cache`.
The GPU loads the model on the first authenticated inference request, not during
the laptop command. The image uses your tested library versions, but Modal GPU
compatibility still requires a successful live run; local contract tests do not
prove GPU deployment success.

## 5. Warm up and save the first live run

```powershell
.\.venv\Scripts\python.exe check_endpoint.py
```

Enter the base Modal URL (no path) and the new AtlasLaunch API key when asked.
First startup/download may take several minutes. Subsequent cold starts reload
cached weights. The script follows only same-origin Modal 303 result redirects,
without resubmitting the prompt. It saves `modal-first-live-run.json` without keys.
The protected `/health` route checks only the gateway; it does not start the GPU.

## 6. Connect the workbench

Open https://atlaslaunch.pauliyen248.chatgpt.site and select **Live endpoint**.

| Field | Value |
| --- | --- |
| Inference endpoint | Your Modal base URL plus `/v1/chat/completions` |
| API format | OpenAI-compatible chat |
| Served model name | `NCAIR1/N-ATLaS` |
| Access token | Your new `ATLAS_API_KEY` |

Click Check connection. Then run the playground and suite. Export actual results.
The workbench allows 120 seconds for Modal responses and never follows redirects.
If cold start takes longer, use `check_endpoint.py` to warm the model, then retry
in the workbench. Do not repeatedly click Check connection during a cold start.
The workbench remains owner-private until you explicitly arrange tester access.

## Limits and shutdown

- Chat Completions subset only: text messages, no streaming, tools or attachments.
- 2048 input tokens, 512 maximum generated tokens, one active GPU container.
- Auth is checked in the CPU gateway before GPU work; failed auth can still use
  small amounts of gateway CPU. This demo is not a fully rate-limited public API.
- This code doesn't persist prompts or answers on Modal. Operators should still
  review platform logging policies. Downloaded local reports include prompt text.
- Language/quality failures remain visible; a completed request is not an accuracy pass.
- Stop the `atlaslaunch-natlas` App in Modal's dashboard when finished. Stopping
  the app does not delete its cached model volume or Secret. Delete those separately
  if you no longer need them. Never publish the gated weights.

N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation
and Digital Economy, and powered by Awarri Technologies.

## Verified owner run

On 11 October 2026, the owner successfully ran this Modal deployment and five live requests through the hosted workbench. See `docs/EVIDENCE.md` in the full repository. This does not establish production reliability or language accuracy. The standalone Next.js frontend is a portability adaptation of the hosted Sites version.
