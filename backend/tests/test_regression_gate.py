from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.evals import (
    ConfigVersion,
    EvalDataset,
    EvalMetrics,
    EvalReport,
    GoldFinding,
    RegressionRun,
)
from app.services.regression_gate import RegressionGateService


def test_regression_gate_blocks_missed_critical_must_detect() -> None:
    baseline = _run(
        run_id="regrun_baseline_critical",
        config_id="cfg_baseline",
        reports=[
            _report(
                dataset_id="evalds_critical_miss",
                severity="critical",
                matched_gold_ids=["gold_critical_batch_release"],
                unmatched_gold_ids=[],
                recall=1.0,
            )
        ],
    )
    candidate = _run(
        run_id="regrun_candidate_critical",
        config_id="cfg_candidate",
        reports=[
            _report(
                dataset_id="evalds_critical_miss",
                severity="critical",
                matched_gold_ids=[],
                unmatched_gold_ids=["gold_critical_batch_release"],
                recall=0.0,
            )
        ],
    )

    report = RegressionGateService().compare(baseline=baseline, candidate=candidate)

    assert report.passed is False
    assert "MISSED_CRITICAL_MUST_DETECT" in {
        criterion.criterion for criterion in report.blocking_criteria
    }
    assert "Status: FAIL" in report.markdown_report


def test_regression_gate_blocks_missed_high_must_detect() -> None:
    baseline = _run(
        run_id="regrun_baseline_high",
        config_id="cfg_baseline",
        reports=[
            _report(
                dataset_id="evalds_high_miss",
                severity="high",
                matched_gold_ids=["gold_high_batch_release"],
                unmatched_gold_ids=[],
                recall=1.0,
            )
        ],
    )
    candidate = _run(
        run_id="regrun_candidate_high",
        config_id="cfg_candidate",
        reports=[
            _report(
                dataset_id="evalds_high_miss",
                severity="high",
                matched_gold_ids=[],
                unmatched_gold_ids=["gold_high_batch_release"],
                recall=0.0,
            )
        ],
    )

    report = RegressionGateService().compare(baseline=baseline, candidate=candidate)

    assert report.passed is False
    assert "MISSED_HIGH_MUST_DETECT" in {
        criterion.criterion for criterion in report.blocking_criteria
    }


def test_regression_gate_blocks_auto_clear_with_known_high_or_critical_gold() -> None:
    baseline = _run(
        run_id="regrun_baseline_autoclear",
        config_id="cfg_baseline",
        reports=[_report(dataset_id="evalds_autoclear", severity="high", recall=1.0)],
    )
    candidate = _run(
        run_id="regrun_candidate_autoclear",
        config_id="cfg_candidate",
        reports=[
            _report(
                dataset_id="evalds_autoclear",
                severity="high",
                recall=1.0,
                auto_clear_false_negative_count=1,
            )
        ],
    )

    report = RegressionGateService().compare(baseline=baseline, candidate=candidate)

    assert report.passed is False
    assert "AUTO_CLEAR_HIGH_CRITICAL_GOLD" in {
        criterion.criterion for criterion in report.blocking_criteria
    }


def test_regression_gate_blocks_metric_threshold_regressions() -> None:
    baseline = _run(
        run_id="regrun_baseline_thresholds",
        config_id="cfg_baseline",
        reports=[
            _report(
                dataset_id="evalds_thresholds",
                severity="medium",
                recall=1.0,
                citation_precision=0.98,
                requirement_match_accuracy=0.98,
            )
        ],
    )
    candidate = _run(
        run_id="regrun_candidate_thresholds",
        config_id="cfg_candidate",
        reports=[
            _report(
                dataset_id="evalds_thresholds",
                severity="medium",
                recall=1.0,
                citation_precision=0.72,
                requirement_match_accuracy=0.74,
            )
        ],
    )

    report = RegressionGateService(
        citation_precision_threshold=0.9,
        requirement_match_accuracy_threshold=0.9,
    ).compare(baseline=baseline, candidate=candidate)

    criteria = {criterion.criterion for criterion in report.blocking_criteria}
    assert "CITATION_PRECISION_BELOW_THRESHOLD" in criteria
    assert "REQUIREMENT_MATCH_ACCURACY_BELOW_THRESHOLD" in criteria
    assert report.json_report["passed"] is False


def test_regression_gate_blocks_human_review_rate_increase_without_recall_gain() -> None:
    baseline = _run(
        run_id="regrun_baseline_hrr",
        config_id="cfg_baseline",
        reports=[
            _report(
                dataset_id="evalds_hrr",
                severity="high",
                recall=1.0,
                human_review_rate=0.2,
            )
        ],
    )
    candidate = _run(
        run_id="regrun_candidate_hrr",
        config_id="cfg_candidate",
        reports=[
            _report(
                dataset_id="evalds_hrr",
                severity="high",
                recall=1.0,
                human_review_rate=0.8,
            )
        ],
    )

    report = RegressionGateService(max_human_review_rate_increase=0.25).compare(
        baseline=baseline,
        candidate=candidate,
    )

    assert report.passed is False
    assert "HUMAN_REVIEW_RATE_INCREASE_WITHOUT_RECALL_GAIN" in {
        criterion.criterion for criterion in report.blocking_criteria
    }


