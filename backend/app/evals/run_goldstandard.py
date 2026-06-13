"""Ringversuch harness: run goldstandard_pharmaqrm cases through the full pipeline.

Ingests each synthetic gold-standard case (4 German GMP documents), runs the
backend pipeline (claim ledger -> primary multi-agent review -> evidence
verification -> adversarial review -> risk fusion), then scores the resulting
findings against the case's hidden_errors_answer_key.json, including the
non-error decoys for the specificity side.

Usage (from backend/):
    .venv/bin/python -m app.evals.run_goldstandard --mode mock
    .venv/bin/python -m app.evals.run_goldstandard --mode live --cases case_01 case_02

Live mode requires QRM_ANTHROPIC_API_KEY and QRM_OPENAI_API_KEY in the
environment (the script maps them from ANTHROPIC_API_KEY/OPENAI_API_KEY in a
repo-root .env if present).
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent
DEFAULT_CASES_DIR = REPO_ROOT / "goldstandard_pharmaqrm"
DEFAULT_OUTPUT_DIR = DEFAULT_CASES_DIR / "runs"

PROCESS_AREA = "drug_product_manufacturing"
DOCUMENT_TYPE = "deviation"
TENANT_ID = "tenant_goldstandard_pharmaqrm"
REQUIREMENT_SET_ID = "rset_goldstandard_gmp_2026_1"


def _load_dotenv_keys() -> None:
    """Map legacy root .env provider keys onto the QRM_* names the backend expects."""
    env_path = REPO_ROOT / ".env"
    values: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"').strip("'")
    for source, target in [
        ("ANTHROPIC_API_KEY", "QRM_ANTHROPIC_API_KEY"),
        ("OPENAI_API_KEY", "QRM_OPENAI_API_KEY"),
        ("GEMINI_API_KEY", "QRM_GEMINI_API_KEY"),
        ("MISTRAL_API_KEY", "QRM_MISTRAL_API_KEY"),
    ]:
        if target not in os.environ:
            value = os.environ.get(source) or values.get(source, "")
            if value:
                os.environ[target] = value


def _configure_environment(
    mode: str,
    stack: str,
    anthropic_model: str,
    openai_model: str,
    mistral_model: str,
) -> None:
    if mode == "live":
        _load_dotenv_keys()
        os.environ["QRM_EXTERNAL_MODEL_CALLS_ENABLED"] = "true"
        os.environ.setdefault("QRM_MODEL_PROVIDER_TIMEOUT_SECONDS", "240")
        os.environ.setdefault("QRM_MODEL_PROVIDER_MAX_RETRIES", "2")
        if stack == "eu":
            os.environ["QRM_ALLOWED_MODEL_PROVIDERS"] = "mistral,mock"
            os.environ["QRM_REVIEWER_PROVIDER_OVERRIDE"] = "mistral"
            os.environ["QRM_MISTRAL_MODEL_ID"] = mistral_model
            os.environ.pop("QRM_CRITIC_PROVIDERS", None)
        elif stack == "hybrid":
            os.environ["QRM_ALLOWED_MODEL_PROVIDERS"] = "mistral,anthropic,openai,mock"
            os.environ["QRM_REVIEWER_PROVIDER_OVERRIDE"] = "mistral"
            os.environ["QRM_CRITIC_PROVIDERS"] = "anthropic,openai"
            os.environ["QRM_MISTRAL_MODEL_ID"] = mistral_model
            os.environ["QRM_ANTHROPIC_MODEL_ID"] = anthropic_model
            os.environ["QRM_OPENAI_MODEL_ID"] = openai_model
        else:
            os.environ["QRM_ALLOWED_MODEL_PROVIDERS"] = "anthropic,openai,mock"
            os.environ.pop("QRM_REVIEWER_PROVIDER_OVERRIDE", None)
            os.environ.pop("QRM_CRITIC_PROVIDERS", None)
            os.environ["QRM_ANTHROPIC_MODEL_ID"] = anthropic_model
            os.environ["QRM_OPENAI_MODEL_ID"] = openai_model
    else:
        os.environ["QRM_EXTERNAL_MODEL_CALLS_ENABLED"] = "false"
        os.environ["QRM_ALLOWED_MODEL_PROVIDERS"] = "mock"


def _requirement_set() -> dict[str, Any]:
    """Load the canonical general GMP library, scoped to the harness tenant.

    Benchmark and production check against the SAME requirement library
    (src/data/gmp-general-requirement-library.json); only the set id and
    tenant are overridden so the harness stays self-contained.
    """
    library_path = REPO_ROOT / "src" / "data" / "gmp-general-requirement-library.json"
    library: dict[str, Any] = json.loads(library_path.read_text(encoding="utf-8"))
    library["requirement_set_id"] = REQUIREMENT_SET_ID
    library["tenant_id"] = TENANT_ID
    library["imported_at"] = datetime.now(UTC).isoformat()
    library["imported_by"] = "user_goldstandard_harness"
    library["active"] = True
    return library


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[\s ]+", " ", text)
    text = re.sub(r"[*_`#>|]", "", text)
    return text.strip()


def _token_set(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9äöüß]+", _normalize(text)) if len(token) > 2}


def _jaccard(a: str, b: str) -> float:
    ta, tb = _token_set(a), _token_set(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def _finding_texts(finding: dict[str, Any]) -> list[str]:
    texts = [finding.get("risk_statement", ""), finding.get("recommended_action", "")]
    texts.extend(finding.get("missing_information", []) or [])
    for item in finding.get("evidence_items", []) or []:
        texts.append(item.get("quote", ""))
    return [t for t in texts if t]


def _match_error(gold: dict[str, Any], findings: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return best matching finding for a gold error, or None."""
    gold_evidence = gold.get("exact_evidence_text", "")
    gold_expected = gold.get("expected_reviewer_finding", "")
    gold_why = gold.get("why_it_is_a_problem", "")
    best: tuple[float, dict[str, Any], str] | None = None
    for finding in findings:
        score = 0.0
        method = ""
        norm_gold_ev = _normalize(gold_evidence)
        for text in _finding_texts(finding):
            norm_text = _normalize(text)
            if norm_gold_ev and (norm_gold_ev in norm_text or norm_text in norm_gold_ev):
                score = max(score, 1.0)
                method = "evidence_substring"
                continue
            ev_score = max(_jaccard(gold_evidence, text), _similarity(gold_evidence, text))
            sem_score = max(
                _jaccard(gold_expected, text),
                _jaccard(gold_why, text),
            )
            if ev_score > score:
                score, method = ev_score, "evidence_fuzzy"
            if sem_score > score:
                score, method = sem_score, "semantic_overlap"
        if score >= 0.40 and (best is None or score > best[0]):
            best = (score, finding, method)
    if best is None:
        return None
    return {
        "score": round(best[0], 3),
        "method": best[2],
        "finding_id": best[1].get("finding_id"),
        "risk_statement": best[1].get("risk_statement"),
        "severity": best[1].get("severity"),
    }


