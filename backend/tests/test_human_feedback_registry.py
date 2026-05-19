from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

import pytest
from fastapi.testclient import TestClient

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import (
    Document,
    DocumentChunk,
    DocumentSet,
    RequirementSet,
    ReviewDecision,
    RiskFinding,
)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()
    _setup_feedback_context()


def test_human_feedback_registry_returns_model_performance_datapoints() -> None:
    repository.add_review_decision(
        ReviewDecision(
            review_id="review_feedback_downgrade",
            finding_id="finding_feedback_high",
            reviewer_id="reviewer_qa_1",
            decision="downgrade",
            rationale="Severity is overstated after source review.",
            created_at=datetime.now(UTC),
        )
    )

    response = TestClient(app).get("/analytics/human-feedback")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_feedback_records"] == 1
    assert payload["records"][0] == {
        "feedback_id": "hfb_review_feedback_downgrade",
        "review_id": "review_feedback_downgrade",
        "document_set_id": "ds_feedback_demo",
        "finding_id": "finding_feedback_high",
        "tenant_id": "tenant_demo_pharma",
        "document_type": "change_control",
        "process_area": "aseptic_filling",
        "agent_role": "RegulatoryConsistencyReviewer",
        "model_provider": "openai",
        "model_name": "gpt-4o-mini",
        "model_version": "2026-05-13",
        "prompt_version": "reg-consistency-v1",
        "requirement_references": ["req_feedback_validation"],
        "risk_category": "validation_gap",
        "original_severity": "high",
        "original_evidence_support": "weak",
        "verifier_evidence_support": None,
        "human_decision": "downgrade",
        "feedback_outcome": "severity_overstated",
        "reviewer_id": "reviewer_qa_1",
        "rationale": "Severity is overstated after source review.",
        "created_at": payload["records"][0]["created_at"],
        "high_critical_recall_guard": True,
    }
    assert payload["model_cards"][0]["model_name"] == "gpt-4o-mini"
    assert payload["model_cards"][0]["agent_role"] == "RegulatoryConsistencyReviewer"
    assert payload["model_cards"][0]["total_human_decisions"] == 1
    assert payload["model_cards"][0]["downgrade_count"] == 1
    assert payload["model_cards"][0]["false_positive_count"] == 0
    assert payload["model_cards"][0]["severity_issue_count"] == 1
    assert payload["model_cards"][0]["evidence_issue_count"] == 0
    assert payload["model_cards"][0]["requirement_issue_count"] == 0
    assert payload["model_cards"][0]["missed_finding_count"] == 0
    assert payload["model_cards"][0]["downgrade_rate"] == 1.0


def test_human_feedback_registry_captures_reviewer_calibration_categories() -> None:
    decisions = [
        (
            "review_feedback_evidence_wrong",
            "evidence_incorrect",
            "The cited passage does not support the finding.",
        ),
        (
            "review_feedback_requirement_wrong",
            "requirement_incorrect",
            "The linked requirement is not applicable.",
        ),
        (
            "review_feedback_missed_finding",
            "missed_finding",
            "Reviewer found an additional missing batch-impact risk.",
        ),
    ]
    for review_id, decision, rationale in decisions:
        repository.add_review_decision(
            ReviewDecision(
                review_id=review_id,
                finding_id="finding_feedback_high",
                reviewer_id="reviewer_qa_1",
                decision=decision,
                rationale=rationale,
                created_at=datetime.now(UTC),
            )
        )

    response = TestClient(app).get("/analytics/human-feedback")

    assert response.status_code == 200
    payload = response.json()
    assert {
        record["feedback_outcome"]
        for record in payload["records"]
    } == {"evidence_issue", "requirement_issue", "missed_finding"}
    assert payload["model_cards"][0]["evidence_issue_count"] == 1
    assert payload["model_cards"][0]["requirement_issue_count"] == 1
    assert payload["model_cards"][0]["missed_finding_count"] == 1


def _setup_feedback_context() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set())
    repository.add_document(document=_document(), chunks=[_chunk()])
    repository.replace_risk_findings(
        document_set_id="ds_feedback_demo",
        findings=[_finding()],
    )
    audit_log.append(
        event_type="finding_created",
        actor_id="model_gpt-4o-mini",
        actor_type="model",
        entity_type="RiskFinding",
        entity_id="finding_feedback_high",
        payload={
            "document_set_id": "ds_feedback_demo",
            "agent_role": "RegulatoryConsistencyReviewer",
            "prompt_version": "reg-consistency-v1",
        },
    )


def _document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_feedback_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_feedback_demo_2026",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="change_control",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="needs_human_review",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_feedback_demo_2026",
        tenant_id="tenant_demo_pharma",
        name="Feedback Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_feedback_validation",
                "source_type": "internal_sop",
                "source_name": "SOP-VAL-001",
                "source_version": "1.0",
                "section": "5.1",
                "requirement_text": "Validation impact must be justified.",
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["validation rationale"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )


def _document() -> Document:
    return Document(
        document_id="doc_feedback_change",
        document_set_id="ds_feedback_demo",
        filename="change-control.txt",
        file_hash_sha256=sha256(b"feedback-change").hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri="local://feedback/change-control.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=0.95,
        language="en",
        metadata={},
    )


def _chunk() -> DocumentChunk:
    text = "Change control states no validation impact."
    return DocumentChunk(
        chunk_id="chunk_feedback_change_p1",
        document_id="doc_feedback_change",
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )


def _finding() -> RiskFinding:
    quote = "Change control states no validation impact."
    return RiskFinding(
        finding_id="finding_feedback_high",
        document_set_id="ds_feedback_demo",
        risk_category="validation_gap",
        severity="high",
        likelihood=3,
        detectability=3,
        risk_statement="Validation impact rationale may be incomplete.",
        evidence_items=[
            {
                "document_id": "doc_feedback_change",
                "chunk_id": "chunk_feedback_change_p1",
                "page": 1,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": "supports",
                "verifier_score": 0.9,
            }
        ],
        requirement_references=["req_feedback_validation"],
        missing_information=["validation rationale"],
        model_provider="openai",
        model_name="gpt-4o-mini",
        model_version="2026-05-13",
        prompt_version="reg-consistency-v1",
        evidence_support="weak",
        recommended_action="Route to QA.",
        auto_close_allowed=False,
        status="needs_human_review",
        verification_result=None,
    )
