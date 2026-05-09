from __future__ import annotations

from fastapi.testclient import TestClient

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.main import app


def test_demo_seed_creates_reviewable_document_set_and_review_pack() -> None:
    repository.reset()
    audit_log.clear()
    client = TestClient(app)

    seed_response = client.post("/demo/seed")

    assert seed_response.status_code == 201
    payload = seed_response.json()
    assert payload["document_set"]["document_set_id"] == "ds_demo_avi_threshold"
    assert payload["pipeline_run"]["document_set_id"] == "ds_demo_avi_threshold"
    assert payload["review_pack"]["document_set_id"] == "ds_demo_avi_threshold"
    assert payload["review_pack"]["top_risks"]
    assert "finding" in payload["review_pack"]["top_risks"][0]["finding_id"]

    list_response = client.get("/document-sets")
    assert list_response.status_code == 200
    assert [item["document_set_id"] for item in list_response.json()] == [
        "ds_demo_avi_threshold"
    ]

    pack_response = client.get("/document-sets/ds_demo_avi_threshold/review-pack")
    assert pack_response.status_code == 200
    assert pack_response.json()["top_risks"]


def test_demo_seed_is_idempotent_for_the_same_demo_dataset() -> None:
    repository.reset()
    audit_log.clear()
    client = TestClient(app)

    first = client.post("/demo/seed")
    second = client.post("/demo/seed")

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["created"] is False
    assert len(repository.list_document_sets()) == 1
