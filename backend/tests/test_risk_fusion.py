from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256

import pytest
from fastapi.testclient import TestClient

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.main import app
from app.risk.gates import required_reviewer_roles_for_scope
from app.schemas.domain import (
    Document,
    DocumentChunk,
    DocumentSet,
    FindingVerificationResult,
    ModelRun,
    RequirementSet,
    RiskFinding,
    TokenUsage,
)
from app.schemas.review import CoverageSummary
from app.services.risk_fusion import RiskFusionService


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()


def test_single_critical_finding_requires_human_review_without_majority_vote() -> None:
    _setup_document_context()
    repository.replace_risk_findings(
        document_set_id="ds_fusion_demo",
        findings=[_finding("finding_critical_single", severity="critical")],
    )
    repository.replace_coverage_summaries(
        document_set_id="ds_fusion_demo",
        coverage_summaries=[
            _coverage("agent_a", finding_count=0),
            _coverage("agent_b", finding_count=0),
        ],
    )

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert decision.decision == "human_review_required"
    assert decision.credible_high_or_critical_exists is True
    assert "single high/critical finding is sufficient" in " ".join(
        decision.required_human_review_reasons
    )


def test_weak_high_risk_finding_blocks_auto_clear() -> None:
    _setup_document_context()
    repository.replace_risk_findings(
        document_set_id="ds_fusion_demo",
        findings=[
            _finding(
                "finding_high_weak",
                severity="high",
                evidence_support="weak",
                verification_result=_verification(
                    finding_id="finding_high_weak",
                    evidence_support="weak",
                    deterministic_checks_passed=False,
                ),
            )
        ],
    )

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert decision.decision == "blocked_due_to_unverified_high_risk"
    assert "high/critical finding has weak or partial evidence" in decision.auto_clear_blockers
    assert decision.auto_clear_allowed is False


def test_model_disagreement_on_possible_high_risk_routes_to_human_review() -> None:
    _setup_document_context()
    repository.replace_risk_findings(
        document_set_id="ds_fusion_demo",
        findings=[
            _finding(
                "finding_visual_low",
                severity="low",
                risk_category="visual_inspection",
                model_name="reviewer-low",
            ),
            _finding(
                "finding_visual_high",
                severity="high",
                risk_category="visual_inspection",
                model_name="reviewer-high",
            ),
        ],
    )

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert decision.decision == "human_review_required"
    assert decision.model_disagreement_score > 0
    assert any("model disagreement" in reason for reason in decision.required_human_review_reasons)


def test_parser_quality_below_threshold_blocks_auto_clear() -> None:
    _setup_document_context(document_quality=0.2)
    repository.replace_risk_findings(
        document_set_id="ds_fusion_demo",
        findings=[_finding("finding_low_clean", severity="low", auto_close_allowed=True)],
    )

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert decision.decision == "insufficient_document_quality"
    assert "document quality below threshold" in decision.auto_clear_blockers
    assert decision.document_quality_score == 0.2


def test_out_of_scope_document_set_is_not_auto_cleared() -> None:
    _setup_document_context(process_area="warehouse")

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert decision.decision == "out_of_scope"
    assert decision.ood_score == 1.0
    assert "document set is outside active requirement scope" in decision.auto_clear_blockers


def test_missing_required_attachments_blocks_auto_clear_as_more_information_needed() -> None:
    _setup_document_context(
        document_metadata={"required_attachments_missing": ["validation addendum"]}
    )

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert decision.decision == "needs_more_information"
    assert "missing required attachment: validation addendum" in decision.auto_clear_blockers
    assert decision.auto_clear_allowed is False


def test_failed_model_run_blocks_auto_clear_when_review_coverage_is_affected() -> None:
    _setup_document_context()
    repository.add_model_run(
        document_set_id="ds_fusion_demo",
        model_run=_model_run(status="failed"),
    )

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert decision.decision == "blocked_due_to_model_failure"
    assert "failed model run affects review coverage" in decision.auto_clear_blockers