def test_regression_gate_allows_human_review_rate_increase_when_recall_improves() -> None:
    baseline = _run(
        run_id="regrun_baseline_recall_gain",
        config_id="cfg_baseline",
        reports=[
            _report(
                dataset_id="evalds_recall_gain",
                severity="high",
                matched_gold_ids=[],
                unmatched_gold_ids=["gold_high_recall_gain"],
                recall=0.0,
                human_review_rate=0.2,
            )
        ],
    )
    candidate = _run(
        run_id="regrun_candidate_recall_gain",
        config_id="cfg_candidate",
        reports=[
            _report(
                dataset_id="evalds_recall_gain",
                severity="high",
                matched_gold_ids=["gold_high_recall_gain"],
                unmatched_gold_ids=[],
                recall=1.0,
                human_review_rate=0.8,
            )
        ],
    )

    report = RegressionGateService(max_human_review_rate_increase=0.25).compare(
        baseline=baseline,
        candidate=candidate,
    )

    assert report.passed is True
    assert report.blocking_criteria == []
    assert "Status: PASS" in report.markdown_report


def _run(
    *,
    run_id: str,
    config_id: str,
    reports: list[EvalReport],
) -> RegressionRun:
    return RegressionRun(
        regression_run_id=run_id,
        config_version=_config(config_id),
        eval_reports=reports,
        generated_at=datetime.now(UTC),
        runner_version="regression-gate-test",
    )


def _config(config_id: str) -> ConfigVersion:
    return ConfigVersion(
        config_version_id=config_id,
        model_provider="mock",
        model_name="mock-reviewer",
        model_version="0.1.0",
        prompt_versions={"DeviationReviewer": "deviation_reviewer_v1"},
        requirement_set_id="rset_eval_demo",
        requirement_set_version="2026.1",
        risk_fusion_policy_version="risk-fusion-policy-v0.2",
        orchestration_version="orchestration-v0.1",
        created_at=datetime.now(UTC),
    )


def _report(
    *,
    dataset_id: str,
    severity: str,
    matched_gold_ids: list[str] | None = None,
    unmatched_gold_ids: list[str] | None = None,
    recall: float,
    citation_precision: float = 0.95,
    requirement_match_accuracy: float = 0.95,
    auto_clear_false_negative_count: int = 0,
    human_review_rate: float = 0.4,
) -> EvalReport:
    matched = (
        matched_gold_ids
        if matched_gold_ids is not None
        else [f"gold_{severity}_{dataset_id}"]
    )
    unmatched = unmatched_gold_ids if unmatched_gold_ids is not None else []
    gold_ids = matched + unmatched
    dataset = EvalDataset(
        dataset_id=dataset_id,
        name=f"Dataset {dataset_id}",
        version="2026.1",
        document_type="deviation",
        process_area="aseptic_filling",
        gold_findings=[
            _gold_finding(gold_id=gold_id, severity=severity)
            for gold_id in gold_ids
        ],
        seeded_defects=["seeded defect"] if gold_ids else [],
    )
    failures = [
        f"Critical must_detect finding missed: {gold_id}"
        for gold_id in unmatched
        if severity == "critical"
    ]
    if auto_clear_false_negative_count:
        failures.append("Auto-clear despite known high/critical gold finding")
    passed = not failures
    return EvalReport(
        dataset=dataset,
        metrics=EvalMetrics(
            recall_by_severity={severity: recall},
            false_omission_rate=1.0 - recall,
            false_positive_rate=0.0,
            citation_precision=citation_precision,
            requirement_match_accuracy=requirement_match_accuracy,
            auto_clear_false_negative_count=auto_clear_false_negative_count,
            human_review_rate=human_review_rate,
        ),
        passed=passed,
        failures=failures,
        matched_gold_finding_ids=matched,
        unmatched_gold_finding_ids=unmatched,
        false_positive_finding_ids=[],
        markdown_report="fixture report",
        generated_at=datetime.now(UTC),
        runner_version="eval-runner-test",
    )


def _gold_finding(*, gold_id: str, severity: str) -> GoldFinding:
    return GoldFinding(
        gold_finding_id=gold_id,
        expected_risk_category="batch_impact_assessment",
        expected_severity=severity,
        expected_requirement_ids=["req_eval_batch_impact"],
        expected_evidence_refs=[],
        must_detect=True,
    )
