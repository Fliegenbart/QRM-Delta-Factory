from __future__ import annotations

import re
from pathlib import Path

from app.evals.run_goldstandard import (
    _load_post_run_oracle,
    _match_error,
    _package_document_paths,
    _package_metadata,
    _package_mode_exit_code,
    _package_release_gate,
    _review_pack_risks_as_findings,
    _score_visible_review_pack_errors,
    _wait_for_pipeline_completion,
)

PKG001_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "pkg001"
PKG001_DOCUMENT_FILES = {
    "CC-SYN-001": "change_control.md",
    "SOP-QC-AN-014-EX": "sop_excerpt.md",
    "VE-SYN-001": "validation_or_test_evidence.md",
    "RA-SYN-001": "baseline_risk_assessment.md",
    "BR-SYN-001": "batch_record_or_execution_record.md",
}


def test_pkg001_normalizes_package_metadata_for_pipeline_scope() -> None:
    metadata = _package_metadata(PKG001_FIXTURE_DIR)

    assert metadata == {
        "declared_document_type": "change_control_package",
        "declared_process_area": "qc_lab",
    }


def test_pkg001_oracle_preserves_themes_and_evidence_references() -> None:
    oracle = _load_post_run_oracle(PKG001_FIXTURE_DIR / "GOLD_STANDARD.json")

    first_finding = oracle["errors"][0]
    assert first_finding["expected_requirement_theme"] == (
        "Fitness for intended use after tightened quantitative limit"
    )
    assert first_finding["expected_evidence_refs"] == [
        {
            "document_id": "CC-SYN-001",
            "page_or_section": "Abschnitt 1",
            "quote": "von NMT 0,20 % auf NMT 0,10 % abgesenkt",
        },
        {
            "document_id": "SOP-QC-AN-014-EX",
            "page_or_section": "Abschnitt 5.1",
            "quote": "muss die Methodenfitness am neuen Grenzwert dokumentiert werden",
        },
        {
            "document_id": "VE-SYN-001",
            "page_or_section": "Abschnitt 2",
            "quote": "UPLC-12 am Standort BRX-3 war nicht Teil des ursprünglichen Protokolls",
        },
        {
            "document_id": "VE-SYN-001",
            "page_or_section": "Abschnitt 3",
            "quote": (
                "Für 0,10 % wurde keine separate Genauigkeits- oder "
                "Präzisionsstufe durchgeführt"
            ),
        },
    ]


def test_pkg001_all_expected_evidence_quotes_are_literal_source_excerpts() -> None:
    oracle = _load_post_run_oracle(PKG001_FIXTURE_DIR / "GOLD_STANDARD.json")

    for error in oracle["errors"]:
        for ref in error["expected_evidence_refs"]:
            source_path = PKG001_FIXTURE_DIR / PKG001_DOCUMENT_FILES[ref["document_id"]]
            source_text = source_path.read_text(encoding="utf-8")
            assert _normalize_literal_source(ref["quote"]) in _normalize_literal_source(
                source_text
            ), f"{error['error_id']} quote is not literal in {source_path.name}"


def test_pkg001_release_gate_requires_all_blocking_findings_in_visible_review_pack() -> None:
    oracle = _load_post_run_oracle(PKG001_FIXTURE_DIR / "GOLD_STANDARD.json")
    visible_findings = _visible_findings_for(oracle["errors"])

    matched, missed = _score_visible_review_pack_errors(oracle, visible_findings)
    gate = _package_release_gate(
        [
            {
                "case_id": "PKG-001",
                "review_pack_matched_errors": matched,
                "review_pack_missed_errors": missed,
            }
        ]
    )

    assert len(matched) == 5
    assert missed == []
    assert gate == {"passed": True, "missed_blocking_findings": []}


def test_pkg001_release_gate_rejects_generic_hint_and_ignores_raw_internal_findings() -> None:
    oracle = _load_post_run_oracle(PKG001_FIXTURE_DIR / "GOLD_STANDARD.json")
    visible_findings = _visible_findings_for(oracle["errors"])
    visible_findings[0] = {
        "finding_id": "finding_generic_limit_hint",
        "risk_statement": "Der neue Grenzwert sollte geprüft werden.",
        "severity": "high",
        "verifier_status": "strong",
        "evidence_items": [
            {
                "quote": oracle["errors"][0]["expected_evidence_refs"][0]["quote"],
            }
        ],
    }
    raw_internal_findings = _visible_findings_for(oracle["errors"])

    matched, missed = _score_visible_review_pack_errors(oracle, visible_findings)
    gate = _package_release_gate(
        [
            {
                "case_id": "PKG-001",
                "raw_internal_findings": raw_internal_findings,
                "review_pack_matched_errors": matched,
                "review_pack_missed_errors": missed,
            }
        ]
    )

    assert len(matched) == 4
    assert [record["error_id"] for record in missed] == ["PKG001-F01"]
    assert gate == {
        "passed": False,
        "missed_blocking_findings": [
            {
                "case_id": "PKG-001",
                "error_id": "PKG001-F01",
                "severity": "high",
                "expected_reviewer_finding": (
                    "Die alte Validierung deckt die Entscheidung am neuen Grenzwert von "
                    "NMT 0,10 % und die aktuelle UPLC-12-Routineplattform nicht "
                    "ausreichend ab."
                ),
            }
        ],
    }
    assert _package_mode_exit_code(gate) == 1


