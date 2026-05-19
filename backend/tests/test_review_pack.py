from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

import pytest
from fastapi.testclient import TestClient

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import (
    AdversarialChallenge,
    Document,
    DocumentChunk,
    DocumentSet,
    FindingVerificationResult,
    RequirementSet,
    RiskFinding,
)
from app.schemas.review import CoverageSummary
from app.services.review_pack import ReviewPackService
from app.services.risk_fusion import RiskFusionService


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()
    _setup_review_pack_context()


def test_review_pack_is_deterministic_from_latest_risk_decision() -> None:
    risk_decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_review_pack_demo"
    )
    service = ReviewPackService(repository=repository, audit_log=audit_log)

    first_pack = service.get_review_pack("ds_review_pack_demo")
    second_pack = service.get_review_pack("ds_review_pack_demo")

    assert first_pack.review_pack_id == second_pack.review_pack_id
    assert first_pack.decision == risk_decision
    assert first_pack.summary == second_pack.summary
    assert first_pack.review_progress_percent == 0
    assert first_pack.reviewed_finding_count == 0
    assert first_pack.total_finding_count == 1
    assert first_pack.top_risks[0].finding_id == "finding_pack_high"
    assert first_pack.top_risks[0].risk_statement == (
        "Threshold change may allow false accept of defective containers."
    )
    assert first_pack.top_risks[0].severity == "high"
    assert first_pack.top_risks[0].requirement_references == [
        "req_pack_threshold_validation"
    ]


def test_review_pack_contains_evidence_model_positions_and_verifier_status() -> None:
    RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_review_pack_demo"
    )

    pack = ReviewPackService(repository=repository, audit_log=audit_log).get_review_pack(
        "ds_review_pack_demo"
    )

    assert pack.evidence_table[0].page == 1
    assert pack.evidence_table[0].chunk_id == "chunk_pack_change_p1"
    assert "false accept of defective containers" in pack.evidence_table[0].quote
    assert pack.top_risks[0].found_by_agents == ["primary-reviewer"]
    assert pack.top_risks[0].contradicted_by_agents == ["FalseClearanceChallenger"]
    assert pack.top_risks[0].no_issue_agents == ["RegulatoryConsistencyReviewer"]
    assert pack.top_risks[0].verifier_status == "weak"
    assert "human review" in pack.top_risks[0].human_review_reason.lower()
    assert pack.top_risks[0].review_status == "open"
    assert pack.top_risks[0].review_decision_count == 0
    assert pack.top_risks[0].latest_review_decision is None
    assert pack.verifier_results[0].finding_id == "finding_pack_high"


def test_review_pack_includes_reviewer_actions_and_audit_references() -> None:
    RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_review_pack_demo"
    )

    pack = ReviewPackService(repository=repository, audit_log=audit_log).get_review_pack(
        "ds_review_pack_demo"
    )

    actions = {action.action for action in pack.recommended_reviewer_actions}
    assert actions >= {
        "confirm",
        "downgrade",
        "reject_false_positive",
        "request_more_information",
        "escalate_to_qa",
    }
    assert "current validation addendum" in pack.missing_information
    assert any(reference.startswith("audit_") for reference in pack.audit_references)


def test_review_pack_endpoint_returns_compact_dossier() -> None:
    RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_review_pack_demo"
    )
    client = TestClient(app)

    response = client.get("/document-sets/ds_review_pack_demo/review-pack")

    assert response.status_code == 200
    payload = response.json()
    assert payload["document_set_id"] == "ds_review_pack_demo"
    assert payload["top_risks"][0]["evidence_quotes"][0]["chunk_id"] == "chunk_pack_change_p1"
    assert payload["model_positions"][0]["finding_id"] == "finding_pack_high"


