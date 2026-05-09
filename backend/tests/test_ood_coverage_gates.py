from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

import pytest

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.risk.gates import CoverageService, OODService, required_reviewer_roles_for_scope
from app.schemas.domain import Claim, Document, DocumentChunk, DocumentSet, RequirementSet
from app.schemas.review import CoverageSummary
from app.services.review_pack import ReviewPackService
from app.services.risk_fusion import RiskFusionService


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()


def _claim(
    claim_id: str,
    *,
    claim_type: str = "impact_assessment",
) -> Claim:
    quote = "Change control CC-2026-014 modifies the AVI threshold."
    return Claim(
        claim_id=claim_id,
        document_id="doc_gate_change",
        chunk_id="chunk_gate_change_p1",
        page=1,
        claim_type=claim_type,
        normalized_subject="CC-2026-014",
        normalized_predicate="modifies",
        normalized_object="AVI threshold",
        raw_text_quote=quote,
        confidence=0.9,
        dependencies=[],
        created_by_model="mock-claim-extractor",
        prompt_version="mock-claim-extractor-v0.1",
    )


@pytest.mark.parametrize(
    ("setup_kwargs", "expected_reason"),
    [
        (
            {"document_type": "supplier_certificate"},
            "unknown document type: supplier_certificate",
        ),
        ({"process_area": "warehouse"}, "unknown process area: warehouse"),
        ({"language": "de"}, "unsupported language: de"),
        ({"parsing_quality": 0.2}, "document parsing quality below threshold"),
        (
            {"document_metadata": {"missing_required_documents": ["validation report"]}},
            "missing required document: validation report",
        ),
        ({"claims": []}, "unusually few claims"),
        (
            {
                "claims": [
                    _claim("claim_unclear_a", claim_type="missing_or_unclear"),
                    _claim("claim_unclear_b", claim_type="missing_or_unclear"),
                    _claim("claim_impact_a"),
                ]
            },
            "unusually many unclear claims",
        ),
        (
            {"document_type": "unknown_type", "process_area": "unknown_area"},
            "no matching requirements found",
        ),
        (
            {
                "document_type": "deviation",
                "failed_reviewer_role": "DeviationReviewer",
            },
            "relevant reviewer role failed: DeviationReviewer",
        ),
    ],
)
def test_ood_service_scores_all_required_signals(
    setup_kwargs: dict[str, object],
    expected_reason: str,
) -> None:
    _setup_gate_context(**setup_kwargs)

    result = OODService(repository=repository, audit_log=audit_log).evaluate("ds_gate_demo")

    assert result.score > 0
    assert expected_reason in result.reasons


def test_coverage_service_reports_missing_required_roles_and_requirement_coverage() -> None:
    _setup_gate_context()
    repository.replace_coverage_summaries(
        document_set_id="ds_gate_demo",
        coverage_summaries=[
            CoverageSummary(
                agent_id="agent_gmp_data_integrity",
                role="GMPDataIntegrityReviewer",
                coverage_summary="GMPDataIntegrityReviewer completed review.",
                finding_count=0,
            )
        ],
    )

    result = CoverageService(repository=repository, audit_log=audit_log).evaluate(
        "ds_gate_demo"
    )

    assert "GMPDataIntegrityReviewer" in result.completed_roles
    assert "BatchImpactReviewer" in result.missing_roles
    assert result.requirement_coverage_sufficient is True
    assert result.high_or_critical_coverage_gap is True
    assert any("missing required reviewer role" in reason for reason in result.gap_reasons)


def test_risk_fusion_blocks_auto_clear_when_ood_is_over_threshold() -> None:
    _setup_gate_context(document_type="unknown_type", process_area="unknown_area")

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_gate_demo"
    )

    assert decision.auto_clear_allowed is False
    assert decision.ood_score >= 0.5
    assert "OOD score above threshold" in decision.auto_clear_blockers
    assert "no matching requirements found" in decision.required_human_review_reasons


