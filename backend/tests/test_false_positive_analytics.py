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
from app.schemas.risk import RiskDecision as RiskDecisionSchema
from app.services.false_positive_analytics import HumanOverrideAnalyzer


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()


def test_human_override_analyzer_clusters_false_positive_decisions() -> None:
    _setup_false_positive_context()
    repository.replace_risk_findings(
        document_set_id="ds_fp_demo",
        findings=[
            _finding("finding_fp_a", severity="medium", evidence_support="weak"),
            _finding("finding_fp_b", severity="medium", evidence_support="weak"),
        ],
    )
    repository.add_review_decision(
        _review_decision("review_fp_a", "finding_fp_a", decision="reject_false_positive")
    )
    repository.add_review_decision(
        _review_decision("review_fp_b", "finding_fp_b", decision="downgrade")
    )

    report = HumanOverrideAnalyzer(repository=repository, audit_log=audit_log).analyze()

    assert report.total_override_decisions == 2
    assert len(report.clusters) == 1
    cluster = report.clusters[0]
    assert cluster.group.requirement_id == "req_fp_qa_review"
    assert cluster.group.risk_category == "qa_approval"
    assert cluster.group.agent_role == "RegulatoryConsistencyReviewer"
    assert cluster.group.prompt_version == "regulatory-consistency-v1"
    assert cluster.group.evidence_support == "weak"
    assert cluster.group.document_type == "change_control"
    assert cluster.finding_ids == ["finding_fp_a", "finding_fp_b"]
    assert {
        recommendation.recommendation_type for recommendation in cluster.recommendations
    } >= {
        "PROMPT_CLARIFICATION_CANDIDATE",
        "REQUIREMENT_RULE_CLARIFICATION_CANDIDATE",
        "DETERMINISTIC_VERIFIER_RULE_CANDIDATE",
        "DO_NOT_AUTO_ESCALATE_PATTERN_CANDIDATE",
    }
    assert cluster.auto_rule_change_allowed is False
    assert any(
        "new version" in follow_up.lower()
        for recommendation in cluster.recommendations
        for follow_up in recommendation.required_follow_up
    )


def test_false_positive_patterns_do_not_auto_close_high_or_critical_findings() -> None:
    _setup_false_positive_context()
    high_finding = _finding("finding_fp_high", severity="high", evidence_support="partial")
    repository.replace_risk_findings(document_set_id="ds_fp_demo", findings=[high_finding])
    repository.add_review_decision(
        _review_decision("review_fp_high", "finding_fp_high", decision="reject_false_positive")
    )
    original_decision = _risk_decision(auto_clear_allowed=False)
    repository.add_risk_decision(document_set_id="ds_fp_demo", risk_decision=original_decision)

    report = HumanOverrideAnalyzer(repository=repository, audit_log=audit_log).analyze()

    latest_decision = repository.get_latest_risk_decision("ds_fp_demo")
    assert latest_decision == original_decision
    assert report.clusters[0].max_severity == "high"
    assert report.clusters[0].high_critical_recall_guard is True
    assert report.clusters[0].auto_rule_change_allowed is False
    assert not any(
        recommendation.recommendation_type == "DO_NOT_AUTO_ESCALATE_PATTERN_CANDIDATE"
        for recommendation in report.clusters[0].recommendations
    )


def test_false_positive_analytics_endpoint_returns_clusters() -> None:
    _setup_false_positive_context()
    repository.replace_risk_findings(
        document_set_id="ds_fp_demo",
        findings=[_finding("finding_fp_endpoint", severity="medium", evidence_support="weak")],
    )
    repository.add_review_decision(
        _review_decision(
            "review_fp_endpoint",
            "finding_fp_endpoint",
            decision="reject_false_positive",
        )
    )
    client = TestClient(app)

    response = client.get("/analytics/false-positives")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_override_decisions"] == 1
    assert payload["clusters"][0]["group"]["risk_category"] == "qa_approval"
    assert payload["clusters"][0]["auto_rule_change_allowed"] is False


