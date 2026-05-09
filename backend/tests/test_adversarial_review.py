from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import (
    AdversarialChallenge,
    Claim,
    Document,
    DocumentChunk,
    DocumentSet,
    RequirementSet,
    RiskFinding,
)
from app.schemas.review import CoverageSummary
from app.services.adversarial_review import AdversarialReviewService


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set())
    repository.add_document(document=_document(), chunks=[_chunk()])
    repository.replace_claim_ledger(document_set_id="ds_adversarial_demo", claims=_claims())
    repository.replace_risk_findings(
        document_set_id="ds_adversarial_demo",
        findings=[_primary_finding()],
    )
    repository.replace_coverage_summaries(
        document_set_id="ds_adversarial_demo",
        coverage_summaries=[
            CoverageSummary(
                agent_id="agent_regulatory_consistency",
                role="RegulatoryConsistencyReviewer",
                coverage_summary=(
                    "RegulatoryConsistencyReviewer reviewed 3 claims and generated "
                    "0 finding(s)."
                ),
                finding_count=0,
            )
        ],
    )


def test_adversarial_review_endpoint_adds_findings_to_risk_fusion() -> None:
    client = TestClient(app)

    response = client.post("/document-sets/ds_adversarial_demo/run-adversarial-review")

    assert response.status_code == 200
    payload = response.json()
    assert payload["additional_findings"]
    assert payload["new_findings"] == payload["additional_findings"]
    assert payload["escalation_reasons"]
    assert payload["risk_fusion_findings"]
    fused_ids = {finding["finding_id"] for finding in payload["risk_fusion_findings"]}
    assert "finding_primary_weak_clearance" in fused_ids
    assert all(
        finding["finding_id"] in fused_ids for finding in payload["additional_findings"]
    )
    assert all(
        finding["status"] == "needs_human_review"
        for finding in payload["additional_findings"]
    )
    assert repository.list_risk_fusion_findings("ds_adversarial_demo")


def test_adversarial_challenges_are_persisted_and_not_deleted() -> None:
    service = AdversarialReviewService(repository=repository, audit_log=audit_log)

    first_result = service.run_adversarial_review("ds_adversarial_demo")
    first_count = len(repository.list_adversarial_challenges("ds_adversarial_demo"))
    second_result = service.run_adversarial_review("ds_adversarial_demo")
    second_count = len(repository.list_adversarial_challenges("ds_adversarial_demo"))

    assert first_result.challenged_findings
    assert second_result.challenged_findings
    assert second_count >= first_count
    assert repository.list_adversarial_challenges("ds_adversarial_demo")


def test_false_no_issue_claim_is_challenged_and_routed_to_human_review() -> None:
    service = AdversarialReviewService(repository=repository, audit_log=audit_log)

    result = service.run_adversarial_review("ds_adversarial_demo")

    assert result.challenged_no_issue_claims
    challenge = result.challenged_no_issue_claims[0]
    assert challenge.human_review_required is True
    assert challenge.severity == "high"
    assert challenge.missing_evidence or challenge.evidence_items


def test_adversarial_review_flags_operator_error_root_cause_without_rationale() -> None:
    repository.replace_claim_ledger(
        document_set_id="ds_adversarial_demo",
        claims=[
            *_claims(),
            _claim(
                claim_id="claim_operator_error_root_cause",
                claim_type="root_cause",
                normalized_subject="root cause",
                normalized_object="operator error",
                quote="Root cause: operator error.",
            ),
        ],
    )
    service = AdversarialReviewService(repository=repository, audit_log=audit_log)

    result = service.run_adversarial_review("ds_adversarial_demo")

    assert any(
        finding.risk_category == "unsupported_root_cause"
        for finding in result.new_findings
    )
    assert any("operator error" in reason.lower() for reason in result.escalation_reasons)


def test_adversarial_review_escalates_low_document_quality() -> None:
    poor_document = _document().model_copy(
        update={"parsing_quality_score": 0.31, "parsing_status": "parsed"}
    )
    repository.add_document(document=poor_document, chunks=[_chunk()])
    service = AdversarialReviewService(repository=repository, audit_log=audit_log)

    result = service.run_adversarial_review("ds_adversarial_demo")

    assert any("document quality" in reason.lower() for reason in result.escalation_reasons)
    assert any("document quality" in question.lower() for question in result.unresolved_questions)


def test_adversarial_audit_event_references_primary_findings() -> None:
    service = AdversarialReviewService(repository=repository, audit_log=audit_log)

    service.run_adversarial_review("ds_adversarial_demo")

    event = audit_log.list_events()[-1]
    assert event.event_type == "adversarial_review_run"
    assert event.payload["primary_finding_ids"] == ["finding_primary_weak_clearance"]
    assert event.payload["challenge_count"] > 0


