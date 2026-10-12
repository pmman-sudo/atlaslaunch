"""Run locally after Modal setup. Never saves credentials to this project."""
from getpass import getpass
import secrets
import modal

hf_token = getpass("Hugging Face token (hidden): ").strip()
if not hf_token.startswith("hf_"):
    raise SystemExit("Expected a Hugging Face token beginning with hf_.")
api_key = secrets.token_urlsafe(36)
modal.Secret.objects.create("atlaslaunch-secrets", {
    "HF_TOKEN": hf_token,
    "ATLAS_API_KEY": api_key,
})
print("Secret created in your Modal workspace.")
print("Save this AtlasLaunch API key in your password manager. Do not post it in chat:")
print(api_key)
print("Use this new key in AtlasLaunch's Access token field, not your Hugging Face token.")