def test_review_decision_endpoint_persists_decision_and_writes_audit_event() -> None:
    client = TestClient(app)

    response = client.post(
        "/findings/finding_pack_high/review-decision",
        json={
            "reviewer_id": "reviewer_qa_1",
            "decision": "request_more_information",
            "rationale": "Validation addendum is required before QA disposition.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["finding_id"] == "finding_pack_high"
    assert payload["decision"] == "request_more_information"
    assert repository.list_review_decisions("finding_pack_high")[0].review_id.startswith(
        "review_"
    )
    event = audit_log.list_events()[-1]
    assert event.event_type == "review_decision_recorded"
    assert event.payload["finding_id"] == "finding_pack_high"
    assert event.payload["decision"] == "request_more_information"


def test_review_pack_progress_reflects_human_review_decisions() -> None:
    RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_review_pack_demo"
    )
    client = TestClient(app)

    response = client.post(
        "/findings/finding_pack_high/review-decision",
        json={
            "reviewer_id": "reviewer_qa_1",
            "decision": "downgrade",
            "rationale": "Reviewer confirmed lower impact after checking the source.",
        },
    )

    assert response.status_code == 200
    pack = ReviewPackService(repository=repository, audit_log=audit_log).get_review_pack(
        "ds_review_pack_demo"
    )
    assert pack.review_progress_percent == 100
    assert pack.reviewed_finding_count == 1
    assert pack.total_finding_count == 1
    assert pack.top_risks[0].review_status == "reviewed"
    assert pack.top_risks[0].review_decision_count == 1
    assert pack.top_risks[0].latest_review_decision == "downgrade"
    assert pack.top_risks[0].latest_reviewed_at is not None


def _setup_review_pack_context() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set())
    repository.add_document(document=_document(), chunks=[_chunk()])
    repository.replace_risk_findings(
        document_set_id="ds_review_pack_demo",
        findings=[_finding()],
    )
    repository.replace_coverage_summaries(
        document_set_id="ds_review_pack_demo",
        coverage_summaries=[
            CoverageSummary(
                agent_id="agent_regulatory_consistency",
                role="RegulatoryConsistencyReviewer",
                coverage_summary="RegulatoryConsistencyReviewer generated 0 finding(s).",
                finding_count=0,
            )
        ],
    )
    repository.append_adversarial_challenges(
        document_set_id="ds_review_pack_demo",
        challenges=[_challenge()],
    )


def _document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_review_pack_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_review_pack_demo_2026",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="change_control",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_review_pack_demo_2026",
        tenant_id="tenant_demo_pharma",
        name="Review Pack Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_pack_threshold_validation",
                "source_type": "internal_sop",
                "source_name": "SOP-CC-AVI-001",
                "source_version": "3.0",
                "section": "8.4",
                "requirement_text": (
                    "Automated visual inspection threshold changes require current "
                    "validation evidence."
                ),
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["current validation addendum"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )


def _document() -> Document:
    return Document(
        document_id="doc_pack_change",
        document_set_id="ds_review_pack_demo",
        filename="change-control.txt",
        file_hash_sha256=sha256(b"change-control.txt").hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri="local://review-pack/change-control.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=0.95,
        language="en",
        metadata={},
    )


def _chunk() -> DocumentChunk:
    text = (
        "Change control CC-2026-014 modifies the AVI threshold. "
        "Impact assessment notes possible false accept of defective containers."
    )
    return DocumentChunk(
        chunk_id="chunk_pack_change_p1",
        document_id="doc_pack_change",
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )


def _finding() -> RiskFinding:
    quote = "Impact assessment notes possible false accept of defective containers."
    return RiskFinding(
        finding_id="finding_pack_high",
        document_set_id="ds_review_pack_demo",
        risk_category="visual_inspection",
        severity="high",
        likelihood=3,
        detectability=3,
        risk_statement="Threshold change may allow false accept of defective containers.",
        evidence_items=[
            {
                "document_id": "doc_pack_change",
                "chunk_id": "chunk_pack_change_p1",
                "page": 1,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": "supports",
                "verifier_score": 0.95,
            }
        ],
        requirement_references=["req_pack_threshold_validation"],
        missing_information=["current validation addendum"],
        model_provider="mock",
        model_name="primary-reviewer",
        model_version="0.1.0",
        prompt_version="test-review-v0.1",
        evidence_support="weak",
        recommended_action="Route to QA reviewer.",
        auto_close_allowed=False,
        status="needs_human_review",
        verification_result=FindingVerificationResult(
            finding_id="finding_pack_high",
            evidence_support="weak",
            quote_exists=True,
            quote_matches_chunk=True,
            requirement_applicable=True,
            unsupported_claims=[],
            missing_evidence=["current validation addendum"],
            verifier_rationale="Quote exists, but current validation evidence is missing.",
            verifier_model_run_id=None,
            deterministic_checks_passed=False,
        ),
    )


def _challenge() -> AdversarialChallenge:
    quote = "Impact assessment notes possible false accept of defective containers."
    return AdversarialChallenge(
        challenge_id="challenge_pack_false_clearance",
        document_set_id="ds_review_pack_demo",
        target_type="finding",
        target_id="finding_pack_high",
        agent_role="FalseClearanceChallenger",
        severity="high",
        challenge_statement="High-risk false accept cannot be cleared with weak evidence.",
        rationale="Validation addendum is not linked.",
        evidence_items=[
            {
                "document_id": "doc_pack_change",
                "chunk_id": "chunk_pack_change_p1",
                "page": 1,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": "contextual",
                "verifier_score": 0.95,
            }
        ],
        missing_evidence=["current validation addendum"],
        human_review_required=True,
        created_at=datetime.now(UTC),
    )