def test_risk_fusion_blocks_auto_clear_for_high_critical_coverage_gaps() -> None:
    _setup_gate_context(include_complete_coverage=False)

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_gate_demo"
    )

    assert decision.auto_clear_allowed is False
    assert "coverage gap for high/critical scope" in decision.auto_clear_blockers
    assert any(
        "missing required reviewer role" in reason
        for reason in decision.coverage_gap_reasons
    )


def test_no_matching_requirements_is_review_reason_not_clearance() -> None:
    _setup_gate_context(
        document_type="supplier_certificate",
        process_area="warehouse",
        include_complete_coverage=True,
    )

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_gate_demo"
    )

    assert decision.decision != "auto_clear_candidate"
    assert decision.auto_clear_allowed is False
    assert "no matching requirements found" in decision.required_human_review_reasons


def test_review_pack_shows_ood_and_coverage_reasons_clearly() -> None:
    _setup_gate_context(
        document_type="unknown_type",
        process_area="unknown_area",
        claims=[],
        include_complete_coverage=False,
    )
    RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_gate_demo"
    )

    pack = ReviewPackService(repository=repository, audit_log=audit_log).get_review_pack(
        "ds_gate_demo"
    )

    assert "no matching requirements found" in pack.ood_reasons
    assert any("missing required reviewer role" in reason for reason in pack.coverage_gap_reasons)
    assert "OOD/Coverage" in pack.summary


def _setup_gate_context(
    *,
    document_type: str = "change_control",
    process_area: str = "aseptic_filling",
    language: str = "en",
    parsing_quality: float = 0.95,
    document_metadata: dict[str, object] | None = None,
    claims: list[Claim] | None = None,
    include_complete_coverage: bool = False,
    failed_reviewer_role: str | None = None,
) -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(
        _document_set(document_type=document_type, process_area=process_area)
    )
    repository.add_document(
        document=_document(
            language=language,
            parsing_quality=parsing_quality,
            metadata=document_metadata or {},
        ),
        chunks=[_chunk()],
    )
    if claims is None:
        claims = [_claim("claim_impact_a")]
    repository.replace_claim_ledger(document_set_id="ds_gate_demo", claims=claims)
    if include_complete_coverage:
        repository.replace_coverage_summaries(
            document_set_id="ds_gate_demo",
            coverage_summaries=[
                CoverageSummary(
                    agent_id=f"agent_{role}",
                    role=role,
                    coverage_summary=f"{role} completed review.",
                    finding_count=0,
                )
                for role in required_reviewer_roles_for_scope(
                    document_type=document_type,
                    process_area=process_area,
                )
            ],
        )
    if failed_reviewer_role is not None:
        audit_log.append(
            event_type="model_run_failed",
            actor_id="model_mock-reviewer",
            actor_type="model",
            entity_type="ModelRun",
            entity_id="run_failed_gate_demo",
            payload={
                "document_set_id": "ds_gate_demo",
                "role": failed_reviewer_role,
                "status": "failed",
            },
        )


def _document_set(*, document_type: str, process_area: str) -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_gate_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_gate_demo",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type=document_type,
        declared_process_area=process_area,
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_gate_demo",
        tenant_id="tenant_demo_pharma",
        name="Gate Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_gate_threshold_validation",
                "source_type": "internal_sop",
                "source_name": "SOP-CC-AVI-001",
                "source_version": "3.0",
                "section": "8.4",
                "requirement_text": "Threshold changes require current validation evidence.",
                "applies_to_document_types": ["change_control", "deviation"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["validation addendum"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )


def _document(
    *,
    language: str,
    parsing_quality: float,
    metadata: dict[str, object],
) -> Document:
    return Document(
        document_id="doc_gate_change",
        document_set_id="ds_gate_demo",
        filename="change-control.txt",
        file_hash_sha256=sha256(b"change-control.txt").hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri="local://gate/change-control.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=parsing_quality,
        language=language,
        metadata=metadata,
    )


def _chunk() -> DocumentChunk:
    text = "Change control CC-2026-014 modifies the AVI threshold."
    return DocumentChunk(
        chunk_id="chunk_gate_change_p1",
        document_id="doc_gate_change",
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )
