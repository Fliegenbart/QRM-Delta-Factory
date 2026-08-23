"""Turn real benchmark output into the example cases the product shows.

The three "Beispiel-Prüfmappen" on the cases page used to be hand-written
fixtures with invented quotes. For a tool whose whole pitch is "every verdict
carries a verbatim quote", a demo that does not is a credibility risk. This
exporter takes a finished goldstandard run -- the same requirement report the
reviewer would see on a real case -- and writes one JSON per case under
src/data/demo-cases/, together with what a prospect needs to read it honestly:
which model ran, when, and how many of the planted errors it found.

    ./.venv/bin/python -m app.evals.export_demo_cases \\
        --run-dir ../goldstandard_pharmaqrm/runs/<run> --cases case_01,case_08,case_09

The documents stay where they are; the demo shows the report, not the files.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent
DEFAULT_CASES_DIR = REPO_ROOT / "goldstandard_pharmaqrm"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "src" / "data" / "demo-cases"

#: Reviewer-facing framing per case. The corpus names a product and a process
#: step; the one-line "what happened" is what a reviewer scans a list by.
CASE_FRAMING: dict[str, dict[str, str]] = {
    "case_01": {
        "slug": "xylocortin-temperatur",
        "title": "Manteltemperatur 45 Minuten unter Spezifikation, Abweichung als „Minor“ eingestuft",
        "area": "Formulierung / Mischen",
        "trigger": "Abweichung",
    },
    "case_08": {
        "slug": "ibuprofen-werkzeugbruch",
        "title": "Werkzeugbruch an der Tablettenpresse, Wiederholungsfehler und CAPA-Termin fraglich",
        "area": "Tablettierung / Pressen",
        "trigger": "Abweichung mit CAPA",
    },
    "case_09": {
        "slug": "cefuroxim-ph-drift",
        "title": "pH-Drift im Bioreaktor, Chargenprotokoll widerspricht dem SCADA-Audit-Trail",
        "area": "Fermentation (Wirkstoffvorstufe)",
        "trigger": "Abweichung mit Change Control",
    },
}

DOCUMENT_LABELS = {
    "deviation_report": "Abweichungsbericht",
    "batch_record_excerpt": "Chargenprotokoll (Auszug)",
    "capa_plan": "CAPA-Plan",
    "quality_approval_note": "QA-Freigabevermerk",
    "change_control": "Change-Control-Antrag",
}


def _summary_fields(case_dir: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in (case_dir / "case_summary.md").read_text(encoding="utf-8").splitlines():
        match = re.match(r"^- \*\*(.+?):\*\*\s*(.+)$", line.strip())
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def _document_label(file_name: str) -> str:
    stem = re.sub(r"^document_\d+_", "", Path(file_name).stem)
    return DOCUMENT_LABELS.get(stem, stem.replace("_", " "))


def _case_documents(case_dir: Path) -> list[dict[str, str]]:
    # The benchmark uploads the case summary with the documents, and the
    # engine cites it like any other file -- so the demo lists it too.
    documents = [{"file_name": "case_summary.md", "label": "Fall-Zusammenfassung"}]
    documents.extend(
        {"file_name": path.name, "label": _document_label(path.name)}
        for path in sorted(case_dir.glob("document_*.md"))
    )
    return documents


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _name_cited_documents(report: dict[str, Any], case_dir: Path) -> int:
    """Recover the file name behind each cited document id.

    Reports written before the engine recorded document names carry only ids.
    Every surviving quote is a grounded substring of exactly one document, so
    the quotes themselves identify the file: a document id is named by the
    file that contains its quotes and no other. Returns how many ids stayed
    unnamed (quotes found in several files, or in none).
    """
    texts = {
        path.name: _normalise(path.read_text(encoding="utf-8"))
        for path in sorted(case_dir.glob("*.md"))
    }
    votes: dict[str, dict[str, int]] = {}
    for verdict in report.get("verdicts", []):
        for item in verdict.get("evidence", []):
            if item.get("document_name"):
                continue
            holders = [name for name, text in texts.items() if _normalise(item["quote"]) in text]
            if len(holders) == 1:
                tally = votes.setdefault(item["document_id"], {})
                tally[holders[0]] = tally.get(holders[0], 0) + 1
    names = {
        document_id: max(tally, key=tally.get)
        for document_id, tally in votes.items()
        if len(tally) == 1
    }
    unnamed: set[str] = set()
    for verdict in report.get("verdicts", []):
        for item in verdict.get("evidence", []):
            if item.get("document_name"):
                continue
            name = names.get(item["document_id"])
            if name is None:
                unnamed.add(item["document_id"])
                continue
            item["document_name"] = name
    return len(unnamed)


def export_case(
    *, run: dict[str, Any], case_result: dict[str, Any], case_dir: Path
) -> dict[str, Any]:
    case_id = case_dir.name
    framing = CASE_FRAMING.get(case_id)
    if framing is None:
        raise SystemExit(f"no framing for {case_id}; add it to CASE_FRAMING")
    summary = _summary_fields(case_dir)
    report = json.loads(json.dumps(case_result["requirement_report"]))
    unnamed = _name_cited_documents(report, case_dir)
    if unnamed:
        print(f"{case_id}: {unnamed} cited document id(s) could not be named from their quotes")
    # Call-level metadata is operator material; the demo shows the totals.
    calls = report.pop("model_calls", [])
    report["model_calls"] = []
    decoys_passed = case_result.get("decoys_passed", 0)
    if isinstance(decoys_passed, list):
        decoys_passed = len(decoys_passed)
    return {
        "id": case_id,
        "slug": framing["slug"],
        "title": framing["title"],
        "area": framing["area"],
        "trigger": framing["trigger"],
        "product": summary.get("Produkt", ""),
        "dosage_form": summary.get("Darreichungsform", ""),
        "batch": summary.get("Betroffene Charge", ""),
        "documents": _case_documents(case_dir),
        "run": {
            "started_at": run.get("started_at"),
            "stack": run.get("stack"),
            "assessor_mode": run.get("assessor_mode"),
            "model": run.get("hetzner_model")
            or run.get("anthropic_model")
            or run.get("openai_model"),
            "engine_version": report.get("engine_version"),
            "pipeline_status": case_result.get("pipeline_status"),
            "model_calls": len(calls),
            "failed_model_calls": sum(1 for c in calls if c.get("status") != "succeeded"),
            "input_tokens": sum(int(c.get("input_tokens") or 0) for c in calls),
            "output_tokens": sum(int(c.get("output_tokens") or 0) for c in calls),
        },
        "gold": {
            "planted": case_result["gold_error_count"],
            "found": len(case_result["matched_errors"]),
            "decoys": case_result.get("decoy_count", 0),
            "decoys_passed": decoys_passed,
        },
        "report": report,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--cases", default=",".join(CASE_FRAMING))
    parser.add_argument("--cases-dir", default=str(DEFAULT_CASES_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args(argv)

    results = json.loads((Path(args.run_dir) / "results.json").read_text(encoding="utf-8"))
    by_case = {entry["case_id"].lower(): entry for entry in results["cases"]}
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for case_id in [c.strip() for c in args.cases.split(",") if c.strip()]:
        case_result = by_case.get(case_id.lower())
        if case_result is None:
            raise SystemExit(f"{case_id} not in {args.run_dir}")
        payload = export_case(
            run=results["run"],
            case_result=case_result,
            case_dir=Path(args.cases_dir) / case_id,
        )
        target = output_dir / f"{case_id}.json"
        target.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        gold = payload["gold"]
        print(f"{case_id}: {gold['found']}/{gold['planted']} planted errors -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
