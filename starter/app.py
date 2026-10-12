"""Local API. Bind to loopback; add authentication before public deployment."""
from typing import Literal
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from atlaslaunch import AtlasClient, AtlasError

load_dotenv()
app = FastAPI(title="AtlasLaunch", version="0.1.0", description="N-ATLAS inference adapter. /health checks this API, not the model.")

class Prompt(BaseModel):
    prompt: str = Field(min_length=1, max_length=6000)
    language: Literal["English", "Yoruba", "Hausa", "Igbo"] = "English"
    max_tokens: int = Field(default=192, ge=1, le=512)

@app.get("/health")
def health():
    return {"status": "ok", "service": "AtlasLaunch", "model_connection": "not_checked"}

@app.post("/generate")
def generate(body: Prompt):
    try:
        return AtlasClient.from_env().generate(body.prompt, body.language, body.max_tokens)
    except AtlasError as error:
        status = 400 if error.code.startswith("INVALID_") and error.code != "INVALID_RESPONSE" else 502
        return JSONResponse({"code": error.code, "error": str(error)}, status_code=status, headers={"Cache-Control": "no-store"})

@app.post("/check")
def check():
    return generate(Prompt(prompt="Reply with the word ready.", max_tokens=8))
