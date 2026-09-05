from __future__ import annotations

import json
from pathlib import Path

from app.evals.export_demo_cases import _name_cited_documents, export_case


def _case_dir(tmp_path: Path) -> Path:
    case_dir = tmp_path / "case_01"
    case_dir.mkdir()
    (case_dir / "case_summary.md").write_text(
        "# Fall\n- **Produkt:** Xylocortin 20mg\n- **Darreichungsform:** Salbe\n"
        "- **Betroffene Charge:** XYL-2026-004A\n",
        encoding="utf-8",
    )
    (case_dir / "document_01_deviation_report.md").write_text(
        "# Abweichungsbericht\nDie Manteltemperatur sank auf 34,2 °C.\n", encoding="utf-8"
    )
    (case_dir / "document_03_capa_plan.md").write_text(
        "# CAPA\nNachschulung des Operators bis 30.04.2026.\n", encoding="utf-8"
    )
    return case_dir


def _report() -> dict:
    return {
        "engine_version": "requirement-review-v0.2",
        "verdicts": [
            {
                "requirement_id": "req_a",
                "published_status": "violated",
                "evidence": [
                    {"document_id": "doc_1", "chunk_id": "c1", "page": 1, "quote": "sank auf 34,2 °C"},
                    {"document_id": "doc_3", "chunk_id": "c3", "page": 1, "quote": "Nachschulung des Operators"},
                    # Present in no file: stays unnamed rather than guessed.
                    {"document_id": "doc_9", "chunk_id": "c9", "page": 1, "quote": "nirgends zu finden"},
                ],
            }
        ],
        "model_calls": [
            {"status": "succeeded", "input_tokens": 10, "output_tokens": 2},
            {"status": "failed", "input_tokens": 5, "output_tokens": 0},
        ],
    }


def test_cited_documents_are_named_from_their_quotes(tmp_path: Path) -> None:
    report = _report()
    unnamed = _name_cited_documents(report, _case_dir(tmp_path))

    names = [item.get("document_name") for item in report["verdicts"][0]["evidence"]]
    assert names == ["document_01_deviation_report.md", "document_03_capa_plan.md", None]
    assert unnamed == 1


def test_export_case_carries_provenance_and_totals(tmp_path: Path) -> None:
    payload = export_case(
        run={"started_at": "2026-08-23T11:23:40+00:00", "stack": "hetzner", "assessor_mode": "narrow", "hetzner_model": "Qwen3.8-27B"},
        case_result={
            "requirement_report": _report(),
            "pipeline_status": "completed",
            "gold_error_count": 2,
            "matched_errors": [{"error_id": "ERR_01_01"}, {"error_id": "ERR_01_02"}],
            "decoy_count": 1,
            "decoys_passed": [{"decoy_id": "DEC_01_01"}],
        },
        case_dir=_case_dir(tmp_path),
    )

    assert payload["slug"] == "xylocortin-temperatur"
    assert payload["product"] == "Xylocortin 20mg"
    assert [d["label"] for d in payload["documents"]] == [
        "Fall-Zusammenfassung",
        "Abweichungsbericht",
        "CAPA-Plan",
    ]
    assert payload["run"]["model"] == "Qwen3.8-27B"
    assert payload["run"]["model_calls"] == 2
    assert payload["run"]["failed_model_calls"] == 1
    assert payload["run"]["input_tokens"] == 15
    assert payload["gold"] == {"planted": 2, "found": 2, "decoys": 1, "decoys_passed": 1}
    # Call-level rows are operator material and do not ship with the demo.
    assert payload["report"]["model_calls"] == []
    json.dumps(payload)  # serialisable as written
