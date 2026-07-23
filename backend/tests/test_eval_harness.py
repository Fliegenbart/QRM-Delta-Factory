from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from fastapi.testclient import TestClient

from app.evals import run_goldstandard
from app.main import app
from app.schemas.evals import EvalDataset
from app.schemas.risk import RiskDecision
from app.services.eval_runner import EvalRunner


def test_goldstandard_harness_falls_back_to_backend_packaged_requirement_library(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(run_goldstandard, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(run_goldstandard, "BACKEND_DIR", tmp_path / "packaged-backend")
    library_path = (
        run_goldstandard.BACKEND_DIR
        / "src"
        / "data"
        / "gmp-general-requirement-library.json"
    )
    library_path.parent.mkdir(parents=True)
    library_path.write_text('{"requirements": [{"requirement_id": "req_packaged"}]}')

    requirement_set = run_goldstandard._requirement_set()

    assert requirement_set["requirement_set_id"] == run_goldstandard.REQUIREMENT_SET_ID
    assert requirement_set["requirements"]


def test_goldstandard_harness_adds_configured_tenant_auth_header() -> None:
    headers = run_goldstandard._tenant_auth_headers(
        {"test-key": run_goldstandard.TENANT_ID},
        run_goldstandard.TENANT_ID,
    )

    assert headers == {"X-API-Key": "test-key"}


def test_goldstandard_harness_isolates_storage_and_auth_from_production(monkeypatch) -> None:
    monkeypatch.setenv("QRM_PERSISTENCE_ENABLED", "true")
    monkeypatch.setenv("QRM_API_KEYS", "tenant_live=live-key")
    monkeypatch.setenv("QRM_LOCAL_STORAGE_ROOT", "/data/documents")

    run_goldstandard._configure_environment(
        "mock",
        "frontier",
        "claude-sonnet-4-6",
        "gpt-5.4",
        "mistral-large-latest",
    )

    assert run_goldstandard.os.environ["QRM_PERSISTENCE_ENABLED"] == "false"
    assert run_goldstandard.os.environ["QRM_API_KEYS"] == ""
    assert (
        run_goldstandard.os.environ["QRM_LOCAL_STORAGE_ROOT"]
        == "/tmp/qrm-goldstandard-documents"
    )


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


def test_high_must_detect_missed_fails_eval() -> None:
    dataset = _dataset(expected_severity="high")

    report = EvalRunner().evaluate(
        dataset=dataset,
        system_findings=[],
        risk_decision=_risk_decision(decision="human_review_required", auto_clear=False),
    )

    assert report.passed is False
    assert report.metrics.recall_by_severity["high"] == 0.0
    assert any("High must_detect finding missed" in failure for failure in report.failures)


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


def test_evaluator_tracks_pkg_quality_metrics_without_counting_duplicates_as_new_risks() -> None:
    dataset = EvalDataset(
        dataset_id="evalds_pkg_quality_metrics",
        name="PKG quality metrics",
        version="2026.1",
        document_type="change_control",
        process_area="quality_control",
        acceptable_false_positive_boundaries=["Manual baseline adjustment alone"],
        gold_findings=[
            {
                "gold_finding_id": "gold_pkg_high_validation",
                "expected_risk_category": "method_validation",
                "expected_severity": "high",
                "expected_requirement_ids": ["req_eval_batch_impact"],
                "must_detect": True,
                "should_block_auto_clear": True,
            },
            {
                "gold_finding_id": "gold_pkg_critical_approval",
                "expected_risk_category": "qa_approval",
                "expected_severity": "critical",
                "expected_requirement_ids": ["req_eval_qa_approval"],
                "must_detect": True,
                "should_block_auto_clear": True,
            },
        ],
    )

    report = EvalRunner().evaluate(
        dataset=dataset,
        system_findings=[
            _finding(
                finding_id="finding_pkg_validation",
                risk_category="method_validation",
                severity="high",
                requirement_references=["req_eval_batch_impact"],
                quote="The new limit is not covered by the current validation.",
            ),
            _finding(
                finding_id="finding_pkg_validation_duplicate",
                risk_category="method_validation",
                severity="high",
                requirement_references=["req_eval_batch_impact"],
                quote="The new limit is not covered by the current validation.",
            ),
            _finding(
                finding_id="finding_pkg_approval_undercalled",
                risk_category="qa_approval",
                severity="high",
                requirement_references=["req_eval_qa_approval"],
                quote="QA approval is not documented before use.",
            ),
            _finding(
                finding_id="finding_pkg_unsupported_high",
                risk_category="unrelated_claim",
                severity="high",
                requirement_references=[],
                quote="Unsupported high claim.",
                evidence_support="weak",
            ),
            _finding(
                finding_id="finding_pkg_boundary_violation",
                risk_category="unrelated_claim",
                severity="medium",
                requirement_references=[],
                quote="Manual baseline adjustment alone is a deviation.",
            ),
        ],
        risk_decision=_risk_decision(decision="human_review_required", auto_clear=False),
    )

    assert report.metrics.must_detect_recall == 1.0
    assert report.metrics.duplicate_finding_count == 1
    assert report.metrics.duplicate_finding_rate == 0.5
    assert report.metrics.unsupported_finding_rate == 0.2
    assert report.metrics.unsupported_high_critical_published_count == 1
    assert report.metrics.false_positive_boundary_violation_count == 1
    assert report.metrics.severity_exact_count == 1
    assert report.metrics.severity_undercall_count == 1
    assert report.metrics.high_or_critical_undercall_count == 1
    assert report.metrics.severity_overcall_count == 0
    assert report.false_positive_finding_ids == [
        "finding_pkg_unsupported_high",
        "finding_pkg_boundary_violation",
    ]


def test_auto_clear_with_any_blocking_gold_finding_fails_eval() -> None:
    dataset = EvalDataset(
        dataset_id="evalds_blocking_medium",
        name="Blocking medium gold",
        version="2026.1",
        document_type="deviation",
        process_area="aseptic_filling",
        gold_findings=[
            {
                "gold_finding_id": "gold_blocking_medium",
                "expected_risk_category": "batch_impact_assessment",
                "expected_severity": "medium",
                "expected_requirement_ids": ["req_eval_batch_impact"],
                "must_detect": True,
                "should_block_auto_clear": True,
            }
        ],
    )

    report = EvalRunner().evaluate(
        dataset=dataset,
        system_findings=[],
        risk_decision=_risk_decision(decision="auto_clear_candidate", auto_clear=True),
    )

    assert report.metrics.auto_clear_false_negative_count == 1
    assert any("blocking gold finding" in failure for failure in report.failures)


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
    evidence_support: str = "strong",
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
        "evidence_support": evidence_support,
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
