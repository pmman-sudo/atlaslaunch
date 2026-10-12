"""Small authenticated chat API; does not import GPU dependencies."""
import secrets
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

MODEL_ID = "NCAIR1/N-ATLaS"
MODEL_REVISION = "e294476928aca9030e924ca27bb8e085e8581273"


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=6000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: Literal["NCAIR1/N-ATLaS"] = MODEL_ID
    messages: list[Message] = Field(min_length=1, max_length=10)
    max_tokens: int = Field(default=192, ge=1, le=512, strict=True)
    temperature: float = Field(default=0.1, ge=0, le=2)
    stream: Literal[False] = False

    @model_validator(mode="after")
    def bounded_conversation(self):
        if sum(len(m.content) for m in self.messages) > 8000:
            raise ValueError("Conversation exceeds 8000 characters")
        if self.messages[-1].role != "user":
            raise ValueError("Last message must be from the user")
        return self


def create_api(infer, api_key: str):
    if len(api_key) < 32:
        raise ValueError("ATLAS_API_KEY must contain at least 32 characters")
    api = FastAPI(title="AtlasLaunch N-ATLAS", docs_url=None, redoc_url=None)

    def authenticate(authorization):
        expected = f"Bearer {api_key}".encode()
        if not secrets.compare_digest((authorization or "").encode(), expected):
            raise HTTPException(401, "Invalid API key")

    @api.get("/health")
    async def health(authorization: str | None = Header(default=None)):
        authenticate(authorization)
        return {"status": "gateway-ready", "model": MODEL_ID,
                "revision": MODEL_REVISION, "gpu_readiness": "not checked"}

    @api.post("/v1/chat/completions")
    async def chat(body: ChatRequest, authorization: str | None = Header(default=None)):
        authenticate(authorization)
        # Authentication and input checks happen before any GPU invocation.
        try:
            result = await infer(body.model_dump())
        except Exception:
            raise HTTPException(503, "Model unavailable. Inspect Modal logs; retry after warm-up.") from None
        if result.get("error") == "context_limit":
            raise HTTPException(400, "Prompt exceeds the 2048-token input limit")
        return result

    return api