def test_adversarial_challenge_requires_rationale_and_evidence_or_gap() -> None:
    with pytest.raises(ValidationError):
        AdversarialChallenge(
            challenge_id="challenge_invalid",
            document_set_id="ds_adversarial_demo",
            target_type="finding",
            target_id="finding_primary_weak_clearance",
            agent_role="FalseClearanceChallenger",
            severity="medium",
            challenge_statement="Challenge without support must fail validation.",
            rationale="",
            evidence_items=[],
            missing_evidence=[],
            human_review_required=False,
            created_at=datetime.now(UTC),
        )


def _document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_adversarial_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_adversarial_demo_2026",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="change_control",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_adversarial_demo_2026",
        tenant_id="tenant_demo_pharma",
        name="Adversarial Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_visual_inspection_threshold_validation",
                "source_type": "internal_sop",
                "source_name": "SOP-CC-AVI-001",
                "source_version": "3.0",
                "section": "8.4",
                "requirement_text": (
                    "Automated visual inspection threshold changes require current "
                    "validation evidence and effectiveness verification."
                ),
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": [
                    "current validation addendum",
                    "effectiveness check",
                ],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )


def _document() -> Document:
    return Document(
        document_id="doc_adversarial_change",
        document_set_id="ds_adversarial_demo",
        filename="change-control.txt",
        file_hash_sha256=sha256(b"change-control.txt").hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri="local://adversarial/change-control.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=0.96,
        language="en",
        metadata={},
    )


def _chunk() -> DocumentChunk:
    text = (
        "Change control CC-2026-014 modifies the automated visual inspection "
        "rejection threshold. Impact assessment: possible false accept of defective "
        "container and missing current validation addendum for the new threshold."
    )
    return DocumentChunk(
        chunk_id="chunk_adversarial_change_p1",
        document_id="doc_adversarial_change",
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.96,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )


def _claims() -> list[Claim]:
    return [
        _claim(
            claim_id="claim_threshold_change",
            claim_type="deviation_description",
            normalized_subject="CC-2026-014",
            normalized_object="automated visual inspection rejection threshold changed",
            quote=(
                "Change control CC-2026-014 modifies the automated visual inspection "
                "rejection threshold."
            ),
        ),
        _claim(
            claim_id="claim_false_accept",
            claim_type="impact_assessment",
            normalized_subject="automated visual inspection threshold",
            normalized_object="possible false accept of defective container",
            quote="Impact assessment: possible false accept of defective container",
        ),
        _claim(
            claim_id="claim_missing_validation",
            claim_type="missing_or_unclear",
            normalized_subject="new threshold validation evidence",
            normalized_object="missing current validation addendum",
            quote="missing current validation addendum for the new threshold.",
        ),
    ]


def _claim(
    *,
    claim_id: str,
    claim_type: str,
    normalized_subject: str,
    normalized_object: str,
    quote: str,
) -> Claim:
    return Claim(
        claim_id=claim_id,
        document_id="doc_adversarial_change",
        chunk_id="chunk_adversarial_change_p1",
        page=1,
        claim_type=claim_type,
        normalized_subject=normalized_subject,
        normalized_predicate="states",
        normalized_object=normalized_object,
        raw_text_quote=quote,
        confidence=0.91,
        dependencies=[],
        created_by_model="mock-claim-extractor-v0.1",
        prompt_version="mock-claim-ledger-v0.1",
    )


def _primary_finding() -> RiskFinding:
    quote = "Impact assessment: possible false accept of defective container"
    return RiskFinding(
        finding_id="finding_primary_weak_clearance",
        document_set_id="ds_adversarial_demo",
        risk_category="visual_inspection_threshold",
        severity="high",
        likelihood=3,
        detectability=3,
        risk_statement=(
            "Primary review identifies possible false accept, but evidence remains weak."
        ),
        evidence_items=[
            {
                "document_id": "doc_adversarial_change",
                "chunk_id": "chunk_adversarial_change_p1",
                "page": 1,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": "supports",
                "verifier_score": 0.91,
            }
        ],
        requirement_references=["req_visual_inspection_threshold_validation"],
        missing_information=["current validation addendum", "effectiveness check"],
        model_provider="mock",
        model_name="mock-reviewer",
        model_version="0.1.0",
        prompt_version="primary-review-v0.1",
        evidence_support="weak",
        recommended_action="Do not auto-clear; route to SME/QA.",
        auto_close_allowed=False,
        status="needs_human_review",
    )
