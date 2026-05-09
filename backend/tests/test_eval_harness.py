from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.evals import EvalDataset
from app.schemas.risk import RiskDecision
from app.services.eval_runner import EvalRunner


def test_metrics_calculation_counts_recall_precision_and_false_positives() -> None:
    dataset = _dataset()
    matching_finding = _finding(
        finding_id="finding_eval_match",
        risk_category="batch_impact_assessment",
        severity="high",
        requirement_references=["req_eval_batch_impact"],
        quote="Batch impact assessment is missing for BATCH-001.",
    )
    false_positive = _finding(
        finding_id="finding_eval_false_positive",
        risk_category="qa_approval",
        severity="medium",
        requirement_references=["req_eval_qa_approval"],
        quote="QA approval is documented.",
    )

    report = EvalRunner().evaluate(
        dataset=dataset,
        system_findings=[matching_finding, false_positive],
        risk_decision=_risk_decision(decision="human_review_required", auto_clear=False),
    )

    assert report.passed is True
    assert report.metrics.recall_by_severity["high"] == 1.0
    assert report.metrics.false_omission_rate == 0.0
    assert report.metrics.false_positive_rate == 0.5
    assert report.metrics.citation_precision == 0.5
    assert report.metrics.requirement_match_accuracy == 1.0
    assert report.metrics.human_review_rate == 1.0


def test_critical_must_detect_missed_fails_eval() -> None:
    dataset = _dataset(expected_severity="critical")

    report = EvalRunner().evaluate(
        dataset=dataset,
        system_findings=[],
        risk_decision=_risk_decision(decision="human_review_required", auto_clear=False),
    )

    assert report.passed is False
    assert report.metrics.recall_by_severity["critical"] == 0.0
    assert report.metrics.false_omission_rate == 1.0
    assert any("Critical must_detect finding missed" in failure for failure in report.failures)


def test_auto_clear_with_known_high_or_critical_gold_fails_eval() -> None:
    dataset = _dataset(expected_severity="high")
    matching_finding = _finding(
        finding_id="finding_eval_match",
        risk_category="batch_impact_assessment",
        severity="high",
        requirement_references=["req_eval_batch_impact"],
        quote="Batch impact assessment is missing for BATCH-001.",
    )

    report = EvalRunner().evaluate(
        dataset=dataset,
        system_findings=[matching_finding],
        risk_decision=_risk_decision(decision="auto_clear_candidate", auto_clear=True),
    )

    assert report.passed is False
    assert report.metrics.auto_clear_false_negative_count == 1
    assert any(
        "Auto-clear despite known high/critical gold finding" in failure
        for failure in report.failures
    )


def test_runner_loads_three_fixture_datasets_and_generates_markdown() -> None:
    runner = EvalRunner(fixture_dir=Path("examples/evals"))

    datasets = runner.list_datasets()
    dataset_ids = {dataset.dataset.dataset_id for dataset in datasets}

    assert dataset_ids >= {
        "evalds_clean_low_risk",
        "evalds_deviation_missing_batch_impact",
        "evalds_capa_missing_effectiveness_check",
    }
    report = runner.run_fixture("evalds_deviation_missing_batch_impact")
    markdown = runner.render_markdown(report)
    assert "## Pass/Fail" in markdown
    assert "false_omission_rate" in markdown


def test_eval_endpoint_runs_fixture_dataset() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/run",
        json={"dataset_id": "evalds_deviation_missing_batch_impact"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset"]["dataset_id"] == "evalds_deviation_missing_batch_impact"
    assert "markdown_report" in payload
    assert payload["metrics"]["recall_by_severity"]["high"] == 1.0


def _dataset(*, expected_severity: str = "high") -> EvalDataset:
    return EvalDataset(
        dataset_id="evalds_metric_demo",
        name="Metric demo",
        version="2026.1",
        document_type="deviation",
        process_area="aseptic_filling",
        gold_findings=[
            {
                "gold_finding_id": "gold_batch_impact_missing",
                "expected_risk_category": "batch_impact_assessment",
                "expected_severity": expected_severity,
                "expected_requirement_ids": ["req_eval_batch_impact"],
                "expected_evidence_refs": [
                    {
                        "document_id": "doc_eval_deviation",
                        "chunk_id": "chunk_eval_deviation_p1",
                        "page": 1,
                        "quote": "Batch impact assessment is missing for BATCH-001.",
                    }
                ],
                "must_detect": True,
            }
        ],
        seeded_defects=["missing batch impact assessment"],
    )


def _finding(
    *,
    finding_id: str,
    risk_category: str,
    severity: str,
    requirement_references: list[str],
    quote: str,
) -> dict[str, object]:
    return {
        "finding_id": finding_id,
        "document_set_id": "ds_eval_demo",
        "risk_category": risk_category,
        "severity": severity,
        "likelihood": 3,
        "detectability": 3,
        "risk_statement": f"{risk_category} finding.",
        "evidence_items": [
            {
                "document_id": "doc_eval_deviation",
                "chunk_id": "chunk_eval_deviation_p1",
                "page": 1,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": "supports",
                "verifier_score": 0.9,
            }
        ],
        "requirement_references": requirement_references,
        "missing_information": [],
        "model_provider": "mock",
        "model_name": "mock-eval-reviewer",
        "model_version": "0.1.0",
        "prompt_version": "eval-v0.1",
        "evidence_support": "strong",
        "recommended_action": "Route according to eval policy.",
        "auto_close_allowed": False,
        "status": "open",
    }


def _risk_decision(*, decision: str, auto_clear: bool) -> RiskDecision:
    return RiskDecision(
        document_set_id="ds_eval_demo",
        decision=decision,
        max_severity="high",
        credible_high_or_critical_exists=not auto_clear,
        model_disagreement_score=0.0,
        document_quality_score=0.95,
        ood_score=0.0,
        auto_clear_allowed=auto_clear,
        auto_clear_blockers=[],
        required_human_review_reasons=[] if auto_clear else ["eval human review"],
        finding_clusters=[],
        generated_at=datetime.now(UTC),
        policy_version="eval-test-policy-v0.1",
    )
