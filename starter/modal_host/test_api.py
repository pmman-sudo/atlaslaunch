"""Contract/security tests with a fake model; no Modal account or GPU needed."""
from fastapi.testclient import TestClient
import pytest
from atlas_modal_api import create_api, MODEL_ID

KEY = "test-only-key-" * 4
BODY = {"model": MODEL_ID, "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 20, "temperature": 0, "stream": False}


@pytest.fixture
def gateway():
    calls = []
    async def infer(body):
        calls.append(body)
        return {"model": MODEL_ID, "choices": [{"message": {"role": "assistant", "content": "Hello"}}]}
    return TestClient(create_api(infer, KEY)), calls


def test_unauthorized_requests_do_not_start_gpu(gateway):
    client, calls = gateway
    for headers in ({}, {"Authorization": "Bearer wrong"}):
        assert client.post("/v1/chat/completions", json=BODY, headers=headers).status_code == 401
    assert calls == []


def test_valid_request_reaches_model_without_credentials(gateway):
    client, calls = gateway
    r = client.post("/v1/chat/completions", json=BODY, headers={"Authorization": "Bearer " + KEY})
    assert r.status_code == 200
    assert r.json()["model"] == MODEL_ID
    assert calls == [BODY]
    assert KEY not in r.text


@pytest.mark.parametrize("patch", [{"model": "another-model"}, {"max_tokens": 513},
    {"stream": True}, {"messages": []}, {"messages": [{"role": "user", "content": "x" * 6001}]}])
def test_invalid_requests_do_not_start_gpu(gateway, patch):
    client, calls = gateway
    assert client.post("/v1/chat/completions", json={**BODY, **patch},
                       headers={"Authorization": "Bearer " + KEY}).status_code == 422
    assert calls == []


def test_health_does_not_claim_gpu_is_ready(gateway):
    client, calls = gateway
    assert client.get("/health").status_code == 401
    r = client.get("/health", headers={"Authorization": "Bearer " + KEY})
    assert r.json()["gpu_readiness"] == "not checked"
    assert not calls


def test_upstream_errors_are_redacted():
    async def fail(body):
        raise RuntimeError("secret-private-debug-text")
    client = TestClient(create_api(fail, KEY))
    r = client.post("/v1/chat/completions", json=BODY, headers={"Authorization": "Bearer " + KEY})
    assert r.status_code == 503
    assert "secret-private-debug-text" not in r.text
