from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.core.config import get_settings
from app.main import app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "Pharma AI Risk Orchestration Backend"
    assert body["app_version"] == "0.1.0"
    assert body["environment"] == "local"
    assert body["model_roles"]["stack"] == "cloud"
    assert body["model_roles"]["requirement_assessor"] == "anthropic"
    assert body["model_roles"]["entailment_checker"] == "openai"


def test_health_reports_the_local_stack(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("QRM_MODEL_STACK", "local")
    get_settings.cache_clear()
    try:
        response = TestClient(app).get("/health")
    finally:
        get_settings.cache_clear()

    roles = response.json()["model_roles"]
    assert roles == {
        "stack": "local",
        "finding_reviewers": "hetzner",
        "requirement_assessor": "hetzner",
        "requirement_assessor_mode": "narrow",
        "entailment_checker": "hetzner",
        "critics": "hetzner",
    }
