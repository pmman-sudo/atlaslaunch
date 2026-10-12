import json
import httpx
import pytest
from fastapi.testclient import TestClient
from atlaslaunch import AtlasClient, AtlasError
from app import app

ENDPOINT = "https://unit-test.example/v1/chat/completions"

def make_client(status=200, data=None, protocol="openai", callback=None):
    def handler(request):
        if callback:
            callback(request)
        return httpx.Response(status, json=data)
    return AtlasClient(ENDPOINT, token="test-secret", protocol=protocol, transport=httpx.MockTransport(handler))

def test_chat_response_and_payload():
    def inspect(request):
        body = json.loads(request.content)
        assert request.headers["Authorization"] == "Bearer test-secret"
        assert body["model"] == "NCAIR1/N-ATLaS"
        assert "Hausa" in body["messages"][0]["content"]
        assert body["stream"] is False
    result = make_client(data={"choices": [{"message": {"content": "sannu"}}], "model": "NCAIR1/N-ATLaS", "usage": {"total_tokens": 5}}, callback=inspect).generate("Say hello", "Hausa")
    assert result["text"] == "sannu"
    assert result["mode"] == "live"  # Mock transport exercises the live adapter, not a live model.
    assert "test-secret" not in json.dumps(result)

def test_tgi_prompt_format():
    def inspect(request):
        body = json.loads(request.content)
        assert body["inputs"].startswith("<|begin_of_text|>")
        assert body["parameters"]["return_full_text"] is False
    assert make_client(data={"generated_text": "hello"}, protocol="tgi", callback=inspect).generate("Hello")["text"] == "hello"

@pytest.mark.parametrize("status,code", [(401,"AUTHENTICATION_FAILED"),(403,"ACCESS_DENIED"),(404,"ENDPOINT_NOT_FOUND"),(429,"RATE_LIMITED"),(503,"MODEL_UNAVAILABLE"),(302,"UPSTREAM_ERROR")])
def test_actionable_errors_and_no_secret_echo(status, code):
    with pytest.raises(AtlasError) as caught:
        make_client(status, {"error": "test-secret"}).generate("Hello")
    assert caught.value.code == code
    assert "test-secret" not in str(caught.value)

@pytest.mark.parametrize("data", [{}, {"choices": []}, {"generated_text": ""}, None])
def test_invalid_response_is_not_success(data):
    with pytest.raises(AtlasError) as caught:
        make_client(data=data).generate("Hello")
    assert caught.value.code == "INVALID_RESPONSE"

def test_timeout():
    def fail(request):
        raise httpx.ReadTimeout("upstream secret", request=request)
    client = AtlasClient(ENDPOINT, transport=httpx.MockTransport(fail))
    with pytest.raises(AtlasError) as caught:
        client.generate("Hello")
    assert caught.value.code == "TIMEOUT"

def test_remote_http_rejected():
    with pytest.raises(AtlasError):
        AtlasClient("http://remote.example/generate")

def test_health_does_not_claim_model_is_connected():
    result = TestClient(app).get("/health")
    assert result.json()["model_connection"] == "not_checked"

def test_api_missing_config(monkeypatch):
    monkeypatch.setenv("NATLAS_ENDPOINT", "")
    response = TestClient(app).post("/generate", json={"prompt":"hello"})
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_ENDPOINT"

def test_invalid_language_rejected():
    response = TestClient(app).post("/generate", json={"prompt":"hello", "language":"French"})
    assert response.status_code == 422
