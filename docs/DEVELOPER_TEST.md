# Developer trial: what to do and what to return

Thank you for testing AtlasLaunch. Your task is to connect to N-ATLaS, send a prompt, run four language cases, review an answer, and export your results. We want to learn whether another developer can complete this workflow and where the app needs improvement.

Allow about **20–30 minutes**, plus installation or model startup time. Honest failures and confusing steps are useful feedback. You do not need to deploy a model, own a GPU, create a Hugging Face account, or pay for hosting for this trial.

## Before you start

Ask Paul for:

- Your tester alias: `dev-01` or `dev-02` (one alias per actual person).
- Access to this private GitHub repository, or separately arranged access to the hosted app.
- The AtlasLaunch endpoint API key, shared privately, and confirmation that the endpoint is available for your test.
- An agreed private place to return your report and feedback.

Use a fresh browser tab and work independently before reading the other tester's feedback. Record your start time. Use non-sensitive prompts. Never put API keys in GitHub issues, screenshots, report notes, or commits.

## 1. Open the app

Choose **one** route.

### Route A — Run locally (optional for developers)

Install Git and Node.js **24** with npm if needed. Accept the repository invitation and sign into GitHub when prompted. In PowerShell or a terminal, run:

```sh
git clone https://github.com/pmman-sudo/atlaslaunch.git
cd atlaslaunch
git rev-parse HEAD
node --version
npm ci
npm run dev
```

Copy the commit printed by `git rev-parse HEAD` into your feedback. `node --version` should begin with `v24.`. Keep the terminal running and open **http://localhost:3000** in your browser. If the terminal reports a different port, use its displayed local URL.

If `git clone` says the repository cannot be found, check that you accepted the invitation and are using the invited GitHub account. If installation or startup fails, save the error text and ask Paul for help; record the help you needed.

### Route B — Use the hosted app