def test_auto_clear_candidate_only_when_all_gates_pass() -> None:
    _setup_document_context()
    repository.replace_risk_findings(
        document_set_id="ds_fusion_demo",
        findings=[
            _finding(
                "finding_low_strong",
                severity="low",
                evidence_support="strong",
                auto_close_allowed=True,
            )
        ],
    )

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert decision.decision == "auto_clear_candidate"
    assert decision.auto_clear_allowed is True
    assert decision.auto_clear_blockers == []


def test_any_coverage_gap_blocks_auto_clear_even_without_high_critical_scope() -> None:
    _setup_document_context(requirement_criticality="medium")
    repository.replace_coverage_summaries(
        document_set_id="ds_fusion_demo",
        coverage_summaries=[
            CoverageSummary(
                agent_id="agent_GMPDataIntegrityReviewer",
                role="GMPDataIntegrityReviewer",
                coverage_summary="Only one required reviewer role completed review.",
                finding_count=0,
            )
        ],
    )

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert decision.decision == "human_review_required"
    assert decision.auto_clear_allowed is False
    assert "coverage gap blocks auto-clear" in decision.auto_clear_blockers
    assert any(
        reason.startswith("missing required reviewer role")
        for reason in decision.coverage_gap_reasons
    )


def test_finding_clustering_groups_related_findings_without_majority_vote() -> None:
    _setup_document_context()
    repository.replace_risk_findings(
        document_set_id="ds_fusion_demo",
        findings=[
            _finding(
                "finding_same_cluster_a",
                severity="medium",
                risk_category="data_integrity",
                requirement_references=["req_fusion_data_integrity"],
            ),
            _finding(
                "finding_same_cluster_b",
                severity="medium",
                risk_category="data_integrity",
                requirement_references=["req_fusion_data_integrity"],
                model_name="second-reviewer",
            ),
        ],
    )

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert len(decision.finding_clusters) == 1
    assert set(decision.finding_clusters[0].finding_ids) == {
        "finding_same_cluster_a",
        "finding_same_cluster_b",
    }


def test_risk_decision_is_persisted_and_audited_with_policy_version() -> None:
    _setup_document_context()

    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_fusion_demo"
    )

    assert repository.get_latest_risk_decision("ds_fusion_demo") == decision
    event = audit_log.list_events()[-1]
    assert event.event_type == "risk_fusion_decision_generated"
    assert event.payload["policy_version"] == decision.policy_version
    assert event.payload["decision"] == decision.decision


def test_risk_fusion_endpoint_returns_risk_decision() -> None:
    _setup_document_context()
    client = TestClient(app)

    response = client.post("/document-sets/ds_fusion_demo/run-risk-fusion")

    assert response.status_code == 200
    assert response.json()["document_set_id"] == "ds_fusion_demo"
    assert response.json()["policy_version"] == "risk-fusion-policy-v0.2"


def _setup_document_context(
    *,
    document_quality: float = 0.95,
    document_metadata: dict[str, object] | None = None,
    process_area: str = "aseptic_filling",
    requirement_criticality: str = "high",
) -> None:
    repository.create_requirement_set(_requirement_set(criticality=requirement_criticality))
    repository.create_document_set(_document_set(process_area=process_area))
    repository.add_document(
        document=_document(quality=document_quality, metadata=document_metadata or {}),
        chunks=[_chunk()],
    )
    repository.replace_coverage_summaries(
        document_set_id="ds_fusion_demo",
        coverage_summaries=[
            CoverageSummary(
                agent_id=f"agent_{role}",
                role=role,
                coverage_summary=f"{role} completed review.",
                finding_count=0,
            )
            for role in required_reviewer_roles_for_scope(
                document_type="change_control",
                process_area=process_area,
            )
        ],
    )