def test_pkg001_release_gate_rejects_semantically_exact_partial_visible_hint() -> None:
    oracle = _load_post_run_oracle(PKG001_FIXTURE_DIR / "GOLD_STANDARD.json")
    visible_findings = _visible_findings_for(oracle["errors"])
    visible_findings[0]["verifier_status"] = "partial"

    matched, missed = _score_visible_review_pack_errors(oracle, visible_findings)
    gate = _package_release_gate(
        [
            {
                "case_id": "PKG-001",
                "review_pack_matched_errors": matched,
                "review_pack_missed_errors": missed,
            }
        ]
    )

    assert len(matched) == 4
    assert [record["error_id"] for record in missed] == ["PKG001-F01"]
    assert _package_mode_exit_code(gate) == 1


def test_pkg001_upload_manifest_excludes_oracle_and_answer_keys(tmp_path: Path) -> None:
    package_dir = tmp_path / "PKG-001"
    package_dir.mkdir()
    for name in [
        "change_control.md",
        "validation_or_test_evidence.md",
        "GOLD_STANDARD.json",
        "hidden_errors_answer_key.json",
    ]:
        (package_dir / name).write_text("fixture", encoding="utf-8")

    assert [path.name for path in _package_document_paths(package_dir)] == [
        "change_control.md",
        "validation_or_test_evidence.md",
    ]


def test_harness_polls_202_pipeline_run_until_terminal() -> None:
    client = _PipelineClient(
        get_payloads=[
            {"status": "running"},
            {"status": "needs_human_review", "model_manifest": []},
        ]
    )

    completed = _wait_for_pipeline_completion(
        client,
        {"pipeline_run_id": "prun_pkg001", "status": "running"},
        poll_interval_seconds=0,
        timeout_seconds=1,
    )

    assert completed["status"] == "needs_human_review"
    assert client.requested_paths == [
        "/pipeline-runs/prun_pkg001",
        "/pipeline-runs/prun_pkg001",
    ]


def test_review_pack_risks_are_scoreable_against_pkg001_oracle() -> None:
    risks = [
        {
            "finding_id": "risk_training_gap",
            "risk_statement": "SOP v4 was effective before training completion was evidenced.",
            "severity": "medium",
            "verifier_status": "strong",
            "requirement_references": ["req_qc_training_before_effective_sop_use"],
            "evidence_quotes": [
                {
                    "document_id": "doc_training",
                    "chunk_id": "chunk_training_1",
                    "page": 3,
                    "quote": "Training matrix lists SOP v4 as not completed before effective use.",
                    "support_type": "supports",
                }
            ],
        }
    ]

    scoreable = _review_pack_risks_as_findings(risks)

    assert scoreable[0]["verifier_status"] == "strong"

    assert _match_error(
        {
            "error_id": "PKG001-TRAINING",
            "severity": "medium",
            "expected_reviewer_finding": (
                "Training for SOP v4 was not completed before effective use."
            ),
            "why_it_is_a_problem": "Training must precede GMP use.",
            "exact_evidence_text": (
                "Training matrix lists SOP v4 as not completed before effective use."
            ),
        },
        scoreable,
    )


def _visible_findings_for(errors: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "finding_id": f"finding_{error['error_id']}",
            "risk_statement": error["expected_reviewer_finding"],
            "severity": error["severity"],
            "verifier_status": "strong",
            "evidence_items": [
                {"quote": ref["quote"]}
                for ref in error["expected_evidence_refs"]
            ],
        }
        for error in errors
    ]


def _normalize_literal_source(text: str) -> str:
    """Ignore Markdown and whitespace, while preserving source punctuation."""
    return " ".join(re.sub(r"[*_`#>|]", "", text).split())


class _PipelineResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.status_code = 200
        self._payload = payload
        self.text = ""

    def json(self) -> dict[str, object]:
        return self._payload


class _PipelineClient:
    def __init__(self, *, get_payloads: list[dict[str, object]]) -> None:
        self.get_payloads = get_payloads
        self.requested_paths: list[str] = []

    def get(self, path: str) -> _PipelineResponse:
        self.requested_paths.append(path)
        return _PipelineResponse(self.get_payloads.pop(0))
