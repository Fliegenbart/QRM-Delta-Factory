from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

import pytest

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.schemas.domain import Document, DocumentChunk, DocumentSet, RequirementSet, RiskFinding
from app.verifiers.evidence import EvidenceVerifierService


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set())
    repository.add_document(document=_document(), chunks=[_chunk()])


def test_valid_quote_and_requirement_produce_strong_verification_result() -> None:
    finding = _finding()
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.finding_id == finding.finding_id
    assert result.evidence_support == "strong"
    assert result.quote_exists is True
    assert result.quote_matches_chunk is True
    assert result.requirement_applicable is True
    assert result.deterministic_checks_passed is True
    assert result.unsupported_claims == []
    assert result.missing_evidence == []


def test_wrong_quote_is_not_silently_accepted() -> None:
    finding = _finding(
        quote="Impact assessment: no product impact identified.",
        risk_statement="Unsupported claim should not be accepted.",
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.quote_exists is False
    assert result.quote_matches_chunk is False
    assert result.evidence_support == "none"
    assert result.deterministic_checks_passed is False
    assert result.unsupported_claims


def test_quote_that_does_not_support_the_risk_statement_is_evidence_support_none() -> None:
    finding = _finding(
        quote="Impact assessment: possible false accept of defective container.",
        risk_statement="QA approval is documented and batch release is closed.",
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.quote_exists is True
    assert result.quote_matches_chunk is True
    assert result.requirement_applicable is True
    assert result.evidence_support == "none"
    assert result.deterministic_checks_passed is False
    assert any("risk statement" in item.lower() for item in result.unsupported_claims)


def test_partial_evidence_that_only_supports_part_of_statement_is_partial() -> None:
    finding = _finding(
        quote="Impact assessment: possible false accept of defective container.",
        risk_statement=(
            "Impact assessment identifies possible false accept risk, but QA approval is "
            "documented."
        ),
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.quote_exists is True
    assert result.quote_matches_chunk is True
    assert result.evidence_support == "partial"
    assert result.deterministic_checks_passed is False
    assert any("risk statement" in item.lower() for item in result.unsupported_claims)


def test_wrong_requirement_is_marked_not_applicable() -> None:
    finding = _finding(requirement_references=["req_not_applicable_to_deviation"])
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.requirement_applicable is False
    assert result.deterministic_checks_passed is False
    assert result.evidence_support == "weak"
    assert "not applicable" in result.verifier_rationale.lower()


def test_wrong_page_fails_deterministic_checks() -> None:
    finding = _finding(page=5)
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.quote_matches_chunk is True
    assert result.deterministic_checks_passed is False
    assert any("page" in item.lower() for item in result.missing_evidence)


def test_verification_result_is_attached_and_audited() -> None:
    finding = _finding()
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    verified_findings = service.verify_findings("ds_verifier_demo", [finding])

    assert verified_findings[0].verification_result is not None
    assert verified_findings[0].verification_result.evidence_support == "strong"
    assert repository.list_risk_findings("ds_verifier_demo")[0].verification_result is not None
    event = audit_log.list_events()[-1]
    assert event.event_type == "evidence_verifier_run"
    assert event.payload["finding_count"] == 1
    assert event.payload["strong_count"] == 1


def test_missing_document_is_stored_as_unverified_not_deleted() -> None:
    finding = _finding(document_id="doc_missing")
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    verified_findings = service.verify_findings("ds_verifier_demo", [finding])

    assert len(verified_findings) == 1
    result = verified_findings[0].verification_result
    assert result is not None
    assert result.quote_exists is False
    assert result.evidence_support == "none"
    assert repository.list_risk_findings("ds_verifier_demo")[0].finding_id == finding.finding_id


def _document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_verifier_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_verifier_demo_2026",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="deviation",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_verifier_demo_2026",
        tenant_id="tenant_demo_pharma",
        name="Verifier Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_deviation_documented_impact_assessment",
                "source_type": "internal_sop",
                "source_name": "SOP-DEV-001",
                "source_version": "4.2",
                "section": "6.3",
                "requirement_text": "Deviation records need documented product impact assessment.",
                "applies_to_document_types": ["deviation"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["deviation record", "impact assessment"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_not_applicable_to_deviation",
                "source_type": "internal_sop",
                "source_name": "SOP-CAPA-001",
                "source_version": "1.0",
                "section": "2.0",
                "requirement_text": "CAPA-only requirement.",
                "applies_to_document_types": ["capa"],
                "applies_to_process_areas": ["packaging"],
                "criticality": "medium",
                "required_evidence": ["CAPA record"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
        ],
    )


def _document() -> Document:
    return Document(
        document_id="doc_verifier_deviation",
        document_set_id="ds_verifier_demo",
        filename="deviation.txt",
        file_hash_sha256=sha256(b"deviation.txt").hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri="local://verifier/deviation.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=0.95,
        language="en",
        metadata={},
    )


def _chunk() -> DocumentChunk:
    text = (
        "Deviation DEV-2026-014 for Batch BATCH-001. "
        "Impact assessment: possible false accept of defective container."
    )
    return DocumentChunk(
        chunk_id="chunk_verifier_deviation_p1",
        document_id="doc_verifier_deviation",
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )


def _finding(
    *,
    quote: str = "Impact assessment: possible false accept of defective container.",
    risk_statement: str = "Deviation impact assessment indicates possible false accept risk.",
    document_id: str = "doc_verifier_deviation",
    page: int = 1,
    requirement_references: list[str] | None = None,
) -> RiskFinding:
    return RiskFinding(
        finding_id="finding_verifier_demo",
        document_set_id="ds_verifier_demo",
        risk_category="deviation_management",
        severity="high",
        likelihood=3,
        detectability=3,
        risk_statement=risk_statement,
        evidence_items=[
            {
                "document_id": document_id,
                "chunk_id": "chunk_verifier_deviation_p1",
                "page": page,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": "supports",
                "verifier_score": 0.9,
            }
        ],
        requirement_references=requirement_references
        or ["req_deviation_documented_impact_assessment"],
        missing_information=[],
        model_provider="mock",
        model_name="mock-reviewer",
        model_version="0.1.0",
        prompt_version="deviation_reviewer_v1",
        evidence_support="partial",
        recommended_action="Route to QA/SME for review.",
        auto_close_allowed=False,
        status="needs_human_review",
    )