def _match_decoy(decoy: dict[str, Any], findings: list[dict[str, Any]]) -> dict[str, Any] | None:
    """A decoy counts as a false alarm if a finding is squarely about the decoy text."""
    decoy_text = decoy.get("evidence_text", "")
    norm_decoy = _normalize(decoy_text)
    for finding in findings:
        for item in finding.get("evidence_items", []) or []:
            quote = _normalize(item.get("quote", ""))
            if not quote:
                continue
            if norm_decoy and (norm_decoy in quote or quote in norm_decoy):
                statement = finding.get("risk_statement", "")
                is_about_decoy = (
                    _jaccard(decoy_text, statement) > 0.2
                    or _similarity(decoy_text, statement) > 0.3
                )
                if is_about_decoy:
                    return {
                        "finding_id": finding.get("finding_id"),
                        "risk_statement": statement,
                        "severity": finding.get("severity"),
                    }
    return None


def run_case(client: Any, repository: Any, case_dir: Path) -> dict[str, Any]:
    answer_key_path = case_dir / "hidden_errors_answer_key.json"
    answer_key = json.loads(answer_key_path.read_text(encoding="utf-8"))
    case_id = answer_key["case_id"]

    create_response = client.post(
        "/document-sets",
        json={
            "tenant_id": TENANT_ID,
            "requirement_set_id": REQUIREMENT_SET_ID,
            "declared_document_type": DOCUMENT_TYPE,
            "declared_process_area": PROCESS_AREA,
            "uploaded_by": "user_goldstandard_harness",
        },
    )
    create_response.raise_for_status() if hasattr(create_response, "raise_for_status") else None
    if create_response.status_code != 201:
        raise RuntimeError(f"{case_id}: document set creation failed: {create_response.text}")
    document_set_id = create_response.json()["document_set_id"]

    uploaded = []
    for doc_path in sorted(case_dir.glob("document_*.md")):
        upload = client.post(
            f"/document-sets/{document_set_id}/documents",
            files={"file": (doc_path.name, doc_path.read_bytes(), "text/markdown")},
            data={"uploaded_by": "user_goldstandard_harness"},
        )
        if upload.status_code != 201:
            raise RuntimeError(f"{case_id}: upload of {doc_path.name} failed: {upload.text}")
        uploaded.append(doc_path.name)

    pipeline_response = client.post(f"/document-sets/{document_set_id}/pipeline-runs")
    if pipeline_response.status_code != 201:
        raise RuntimeError(f"{case_id}: pipeline run failed: {pipeline_response.text}")
    pipeline_payload = pipeline_response.json()

    claims = repository.list_claims(document_set_id)
    fusion_findings = repository.list_risk_fusion_findings(document_set_id)
    primary_findings = repository.list_risk_findings(document_set_id)
    findings_models = fusion_findings or primary_findings
    findings = [finding.model_dump(mode="json") for finding in findings_models]
    decision = repository.get_latest_risk_decision(document_set_id)

    matched: list[dict[str, Any]] = []
    missed: list[dict[str, Any]] = []
    for gold in answer_key.get("errors", []):
        match = _match_error(gold, findings)
        record = {
            "error_id": gold["error_id"],
            "severity": gold.get("severity"),
            "error_type": gold.get("error_type"),
            "expected_reviewer_finding": gold.get("expected_reviewer_finding"),
            "match": match,
        }
        (matched if match else missed).append(record)

    decoy_hits: list[dict[str, Any]] = []
    decoys_passed: list[dict[str, Any]] = []
    for decoy in answer_key.get("non_error_decoys", []):
        hit = _match_decoy(decoy, findings)
        record = {
            "decoy_id": decoy["decoy_id"],
            "evidence_text": decoy.get("evidence_text"),
            "hit": hit,
        }
        (decoy_hits if hit else decoys_passed).append(record)

    matched_finding_ids = {
        record["match"]["finding_id"] for record in matched if record["match"]
    }
    unmatched_findings = [
        {
            "finding_id": finding.get("finding_id"),
            "severity": finding.get("severity"),
            "risk_statement": finding.get("risk_statement"),
        }
        for finding in findings
        if finding.get("finding_id") not in matched_finding_ids
    ]

    verified = [
        finding
        for finding in findings
        if (finding.get("verification_result") or {}).get("quote_matches_chunk")
    ]

    model_statuses = {
        entry.get("agent_role"): entry.get("status")
        for entry in pipeline_payload.get("model_manifest", [])
    }

    tokens_by_provider: dict[str, dict[str, int]] = {}

    def _add_tokens(provider: str, usage: dict[str, Any]) -> None:
        bucket = tokens_by_provider.setdefault(
            provider, {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "calls": 0}
        )
        bucket["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
        bucket["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
        bucket["total_tokens"] += int(usage.get("total_tokens", 0) or 0)
        bucket["calls"] += 1

    for model_run in repository.list_model_runs(document_set_id):
        _add_tokens(model_run.provider, model_run.token_usage.model_dump())
    from app.audit.events import audit_log as _audit_log

    for event in _audit_log.list_events():
        if (
            event.event_type == "claims_extracted"
            and event.entity_id == document_set_id
            and isinstance(event.payload.get("llm_usage"), dict)
        ):
            usage = event.payload["llm_usage"]
            _add_tokens(
                f"extraction:{event.payload.get('extractor_provider', 'unknown')}",
                {
                    "input_tokens": usage.get("input", 0),
                    "output_tokens": usage.get("output", 0),
                    "total_tokens": usage.get("total", 0),
                },
            )

    return {
        "case_id": case_id,
        "document_set_id": document_set_id,
        "documents_uploaded": uploaded,
        "pipeline_status": pipeline_payload.get("status"),
        "failed_step": pipeline_payload.get("failed_step"),
        "error_summary": pipeline_payload.get("error_summary"),
        "tokens_by_provider": tokens_by_provider,
        "model_statuses": model_statuses,
        "failed_model_roles": sorted(
            role for role, status in model_statuses.items() if status and status != "succeeded"
        ),
        "claim_count": len(claims),
        "finding_count": len(findings),
        "citation_verified_finding_count": len(verified),
        "risk_decision": getattr(decision, "decision", None),
        "auto_clear_allowed": getattr(decision, "auto_clear_allowed", None),
        "gold_error_count": len(answer_key.get("errors", [])),
        "matched_errors": matched,
        "missed_errors": missed,
        "decoy_count": len(answer_key.get("non_error_decoys", [])),
        "decoy_false_alarms": decoy_hits,
        "decoys_passed": decoys_passed,
        "unmatched_findings": unmatched_findings,
    }


def _aggregate(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    total_errors = sum(case["gold_error_count"] for case in case_results)
    total_matched = sum(len(case["matched_errors"]) for case in case_results)
    total_decoys = sum(case["decoy_count"] for case in case_results)
    total_decoy_hits = sum(len(case["decoy_false_alarms"]) for case in case_results)
    total_findings = sum(case["finding_count"] for case in case_results)
    total_verified = sum(case["citation_verified_finding_count"] for case in case_results)
    tokens: dict[str, dict[str, int]] = {}
    for case in case_results:
        for provider, usage in (case.get("tokens_by_provider") or {}).items():
            bucket = tokens.setdefault(
                provider, {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "calls": 0}
            )
            for key in bucket:
                bucket[key] += usage.get(key, 0)
    return {
        "tokens_by_provider": tokens,
        "cases": len(case_results),
        "sensitivity": {
            "found": total_matched,
            "total": total_errors,
            "rate": round(total_matched / total_errors, 3) if total_errors else None,
        },
        "specificity_decoys": {
            "passed": total_decoys - total_decoy_hits,
            "total": total_decoys,
            "rate": round((total_decoys - total_decoy_hits) / total_decoys, 3)
            if total_decoys
            else None,
        },
        "citation_precision": {
            "verified": total_verified,
            "total_findings": total_findings,
            "rate": round(total_verified / total_findings, 3) if total_findings else None,
        },
    }


def _render_markdown(
    run_meta: dict[str, Any],
    aggregate: dict[str, Any],
    case_results: list[dict[str, Any]],
) -> str:
    lines = [
        "# Ringversuch-Report: Goldstandard PharmaQRM",
        "",
        f"- Modus: `{run_meta['mode']}` | Stack: `{run_meta.get('stack') or '-'}`",
        f"- Zeitpunkt: {run_meta['started_at']}",
        f"- Anthropic-Modell: `{run_meta.get('anthropic_model') or '-'}`",
        f"- OpenAI-Modell: `{run_meta.get('openai_model') or '-'}`",
        f"- Mistral-Modell: `{run_meta.get('mistral_model') or '-'}`",
        "",
        "## Gesamtergebnis",
        "",
    ]
    sens = aggregate["sensitivity"]
    spec = aggregate["specificity_decoys"]
    cite = aggregate["citation_precision"]
    lines.append(
        f"- **Sensitivität:** {sens['found']} von {sens['total']} versteckten Fehlern gefunden"
        + (f" ({sens['rate']:.0%})" if sens["rate"] is not None else "")
    )
    lines.append(
        f"- **Spezifität (Decoys):** {spec['passed']} von {spec['total']} Decoys korrekt"
        " nicht beanstandet"
        + (f" ({spec['rate']:.0%})" if spec["rate"] is not None else "")
    )
    lines.append(
        f"- **Belegtreue:** {cite['verified']} von {cite['total_findings']} Findings mit"
        " verifiziertem Zitat"
        + (f" ({cite['rate']:.0%})" if cite["rate"] is not None else "")
    )
    if aggregate.get("tokens_by_provider"):
        lines.append("")
        lines.append("## Token-Verbrauch")
        lines.append("")
        lines.append("| Provider | Calls | Input | Output | Total |")
        lines.append("|---|---|---|---|---|")
        for provider, usage in sorted(aggregate["tokens_by_provider"].items()):
            lines.append(
                f"| {provider} | {usage['calls']} | {usage['input_tokens']:,} "
                f"| {usage['output_tokens']:,} | {usage['total_tokens']:,} |"
            )
    lines.append("")
    lines.append("## Fälle")
    lines.append("")
    lines.append(
        "| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for case in case_results:
        lines.append(
            f"| {case['case_id']} | {case['pipeline_status']} | {case['claim_count']} "
            f"| {case['finding_count']} | {len(case['matched_errors'])}/{case['gold_error_count']} "
            f"| {len(case['decoy_false_alarms'])}/{case['decoy_count']} "
            f"| {case['risk_decision'] or '-'} |"
        )
    lines.append("")
    for case in case_results:
        lines.append(f"### {case['case_id']}")
        lines.append("")
        for record in case["matched_errors"]:
            match = record["match"]
            lines.append(
                f"- ✅ `{record['error_id']}` ({record['severity']}) — gefunden"
                f" via {match['method']} (Score {match['score']}):"
                f" {match['risk_statement']}"
            )
        for record in case["missed_errors"]:
            lines.append(
                f"- ❌ `{record['error_id']}` ({record['severity']}) — übersehen:"
                f" {record['expected_reviewer_finding']}"
            )
        for record in case["decoy_false_alarms"]:
            lines.append(
                f"- ⚠️ Decoy `{record['decoy_id']}` fälschlich beanstandet:"
                f" {record['hit']['risk_statement']}"
            )
        if case["unmatched_findings"]:
            lines.append(
                f"- ℹ️ {len(case['unmatched_findings'])} weitere Findings ohne"
                " Gold-Zuordnung (manuell prüfen)"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run goldstandard cases through the pipeline.")
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
    parser.add_argument(
        "--stack",
        choices=["frontier", "eu", "hybrid"],
        default="frontier",
        help="frontier = Anthropic+OpenAI per role mix; eu = Mistral for everything;"
        " hybrid = Mistral main reviewers + Anthropic/OpenAI red-team critics.",
    )
    parser.add_argument("--cases", nargs="*", help="Subset of case dir names, e.g. case_01")
    parser.add_argument("--cases-dir", default=str(DEFAULT_CASES_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--anthropic-model", default="claude-sonnet-4-6")
    parser.add_argument("--openai-model", default="gpt-5.4")
    parser.add_argument("--mistral-model", default="mistral-large-latest")
    args = parser.parse_args(argv)

    _configure_environment(
        args.mode, args.stack, args.anthropic_model, args.openai_model, args.mistral_model
    )

    # Imports happen after env setup because get_settings() is lru_cached.
    from fastapi.testclient import TestClient

    from app.audit.events import audit_log
    from app.core.config import get_settings
    from app.db.in_memory import repository
    from app.main import app
    from app.schemas.domain import RequirementSet

    get_settings.cache_clear()
    repository.reset()
    audit_log.clear()

    repository.create_requirement_set(RequirementSet.model_validate(_requirement_set()))
    client = TestClient(app)

    cases_dir = Path(args.cases_dir)
    case_dirs = sorted(
        path
        for path in cases_dir.iterdir()
        if path.is_dir() and path.name.startswith("case_")
        and (not args.cases or path.name in args.cases)
    )
    if not case_dirs:
        print(f"No case directories found in {cases_dir}", file=sys.stderr)
        return 1

    started_at = datetime.now(UTC)
    live = args.mode == "live"
    uses_anthropic_openai = live and args.stack in ("frontier", "hybrid")
    uses_mistral = live and args.stack in ("eu", "hybrid")
    run_meta = {
        "mode": args.mode,
        "stack": args.stack if live else None,
        "started_at": started_at.isoformat(timespec="seconds"),
        "anthropic_model": args.anthropic_model if uses_anthropic_openai else None,
        "openai_model": args.openai_model if uses_anthropic_openai else None,
        "mistral_model": args.mistral_model if uses_mistral else None,
        "case_count": len(case_dirs),
    }

    case_results = []
    for index, case_dir in enumerate(case_dirs):
        if args.mode == "live" and index > 0:
            time.sleep(30)
        print(f"[{datetime.now(UTC).strftime('%H:%M:%S')}] running {case_dir.name} ...", flush=True)
        try:
            result = run_case(client, repository, case_dir)
        except Exception as exc:  # noqa: BLE001 - report per-case failure, keep going
            result = {
                "case_id": case_dir.name.upper(),
                "pipeline_status": "harness_error",
                "failed_step": None,
                "error": str(exc),
                "claim_count": 0,
                "finding_count": 0,
                "citation_verified_finding_count": 0,
                "risk_decision": None,
                "auto_clear_allowed": None,
                "gold_error_count": 0,
                "matched_errors": [],
                "missed_errors": [],
                "decoy_count": 0,
                "decoy_false_alarms": [],
                "decoys_passed": [],
                "unmatched_findings": [],
            }
        case_results.append(result)
        print(
            f"    -> status={result['pipeline_status']} claims={result['claim_count']}"
            f" findings={result['finding_count']}"
            f" errors_found={len(result['matched_errors'])}/{result['gold_error_count']}",
            flush=True,
        )

    aggregate = _aggregate(case_results)
    run_label = args.mode if args.mode == "mock" else f"{args.mode}_{args.stack}"
    output_dir = Path(args.output_dir) / started_at.strftime(f"%Y%m%d_%H%M%S_{run_label}")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "results.json").write_text(
        json.dumps(
            {"run": run_meta, "aggregate": aggregate, "cases": case_results},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    markdown = _render_markdown(run_meta, aggregate, case_results)
    (output_dir / "report.md").write_text(markdown, encoding="utf-8")
    print()
    print(markdown)
    print(f"\nReports written to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
