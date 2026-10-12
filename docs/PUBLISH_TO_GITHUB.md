# Publish this prepared repository

Suggested repository name: **atlaslaunch**.
Description: **Developer workbench for N-ATLaS: live multilingual prompts, repeatable tests, review notes, exports, and Modal deployment.**

Start private while preparing tester access and deciding the application's license. This ZIP includes a GitHub-ready source tree, not an already-created remote repository. It excludes Git history and deployment credentials.

1. Extract the ZIP. Open PowerShell in the `atlaslaunch` folder containing `package.json` and `README.md`.
2. On GitHub, create an empty repository named `atlaslaunch` under the intended account. Do not initialize a second README, .gitignore, or license.
3. For the previously identified `pmman-sudo` account, run:

```powershell
git init -b main
git add .
git status --short
git commit -m "Prepare AtlasLaunch workbench and Modal deployment"
git remote add origin https://github.com/pmman-sudo/atlaslaunch.git
git push -u origin main
```

Use a different remote URL if you choose another owner or name. Authenticate through Git's browser flow if prompted; never place a personal access token in the remote URL. If Git requests a commit identity, configure your chosen name and GitHub-associated email before committing.

Review staged paths before pushing. No `.env`, virtual environment, model weights, or `.modal.toml` should be staged. A failing push is not a successful publication; inspect the error before retrying. If the remote already has commits, do not force-push over them.

After upload, check the **Actions** tab for the web and Python jobs. The workflow tests/builds only; it does not deploy or spend GPU credits. Invite the two developers as repository collaborators if they need private source access. Website access is a separate setting.

Official guide: https://docs.github.com/en/repositories/creating-and-managing-repositories/adding-locally-hosted-code-to-github
