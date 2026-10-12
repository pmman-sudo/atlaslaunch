"""Build downloads from Git-tracked starter files only; run from a Git checkout."""
from pathlib import Path
import subprocess
import zipfile

root = Path(__file__).resolve().parent.parent
files = subprocess.check_output(["git", "ls-files", "--", "starter"], cwd=root, text=True).splitlines()
if not files:
    raise SystemExit("No tracked starter files. Run git add . before packaging.")
for name, prefix, folder in [("atlaslaunch-starter.zip", "starter/", "atlaslaunch-starter"), ("atlaslaunch-modal.zip", "starter/modal_host/", "atlaslaunch-modal")]:
    with zipfile.ZipFile(root / "public" / name, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename in files:
            if not filename.startswith(prefix):
                continue
            relative = Path(filename[len(prefix):])
            if any(part.startswith(".venv") or part in {"__pycache__", ".pytest_cache", ".git"} for part in relative.parts):
                continue
            if relative.name.startswith(".env") and relative.name != ".env.example":
                continue
            if relative.suffix in {".pyc", ".pem", ".key", ".safetensors", ".pt"} or relative.name == ".modal.toml":
                continue
            archive.write(root / filename, Path(folder) / relative)
    print("Packaged", name)