def _setup_false_positive_context() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set())
    repository.add_document(document=_document(), chunks=[_chunk()])
    audit_log.append(
        event_type="finding_created",
        actor_id="model_mock-reviewer",
        actor_type="model",
        entity_type="RiskFinding",
        entity_id="finding_fp_a",
        tenant_id="tenant_demo_pharma",
        payload={
            "document_set_id": "ds_fp_demo",
            "agent_role": "RegulatoryConsistencyReviewer",
            "prompt_version": "regulatory-consistency-v1",
        },
    )
    audit_log.append(
        event_type="finding_created",
        actor_id="model_mock-reviewer",
        actor_type="model",
        entity_type="RiskFinding",
        entity_id="finding_fp_b",
        tenant_id="tenant_demo_pharma",
        payload={
            "document_set_id": "ds_fp_demo",
            "agent_role": "RegulatoryConsistencyReviewer",
            "prompt_version": "regulatory-consistency-v1",
        },
    )
    audit_log.append(
        event_type="finding_created",
        actor_id="model_mock-reviewer",
        actor_type="model",
        entity_type="RiskFinding",
        entity_id="finding_fp_endpoint",
        tenant_id="tenant_demo_pharma",
        payload={
            "document_set_id": "ds_fp_demo",
            "agent_role": "RegulatoryConsistencyReviewer",
            "prompt_version": "regulatory-consistency-v1",
        },
    )


def _document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_fp_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_fp_demo",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="change_control",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_fp_demo",
        tenant_id="tenant_demo_pharma",
        name="False Positive Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_fp_qa_review",
                "source_type": "internal_sop",
                "source_name": "SOP-FP-001",
                "source_version": "1.0",
                "section": "4.1",
                "requirement_text": "Quality-impacting change controls require QA review.",
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "medium",
                "required_evidence": ["QA review record"],
                "auto_close_allowed": True,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )


def _document() -> Document:
    return Document(
        document_id="doc_fp_change",
        document_set_id="ds_fp_demo",
        filename="change-control.txt",
        file_hash_sha256=sha256(b"change-control.txt").hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri="local://fp/change-control.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=0.95,
        language="en",
        metadata={},
    )


def _chunk() -> DocumentChunk:
    text = "Change control includes QA review record."
    return DocumentChunk(
        chunk_id="chunk_fp_change_p1",
        document_id="doc_fp_change",
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
    evidence_support: str,
) -> RiskFinding:
    quote = "Change control includes QA review record."
    return RiskFinding(
        finding_id=finding_id,
        document_set_id="ds_fp_demo",
        risk_category="qa_approval",
        severity=severity,
        likelihood=3,
        detectability=3,
        risk_statement="QA approval appears pending and should be reviewed.",
        evidence_items=[
            {
                "document_id": "doc_fp_change",
                "chunk_id": "chunk_fp_change_p1",
                "page": 1,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": "supports",
                "verifier_score": 0.95,
            }
        ],
        requirement_references=["req_fp_qa_review"],
        missing_information=[],
        model_provider="mock",
        model_name="mock-reviewer",
        model_version="0.1.0",
        prompt_version="regulatory-consistency-v1",
        evidence_support=evidence_support,
        recommended_action="Route to human reviewer.",
        auto_close_allowed=False,
        status="needs_human_review",
    )


def _review_decision(review_id: str, finding_id: str, *, decision: str) -> ReviewDecision:
    return ReviewDecision(
        review_id=review_id,
        finding_id=finding_id,
        reviewer_id="reviewer_qa_1",
        decision=decision,
        rationale="Reviewer determined the generated finding over-escalated the cited record.",
        created_at=datetime.now(UTC),
    )


def _risk_decision(*, auto_clear_allowed: bool) -> RiskDecisionSchema:
    return RiskDecisionSchema(
        document_set_id="ds_fp_demo",
        decision="human_review_required",
        max_severity="high",
        credible_high_or_critical_exists=True,
        model_disagreement_score=0.0,
        document_quality_score=0.95,
        ood_score=0.0,
        auto_clear_allowed=auto_clear_allowed,
        auto_clear_blockers=["single high/critical finding is sufficient for human review"],
        required_human_review_reasons=[
            "single high/critical finding is sufficient for human review"
        ],
        finding_clusters=[],
        generated_at=datetime.now(UTC),
        policy_version="risk-fusion-policy-v0.2",
    )