Open [AtlasLaunch on Northflank](https://p01--drainwatch-api--v8qxqym2945f.code.run). This is the simplest route for the trial: no installation or ChatGPT account is needed. The address still contains the old DrainWatch service name because AtlasLaunch reuses that service slot. For live inference, ask Paul for the endpoint API key privately. Record “Northflank hosted app” in your feedback. The older ChatGPT-hosted site is a separate deployment and is not required for this trial.

## 2. Connect to the live model

1. Select **Live endpoint** at the top of the app.
2. Open **Connection** in the sidebar.
3. Enter the following values, unless Paul supplies an updated endpoint:

| Field | Enter |
| --- | --- |
| Inference endpoint | `https://pmman-sudo--atlaslaunch-natlas-web.modal.run/v1/chat/completions` |
| API format | `OpenAI-compatible chat` |
| Served model name | `NCAIR1/N-ATLaS` |
| Access token | The AtlasLaunch API key Paul shared privately |

4. Click **Check connection** once. Wait for the result; the first request can be slow while the model starts.
5. Record the diagnostic message and the time of your first successful response.

**Expected:** “Response received.” and an “Endpoint reachable” status. This means a text response arrived; it does not prove the answer is correct.

Use the endpoint API key, **not** Paul's Hugging Face token or Modal credentials. Although the field says a token is optional for open endpoints, this deployment requires a key. Each connection check makes a real model request.

If you get an authentication error, ask Paul to check the endpoint key. If you get a timeout or model-starting error, send Paul the diagnostic so he can check or warm the deployment. Retry once after he confirms it is ready; do not repeatedly click the button. If still blocked, record the failure and use the fixture-only option below for UI feedback.

## 3. Send one prompt of your own

1. Open **Playground**.
2. Choose a **Response language** you understand.
3. Leave **Maximum output tokens** at `192`.
4. Replace the prompt with a short, non-sensitive task you can judge. For example: “Explain what an API is to a beginner in two short sentences.” Prefer a task relevant to something you might build.
5. Click **Run prompt** once and wait.
6. Read the response. Record whether it answers the question, follows your requested language and format, and has any obvious errors.

**Expected:** a response marked **LIVE REQUEST**, or a clear error. Note the displayed response time. Do not refresh the tab: results are stored only in this session.

## 4. Run the four starter cases

1. Open **Test & review**.
2. Enter your assigned alias in **Tester alias**.
3. Click **Reset cases** to restore the four default solar-panel prompts. Leave the JSON unchanged for this first trial.
4. Confirm **Live endpoint** is still selected.
5. Click **Run test suite** once. Wait until all four cases finish.
6. Inspect each result for a response or an error. The languages are English, Yoruba, Hausa, and Igbo.

**Expected:** five result rows after one playground prompt and one complete suite. The separate connection check does not appear in the results. If you retried a prompt or suite, extra rows are expected; explain the retries in your feedback. Do not remove failed attempts to make the report look better.

The **Successful responses** percentage measures requests without errors, not answer accuracy. Running the suite is a language smoke test, not a validated benchmark. Assess language quality only for languages you understand.

## 5. Add your review note and score

1. In **Results**, click a row to expand it.
2. Choose at least one successful answer you can assess yourself.
3. Enter a **Human quality score** using the scale below.
4. Type your observations into **Review notes**. Start with your alias and explain what worked, what was wrong, and why you chose that score.

| Score | Meaning |
| --- | --- |
| 1 | Incorrect or unusable |
| 2 | Major problems |
| 3 | Partly useful |
| 4 | Good, with minor issues |
| 5 | Correct, clear, and follows instructions |

Example of the format only — write your own assessment, do not copy this as evidence:

> dev-01 — Human review. The answer explains the main idea correctly and uses the requested language, but gives three sentences when I requested two. Score: 4/5.

Leave **Not reviewed** for languages you cannot judge. You can add “Language quality not assessed; I am not fluent in this language.” Notes without a score do not increase the **Human-reviewed** counter. For a failed request, record the error in notes; do not give an answer-quality score.

Write your own review. If you use AI assistance, label its contribution explicitly and keep it separate from your human judgment.

## 6. Export and check your report

1. Confirm your **Tester alias** is filled in and your review is saved in the result row.
2. In the **Results** heading, click **JSON**. The downloaded file is named `atlaslaunch-report.json`.
3. Rename it to `atlaslaunch-dev-01.json` or `atlaslaunch-dev-02.json`, matching your assigned alias.
4. Open it in a text editor. Check that `tester_alias` is correct, `results` contains your attempts, and your review note and score are present.
5. Check that the intended live results have `"mode": "live"`. If rows are fixtures, label the trial accordingly.
6. Inspect prompts and notes for sensitive information before sharing. Access tokens are excluded by the export, but anything you typed into a prompt or note is included.

You may also click **CSV** for an optional spreadsheet copy. Export **before** closing or refreshing the tab. This prototype cannot import a report to restore your session. Do not edit model responses, timings, or errors in the exported evidence.

## 7. Return these items to Paul

Send them through the private channel agreed before testing:

- Your renamed JSON report (if you reached the results stage).
- The completed feedback form below, saved as `feedback-dev-01.md` or `feedback-dev-02.md`.
- Optional screenshots or copied error text, with credentials removed.

If setup failed, return the form and error details anyway. State where you stopped; a blocked attempt is valid feedback. If you can reproduce a software bug, you may also use this repository's **Issues → New issue → Bug report** form. Check it for secrets before posting.

### Feedback form — copy and fill in

```text
Tester alias:
Date, time, and timezone:
OS and browser:
Programming experience:
Languages I can confidently review:
Local app (commit SHA) or hosted app:
Live trial, fixture-only trial, or blocked:
Setup start time:
First successful response time (or not reached):

Step 1 — Open app: completed / blocked / skipped
Step 2 — Connect: completed / blocked / skipped
Step 3 — Own prompt: completed / blocked / skipped
Step 4 — Four-case suite: completed / blocked / skipped
Step 5 — Human review: completed / blocked / skipped
Step 6 — Export: completed / blocked / skipped

Could I finish independently? What help did I need?
What did I try to use the model for?
Which answer(s) did I personally review?
What failed? Include steps to reproduce, expected result, actual result, and error text:
Did I retry any requests? Which ones and why?
Most confusing step:
Most useful feature:
Would I use AtlasLaunch for a project? Why or why not?
One improvement I would prioritize:
Export filename (or no export available):
Permission to quote my anonymized feedback in the submission: yes / no
```

When finished locally, return to the terminal and press **Ctrl+C** to stop the app.

## If live access is unavailable: fixture-only option

Use a separate fresh tab so fixture rows do not mix with an existing live trial. Select **Local fixture**. No endpoint key is needed. Choose **Success response** in the fixture scenario dropdown, then practice the playground, suite, notes, and export steps above. These are fixed software test responses, not N-ATLaS output.

Optionally choose **Authentication error** or **Timeout error** and run a prompt to check whether the error message is understandable. Report these as simulated errors. Use a filename such as `atlaslaunch-dev-01-fixture.json` and mark your feedback **fixture-only**. Do not present fixture scores as model-quality evidence.

## Optional code checks

Developers who also want to check the software can open a second terminal in the repository root and run:

```sh
npm test
npm run typecheck
npm run build
```

These checks require no endpoint key or GPU and use mocked inference. Record failures separately from live-model problems. Python checks are described in the [README](../README.md#checks); they are optional for this usability trial.

## Owner checklist — Paul

- Arrange repository or hosted-site access before asking a tester to begin.
- Confirm the endpoint is running and budget is available. A normal complete trial uses six model calls: one connection check, one prompt, and four suite cases; retries add calls.
- Share only the endpoint API key privately. The current endpoint has one shared application key, not independently revocable tester keys. Coordinate test windows and consider rotating that key afterward, updating your own client too.
- Collect each person's feedback independently. Do not fill in their form for them or present two aliases as two people.
- Keep original reports, including failed attempts. Ask permission before quoting feedback.
- Mark external testing complete only after actual reports are returned. Two trials provide early feedback, not broad validation or a language-accuracy guarantee.