def _document_set(*, process_area: str) -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_fusion_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_fusion_demo_2026",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="change_control",
        declared_process_area=process_area,
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set(*, criticality: str = "high") -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_fusion_demo_2026",
        tenant_id="tenant_demo_pharma",
        name="Fusion Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_fusion_threshold_validation",
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
                "criticality": criticality,
                "required_evidence": ["validation addendum"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_fusion_data_integrity",
                "source_type": "checklist",
                "source_name": "DI Checklist",
                "source_version": "1.0",
                "section": "4.1",
                "requirement_text": "Inspection data integrity review should be documented.",
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "medium",
                "required_evidence": ["audit trail review"],
                "auto_close_allowed": True,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
        ],
    )


def _document(*, quality: float, metadata: dict[str, object]) -> Document:
    return Document(
        document_id="doc_fusion_change",
        document_set_id="ds_fusion_demo",
        filename="change-control.txt",
        file_hash_sha256=sha256(b"change-control.txt").hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri="local://fusion/change-control.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=quality,
        language="en",
        metadata=metadata,
    )


def _chunk() -> DocumentChunk:
    text = "Change control CC-2026-014 modifies the AVI threshold."
    return DocumentChunk(
        chunk_id="chunk_fusion_change_p1",
        document_id="doc_fusion_change",
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )


def _finding(
    finding_id: str,
    *,
    severity: str,
    risk_category: str = "visual_inspection",
    evidence_support: str = "strong",
    requirement_references: list[str] | None = None,
    model_name: str = "mock-reviewer",
    auto_close_allowed: bool = False,
    verification_result: FindingVerificationResult | None = None,
) -> RiskFinding:
    quote = "Change control CC-2026-014 modifies the AVI threshold."
    return RiskFinding(
        finding_id=finding_id,
        document_set_id="ds_fusion_demo",
        risk_category=risk_category,
        severity=severity,
        likelihood=3,
        detectability=3,
        risk_statement=f"{risk_category} finding with {severity} severity.",
        evidence_items=[
            {
                "document_id": "doc_fusion_change",
                "chunk_id": "chunk_fusion_change_p1",
                "page": 1,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": "supports",
                "verifier_score": 0.95,
            }
        ],
        requirement_references=requirement_references
        or ["req_fusion_threshold_validation"],
        missing_information=[],
        model_provider="mock",
        model_name=model_name,
        model_version="0.1.0",
        prompt_version="test-review-v0.1",
        evidence_support=evidence_support,
        recommended_action="Route according to risk fusion policy.",
        auto_close_allowed=auto_close_allowed,
        status="open",
        verification_result=verification_result,
    )


def _verification(
    *,
    finding_id: str,
    evidence_support: str,
    deterministic_checks_passed: bool,
) -> FindingVerificationResult:
    return FindingVerificationResult(
        finding_id=finding_id,
        evidence_support=evidence_support,
        quote_exists=True,
        quote_matches_chunk=deterministic_checks_passed,
        requirement_applicable=True,
        unsupported_claims=[] if deterministic_checks_passed else ["quote mismatch"],
        missing_evidence=[] if deterministic_checks_passed else ["verified source support"],
        verifier_rationale="Deterministic test verification result.",
        verifier_model_run_id=None,
        deterministic_checks_passed=deterministic_checks_passed,
    )


def _coverage(agent_id: str, *, finding_count: int) -> CoverageSummary:
    return CoverageSummary(
        agent_id=agent_id,
        role=agent_id,
        coverage_summary=f"{agent_id} generated {finding_count} finding(s).",
        finding_count=finding_count,
    )


def _model_run(*, status: str) -> ModelRun:
    started_at = datetime.now(UTC)
    return ModelRun(
        model_run_id="run_failed_coverage",
        provider="mock",
        model_name="mock-reviewer",
        model_version="0.1.0",
        prompt_version="test-review-v0.1",
        input_hash=sha256(b"input").hexdigest(),
        output_hash=sha256(b"output").hexdigest(),
        started_at=started_at,
        completed_at=started_at + timedelta(milliseconds=20),
        latency_ms=20,
        token_usage=TokenUsage(input_tokens=1, output_tokens=1, total_tokens=2),
        status=status,
    )
