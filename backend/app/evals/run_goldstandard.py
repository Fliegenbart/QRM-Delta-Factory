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
import tempfile
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Protocol, cast

if TYPE_CHECKING:
    from app.audit.events import AuditService
    from app.db.in_memory import InMemoryDocumentRepository

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent
DEFAULT_CASES_DIR = REPO_ROOT / "goldstandard_pharmaqrm"
DEFAULT_OUTPUT_DIR = DEFAULT_CASES_DIR / "runs"

# The ten suite cases predate per-package declarations and their answer keys
# carry no metadata. Real packages must still declare their own; see
# _package_metadata.
SUITE_DOCUMENT_TYPE = "deviation"
SUITE_PROCESS_AREA = "drug_product_manufacturing"

TENANT_ID = "tenant_goldstandard_pharmaqrm"
REQUIREMENT_SET_ID = "rset_goldstandard_gmp_2026_1"
_TERMINAL_PIPELINE_STATUSES = {"completed", "failed", "needs_human_review"}
_ORACLE_FILENAMES = {"gold_standard.json", "hidden_errors_answer_key.json"}
GOLDSTANDARD_STORAGE_PARENT = Path("/tmp/qrm-goldstandard-documents")
_DOCUMENT_TYPE_ALIASES = {
    "change_control_package": "change_control_package",
}
_PROCESS_AREA_ALIASES = {
    "qc_analytische_freigabeprufung": "qc_lab",
    "quality_control": "quality_control",
}
_CANONICAL_VISIBLE_VERIFIER_STATUSES = {"strong", "verified"}


class _RouteDependencyBindings(Protocol):
    """Mutable route globals intentionally swapped by the isolated harness."""

    repository: InMemoryDocumentRepository
    audit_log: AuditService


def _route_dependency_bindings(module: ModuleType) -> _RouteDependencyBindings:
    """Expose the route's private dependency bindings at this test-only boundary."""
    return cast(_RouteDependencyBindings, module)


def _validate_isolated_harness_environment(
    *,
    persistence_enabled: bool,
    storage_root: Path,
) -> None:
    """Fail closed before a harness can reset any repository state."""
    if persistence_enabled:
        raise ValueError("Goldstandard runner refuses persistent storage")
    root = storage_root.resolve()
    parent = GOLDSTANDARD_STORAGE_PARENT.resolve()
    try:
        root.relative_to(parent)
    except ValueError as exc:
        raise ValueError(
            "Goldstandard runner requires an isolated temporary storage root"
        ) from exc
    if root == parent:
        raise ValueError("Goldstandard runner requires a dedicated temporary storage root")


def _install_isolated_route_bindings() -> tuple[Any, Any, Callable[[], None]]:
    """Bind the harness routes to fresh in-memory state and return a restore hook.

    A caller may have imported the production app before this module. Environment
    changes cannot replace that already-created global repository, so the harness
    explicitly swaps only the route dependencies it invokes and restores them when
    it finishes.
    """
    import app.api.document_sets as document_sets_api
    import app.api.pipeline_runs as pipeline_runs_api
    from app.audit.events import AuditService
    from app.db.in_memory import InMemoryDocumentRepository

    isolated_repository = InMemoryDocumentRepository()
    isolated_audit_log = AuditService()
    document_sets_bindings = _route_dependency_bindings(document_sets_api)
    pipeline_runs_bindings = _route_dependency_bindings(pipeline_runs_api)
    originals = (
        document_sets_bindings.repository,
        document_sets_bindings.audit_log,
        pipeline_runs_bindings.repository,
        pipeline_runs_bindings.audit_log,
    )
    document_sets_bindings.repository = isolated_repository
    document_sets_bindings.audit_log = isolated_audit_log
    pipeline_runs_bindings.repository = isolated_repository
    pipeline_runs_bindings.audit_log = isolated_audit_log

    def restore() -> None:
        (
            document_sets_bindings.repository,
            document_sets_bindings.audit_log,
            pipeline_runs_bindings.repository,
            pipeline_runs_bindings.audit_log,
        ) = originals

    return isolated_repository, isolated_audit_log, restore


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
    # The harness must never read, clear, or append the production snapshot.
    # It calls the ASGI app in a dedicated process, so an in-memory repository
    # and a temporary document root are both sufficient and safer.
    os.environ["QRM_PERSISTENCE_ENABLED"] = "false"
    os.environ["QRM_API_KEYS"] = ""
    os.environ["QRM_LOCAL_STORAGE_ROOT"] = "/tmp/qrm-goldstandard-documents"
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
    library_candidates = [
        REPO_ROOT / "src" / "data" / "gmp-general-requirement-library.json",
        BACKEND_DIR / "src" / "data" / "gmp-general-requirement-library.json",
    ]
    library_path = next((path for path in library_candidates if path.exists()), None)
    if library_path is None:
        raise FileNotFoundError("Canonical GMP requirement library is not packaged")
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


def _normalize_package_metadata_value(value: str, aliases: dict[str, str]) -> str:
    """Turn package metadata labels into stable API values, with taxonomy aliases."""
    transliterated = value.lower().translate(str.maketrans("äöüß", "aous"))
    slug = re.sub(r"[^a-z0-9]+", "_", transliterated).strip("_")
    if not slug:
        raise ValueError("Package metadata value must not be empty")
    return aliases.get(slug, slug)


def _package_metadata(package_dir: Path) -> dict[str, str]:
    """Read the package declaration without ever treating its oracle as an upload.

    A GOLD_STANDARD.json describes a real package and must say what it contains,
    so a missing declaration stays an error there. The suite's own
    hidden_errors_answer_key.json files were written before that contract existed
    and only hold errors and decoys, so they fall back to the suite defaults
    rather than failing every case.
    """
    oracle_path = _oracle_path(package_dir)
    payload: dict[str, Any] = json.loads(oracle_path.read_text(encoding="utf-8"))
    document_type = payload.get("document_type")
    process_area = payload.get("process_area")
    if oracle_path.name == "hidden_errors_answer_key.json":
        if not isinstance(document_type, str):
            document_type = SUITE_DOCUMENT_TYPE
        if not isinstance(process_area, str):
            process_area = SUITE_PROCESS_AREA
    if not isinstance(document_type, str) or not isinstance(process_area, str):
        raise ValueError("Package oracle must declare document_type and process_area")
    return {
        "declared_document_type": _normalize_package_metadata_value(
            document_type, _DOCUMENT_TYPE_ALIASES
        ),
        "declared_process_area": _normalize_package_metadata_value(
            process_area, _PROCESS_AREA_ALIASES
        ),
    }


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


def _review_pack_risks_as_findings(risks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert rendered ReviewPack top-risk cards into finding-like scorer input."""
    scoreable: list[dict[str, Any]] = []
    for risk in risks:
        scoreable.append(
            {
                "finding_id": risk.get("finding_id"),
                "risk_statement": risk.get("risk_statement", ""),
                "severity": risk.get("severity"),
                "verifier_status": risk.get("verifier_status", ""),
                "recommended_action": risk.get("human_review_reason", ""),
                "missing_information": [],
                "requirement_references": risk.get("requirement_references", []),
                "evidence_items": [
                    {
                        "document_id": quote.get("document_id"),
                        "chunk_id": quote.get("chunk_id"),
                        "page": quote.get("page"),
                        "quote": quote.get("quote", ""),
                        "support_type": quote.get("support_type"),
                    }
                    for quote in risk.get("evidence_quotes", []) or []
                ],
            }
        )
    return scoreable


def _score_errors(
    answer_key: dict[str, Any],
    findings: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    matched: list[dict[str, Any]] = []
    missed: list[dict[str, Any]] = []
    for gold in answer_key.get("errors", []):
        match = _match_error(gold, findings)
        record = {
            "error_id": gold["error_id"],
            "severity": gold.get("severity"),
            "error_type": gold.get("error_type"),
            "expected_reviewer_finding": gold.get("expected_reviewer_finding"),
            "should_block_auto_clear": gold.get("should_block_auto_clear", False),
            "match": match,
        }
        (matched if match else missed).append(record)
    return matched, missed


def _package_document_paths(package_dir: Path) -> list[Path]:
    """Return source documents only; evaluation oracles are never pipeline inputs."""
    return [
        path
        for path in sorted(package_dir.iterdir())
        if path.is_file()
        and path.suffix.lower() in {".md", ".txt", ".pdf", ".docx"}
        and path.name.lower() not in _ORACLE_FILENAMES
    ]


def _oracle_path(case_dir: Path) -> Path:
    for filename in ("GOLD_STANDARD.json", "hidden_errors_answer_key.json"):
        path = case_dir / filename
        if path.exists():
            return path
    raise FileNotFoundError(f"No post-run oracle found in {case_dir}")


def _load_post_run_oracle(path: Path) -> dict[str, Any]:
    """Normalize supported oracle formats after the pipeline has completed."""
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if "must_detect_findings" not in payload:
        return payload
    return {
        "case_id": payload["package_id"],
        "errors": [
            {
                "error_id": finding["finding_id"],
                "severity": finding["severity"],
                "error_type": finding.get("risk_category", "gold_finding"),
                "expected_reviewer_finding": finding.get("risk_statement", ""),
                "why_it_is_a_problem": finding.get("why_it_is_hard", ""),
                "exact_evidence_text": "\n".join(
                    ref.get("quote", "")
                    for ref in finding.get("expected_evidence_refs", [])
                ),
                "expected_requirement_theme": finding.get("expected_requirement_theme", ""),
                "expected_evidence_refs": finding.get("expected_evidence_refs", []),
                "should_block_auto_clear": finding.get("should_block_auto_clear", False),
            }
            for finding in payload["must_detect_findings"]
        ],
        "non_error_decoys": [],
        "acceptable_false_positive_boundaries": payload.get(
            "acceptable_false_positive_boundaries", []
        ),
    }


def _match_visible_review_pack_error(
    gold: dict[str, Any], findings: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Match a gold finding only when one visible card states and evidences it.

    A source quote alone is deliberately insufficient: it would credit a generic
    hint that a reviewer cannot action. Conversely, raw pipeline findings are
    never supplied here; this scorer accepts only rendered ReviewPack cards.
    """
    expected_statement = gold.get("expected_reviewer_finding", "")
    expected_evidence = [
        ref.get("quote", "") for ref in gold.get("expected_evidence_refs", [])
    ]
    if not expected_statement or not expected_evidence:
        return _match_error(gold, findings)

    expected_severity = _severity_rank_name(gold.get("severity"))
    best: tuple[float, dict[str, Any]] | None = None
    for finding in findings:
        if finding.get("verifier_status") not in _CANONICAL_VISIBLE_VERIFIER_STATUSES:
            continue
        statement = finding.get("risk_statement", "")
        statement_score = max(
            _jaccard(expected_statement, statement),
            _similarity(expected_statement, statement),
        )
        evidence_quotes = [
            item.get("quote", "") for item in finding.get("evidence_items", []) or []
        ]
        has_expected_evidence = any(
            _normalize(expected_quote) in _normalize(quote)
            or _normalize(quote) in _normalize(expected_quote)
            for expected_quote in expected_evidence
            if expected_quote
            for quote in evidence_quotes
            if quote
        )
        severity_is_not_undercalled = (
            _severity_rank_name(finding.get("severity")) >= expected_severity
        )
        if statement_score < 0.40 or not has_expected_evidence or not severity_is_not_undercalled:
            continue
        if best is None or statement_score > best[0]:
            best = (statement_score, finding)
    if best is None:
        return None
    return {
        "score": round(best[0], 3),
        "method": "visible_pack_statement_and_evidence",
        "finding_id": best[1].get("finding_id"),
        "risk_statement": best[1].get("risk_statement"),
        "severity": best[1].get("severity"),
    }


def _score_visible_review_pack_errors(
    answer_key: dict[str, Any], findings: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Score visible cards one-to-one against gold findings for package release."""
    matched: list[dict[str, Any]] = []
    missed: list[dict[str, Any]] = []
    available = list(findings)
    for gold in answer_key.get("errors", []):
        match = _match_visible_review_pack_error(gold, available)
        record = {
            "error_id": gold["error_id"],
            "severity": gold.get("severity"),
            "error_type": gold.get("error_type"),
            "expected_reviewer_finding": gold.get("expected_reviewer_finding"),
            "should_block_auto_clear": gold.get("should_block_auto_clear", False),
            "match": match,
        }
        if match:
            matched.append(record)
            finding_id = match.get("finding_id")
            if finding_id:
                available = [
                    finding for finding in available if finding.get("finding_id") != finding_id
                ]
        else:
            missed.append(record)
    return matched, missed


def _package_release_gate(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the package-mode release decision from ReviewPack-visible findings only."""
    missed_blocking_findings = [
        {
            "case_id": case["case_id"],
            "error_id": record["error_id"],
            "severity": record.get("severity"),
            "expected_reviewer_finding": record.get("expected_reviewer_finding"),
        }
        for case in case_results
        for record in case.get("review_pack_missed_errors", [])
        if record.get("should_block_auto_clear", False)
    ]
    return {
        "passed": not missed_blocking_findings,
        "missed_blocking_findings": missed_blocking_findings,
    }


def _package_mode_exit_code(package_release_gate: dict[str, Any] | None) -> int:
    """Keep the CLI's package-mode exit status independently testable."""
    return 0 if package_release_gate is None or package_release_gate["passed"] else 1


def _tenant_auth_headers(api_key_to_tenant_id: dict[str, str], tenant_id: str) -> dict[str, str]:
    """Give the in-process harness the same tenant credential required in production."""
    if not api_key_to_tenant_id:
        return {}
    api_key = next(
        (
            key
            for key, mapped_tenant_id in api_key_to_tenant_id.items()
            if mapped_tenant_id == tenant_id
        ),
        None,
    )
    if api_key is None:
        raise RuntimeError(f"No API key configured for goldstandard tenant {tenant_id}")
    return {"X-API-Key": api_key}


def _wait_for_pipeline_completion(
    client: Any,
    initial_payload: dict[str, Any],
    *,
    poll_interval_seconds: float = 0.25,
    timeout_seconds: float = 300.0,
) -> dict[str, Any]:
    """Poll the asynchronous pipeline-run endpoint until it reaches a terminal status."""
    pipeline_run_id = initial_payload.get("pipeline_run_id")
    if not pipeline_run_id:
        raise RuntimeError("Pipeline accepted run without pipeline_run_id")
    payload = initial_payload
    deadline = time.monotonic() + timeout_seconds
    while payload.get("status") not in _TERMINAL_PIPELINE_STATUSES:
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Pipeline run {pipeline_run_id} did not complete before timeout")
        if poll_interval_seconds:
            time.sleep(poll_interval_seconds)
        response = client.get(f"/pipeline-runs/{pipeline_run_id}")
        if response.status_code != 200:
            raise RuntimeError(
                f"Pipeline run {pipeline_run_id} polling failed: {response.text}"
            )
        payload = response.json()
    return payload


def run_case(
    client: Any,
    repository: Any,
    audit_log: Any,
    case_dir: Path,
    *,
    pipeline_timeout_seconds: float = 300.0,
) -> dict[str, Any]:
    case_id = case_dir.name.upper()
    oracle_path = _oracle_path(case_dir)
    package_metadata = _package_metadata(case_dir)

    create_response = client.post(
        "/document-sets",
        json={
            "tenant_id": TENANT_ID,
            "requirement_set_id": REQUIREMENT_SET_ID,
            **package_metadata,
            "uploaded_by": "user_goldstandard_harness",
        },
    )
    create_response.raise_for_status() if hasattr(create_response, "raise_for_status") else None
    if create_response.status_code != 201:
        raise RuntimeError(f"{case_id}: document set creation failed: {create_response.text}")
    document_set_id = create_response.json()["document_set_id"]

    uploaded = []
    for doc_path in _package_document_paths(case_dir):
        upload = client.post(
            f"/document-sets/{document_set_id}/documents",
            files={"file": (doc_path.name, doc_path.read_bytes(), "text/markdown")},
            data={"uploaded_by": "user_goldstandard_harness"},
        )
        if upload.status_code != 201:
            raise RuntimeError(f"{case_id}: upload of {doc_path.name} failed: {upload.text}")
        uploaded.append(doc_path.name)

    pipeline_response = client.post(f"/document-sets/{document_set_id}/pipeline-runs")
    if pipeline_response.status_code != 202:
        raise RuntimeError(f"{case_id}: pipeline run failed: {pipeline_response.text}")
    pipeline_payload = _wait_for_pipeline_completion(
        client,
        pipeline_response.json(),
        timeout_seconds=pipeline_timeout_seconds,
    )

    claims = repository.list_claims(document_set_id)
    fusion_findings = repository.list_risk_fusion_findings(document_set_id)
    primary_findings = repository.list_risk_findings(document_set_id)
    findings_models = fusion_findings or primary_findings
    findings = [finding.model_dump(mode="json") for finding in findings_models]
    decision = repository.get_latest_risk_decision(document_set_id)

    # Gold findings are read only after the pipeline; package metadata above is
    # declaration-only and is never included in the upload manifest.
    answer_key = _load_post_run_oracle(oracle_path)
    case_id = answer_key["case_id"]

    matched, missed = _score_errors(answer_key, findings)

    review_pack_findings: list[dict[str, Any]] = []
    try:
        from app.services.review_pack import ReviewPackService

        review_pack = ReviewPackService(repository=repository, audit_log=audit_log).get_review_pack(
            document_set_id
        )
        review_pack_findings = _review_pack_risks_as_findings(
            [
                risk.model_dump(mode="json")
                for risk in review_pack.top_risks
            ]
        )
        review_pack_matched, review_pack_missed = _score_visible_review_pack_errors(
            answer_key,
            review_pack_findings,
        )
        review_pack_error: str | None = None
    except Exception as exc:  # noqa: BLE001 - pack visibility must not mask pipeline score
        review_pack_matched, review_pack_missed = _score_visible_review_pack_errors(
            answer_key, []
        )
        review_pack_error = str(exc)

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
    gold_related_finding_ids = _gold_related_finding_ids(
        answer_key.get("errors", []), findings
    )

    def _summarize(finding: dict[str, Any]) -> dict[str, Any]:
        return {
            "finding_id": finding.get("finding_id"),
            "severity": finding.get("severity"),
            "risk_statement": finding.get("risk_statement"),
        }

    # Split by whether the finding relates to a planted error at all. Lumping
    # both together made a correct restatement look identical to a false alarm.
    redundant_findings = [
        _summarize(finding)
        for finding in findings
        if finding.get("finding_id") in gold_related_finding_ids
        and finding.get("finding_id") not in matched_finding_ids
    ]
    unmatched_findings = [
        _summarize(finding)
        for finding in findings
        if finding.get("finding_id") not in gold_related_finding_ids
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
    # The manifest already carries why a role failed; without it a run reports
    # only that eight roles are gone and the cause has to be reconstructed from
    # token counts.
    model_failures = {
        entry.get("agent_role"): {
            "error_type": entry.get("error_type"),
            "error_summary": entry.get("error_summary"),
        }
        for entry in pipeline_payload.get("model_manifest", [])
        if entry.get("status") and entry.get("status") != "succeeded"
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
        "model_failures": model_failures,
        "claim_count": len(claims),
        "finding_count": len(findings),
        "review_pack_finding_count": len(review_pack_findings),
        "citation_verified_finding_count": len(verified),
        "risk_decision": getattr(decision, "decision", None),
        "auto_clear_allowed": getattr(decision, "auto_clear_allowed", None),
        "gold_error_count": len(answer_key.get("errors", [])),
        "matched_errors": matched,
        "missed_errors": missed,
        "review_pack_matched_errors": review_pack_matched,
        "review_pack_missed_errors": review_pack_missed,
        "review_pack_error": review_pack_error,
        "decoy_count": len(answer_key.get("non_error_decoys", [])),
        "decoy_false_alarms": decoy_hits,
        "decoys_passed": decoys_passed,
        "redundant_findings": redundant_findings,
        "unmatched_findings": unmatched_findings,
        # Kept in full so a finished run can be rescored against a changed
        # matcher without paying for the model calls again.
        "findings": findings,
        "quality_metrics": _quality_metrics(
            answer_key=answer_key,
            findings=findings,
            matched=matched,
            risk_decision=decision,
        ),
    }


def _quality_metrics(
    *,
    answer_key: dict[str, Any],
    findings: list[dict[str, Any]],
    matched: list[dict[str, Any]],
    risk_decision: Any,
) -> dict[str, Any]:
    errors = answer_key.get("errors", [])
    matched_ids = {
        record["match"]["finding_id"] for record in matched if record.get("match")
    }
    exact = 0
    under = 0
    over = 0
    high_or_critical_under = 0
    for record in matched:
        gold = next(error for error in errors if error["error_id"] == record["error_id"])
        actual = record["match"].get("severity")
        expected = gold.get("severity")
        if actual == expected:
            exact += 1
        elif _severity_rank_name(actual) < _severity_rank_name(expected):
            under += 1
            if expected in {"high", "critical"}:
                high_or_critical_under += 1
        else:
            over += 1
    # A finding either restates an error the run already reported, or it points
    # at nothing in the answer key. Summing per-gold candidate counts conflated
    # the two and could exceed the number of findings, because a finding that
    # fits two gold errors was counted once per error.
    gold_related_ids = _gold_related_finding_ids(errors, findings)
    redundant_ids = gold_related_ids - matched_ids
    unmatched_findings = [
        finding for finding in findings if finding.get("finding_id") not in gold_related_ids
    ]
    unsupported = [
        finding
        for finding in findings
        if finding.get("evidence_support") != "strong"
        and finding.get("status") != "rejected"
    ]
    boundaries = answer_key.get("acceptable_false_positive_boundaries", [])
    boundary_violations = [
        finding
        for finding in unmatched_findings
        if _matches_false_positive_boundary(finding, boundaries)
    ]
    blocking_gold = [
        error for error in errors if error.get("should_block_auto_clear", False)
    ]
    auto_clear_false_negative_count = (
        len(blocking_gold) if getattr(risk_decision, "auto_clear_allowed", False) else 0
    )
    return {
        "must_detect_recall": round(len(matched) / len(errors), 4) if errors else 1.0,
        "matched_finding_count": len(matched_ids),
        "gold_related_finding_count": len(gold_related_ids),
        "redundant_finding_count": len(redundant_ids),
        "unrelated_finding_count": len(unmatched_findings),
        "unsupported_finding_count": len(unsupported),
        "finding_count": len(findings),
        "unsupported_high_critical_published_count": sum(
            finding.get("severity") in {"high", "critical"} for finding in unsupported
        ),
        "false_positive_boundary_violation_count": len(boundary_violations),
        "severity_exact_count": exact,
        "severity_undercall_count": under,
        "severity_overcall_count": over,
        "high_or_critical_undercall_count": high_or_critical_under,
        "auto_clear_false_negative_count": auto_clear_false_negative_count,
    }


def _gold_related_finding_ids(
    errors: list[dict[str, Any]],
    findings: list[dict[str, Any]],
) -> set[Any]:
    """Findings that point at some planted error, whether or not they scored it.

    Only the first finding per gold error is credited as the match, so without
    this distinction every further correct restatement of the same error was
    indistinguishable from a finding about nothing.
    """
    return {
        finding.get("finding_id")
        for gold in errors
        for finding in findings
        if _match_error(gold, [finding]) is not None
    }


def _severity_rank_name(severity: Any) -> int:
    return {"informational": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}.get(
        str(severity), -1
    )


def _matches_false_positive_boundary(
    finding: dict[str, Any], boundaries: list[str],
) -> bool:
    finding_text = " ".join(_finding_texts(finding))
    normalized_finding = _normalize(finding_text)
    return any(
        (normalized_boundary := _normalize(boundary))
        and normalized_boundary in normalized_finding
        for boundary in boundaries
    )


def _aggregate(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    total_errors = sum(case["gold_error_count"] for case in case_results)
    total_matched = sum(len(case["matched_errors"]) for case in case_results)
    total_review_pack_matched = sum(
        len(case.get("review_pack_matched_errors") or []) for case in case_results
    )
    total_decoys = sum(case["decoy_count"] for case in case_results)
    total_decoy_hits = sum(len(case["decoy_false_alarms"]) for case in case_results)
    total_findings = sum(case["finding_count"] for case in case_results)
    total_verified = sum(case["citation_verified_finding_count"] for case in case_results)
    # Only counts may be summed. Rates are recomputed from the totals below;
    # adding a per-case ratio ten times reported a recall of 10.0.
    quality_metric_keys = [
        "matched_finding_count",
        "gold_related_finding_count",
        "redundant_finding_count",
        "unrelated_finding_count",
        "unsupported_finding_count",
        "unsupported_high_critical_published_count",
        "false_positive_boundary_violation_count",
        "severity_exact_count",
        "severity_undercall_count",
        "severity_overcall_count",
        "high_or_critical_undercall_count",
        "auto_clear_false_negative_count",
    ]
    quality_metrics: dict[str, Any] = {
        key: sum((case.get("quality_metrics") or {}).get(key, 0) for case in case_results)
        for key in quality_metric_keys
    }
    quality_metrics["must_detect_recall"] = (
        round(total_matched / total_errors, 4) if total_errors else 1.0
    )
    gold_related = quality_metrics["gold_related_finding_count"]
    quality_metrics["redundancy_rate"] = (
        round(quality_metrics["redundant_finding_count"] / gold_related, 4)
        if gold_related
        else 0.0
    )
    quality_metrics["unsupported_finding_rate"] = (
        round(quality_metrics["unsupported_finding_count"] / total_findings, 4)
        if total_findings
        else 0.0
    )

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
        "review_pack_sensitivity": {
            "found": total_review_pack_matched,
            "total": total_errors,
            "rate": round(total_review_pack_matched / total_errors, 3)
            if total_errors
            else None,
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
        # Decoy specificity only covers the planted decoys, which are a tiny
        # fraction of what a run emits. These two say what a reviewer actually
        # faces: how much of the output pointed at a real error, and how long
        # the list in front of them is.
        "finding_precision": {
            "matched": total_matched,
            "total_findings": total_findings,
            "rate": round(total_matched / total_findings, 3) if total_findings else None,
        },
        "findings_per_case": (
            round(total_findings / len(case_results), 1) if case_results else None
        ),
        "quality_metrics": quality_metrics,
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
    pack_sens = aggregate["review_pack_sensitivity"]
    spec = aggregate["specificity_decoys"]
    cite = aggregate["citation_precision"]
    lines.append(
        f"- **Sensitivität:** {sens['found']} von {sens['total']} versteckten Fehlern gefunden"
        + (f" ({sens['rate']:.0%})" if sens["rate"] is not None else "")
    )
    lines.append(
        f"- **In Prüfmappe sichtbar:** {pack_sens['found']} von {pack_sens['total']}"
        " versteckten Fehlern"
        + (f" ({pack_sens['rate']:.0%})" if pack_sens["rate"] is not None else "")
    )
    lines.append(
        f"- **Spezifität (Decoys):** {spec['passed']} von {spec['total']} Decoys korrekt"
        " nicht beanstandet"
        + (f" ({spec['rate']:.0%})" if spec["rate"] is not None else "")
        + " — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings"
    )
    prec = aggregate["finding_precision"]
    quality_summary = aggregate.get("quality_metrics") or {}
    total_findings = prec["total_findings"]
    related = quality_summary.get("gold_related_finding_count")
    if related is not None and total_findings:
        matched_findings = quality_summary.get("matched_finding_count", 0)
        redundant = quality_summary.get("redundant_finding_count", 0)
        unrelated = quality_summary.get("unrelated_finding_count", 0)
        # Deliberately not prec["matched"]: that counts gold errors, and a single
        # finding can satisfy two of them, which produced a hit count larger than
        # the number of findings it came from.
        lines.append(
            f"- **Findings mit Bezug zu echten Fehlern:** {related} von"
            f" {total_findings} ({related / total_findings:.0%})"
            f" — {matched_findings} als Treffer gewertet,"
            f" {redundant} Wiederholungen bereits gemeldeter Fehler"
        )
        lines.append(
            f"- **Ohne Bezug zum Lösungsschlüssel:** {unrelated} von"
            f" {total_findings} ({unrelated / total_findings:.0%})"
            " — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein"
        )
    if aggregate.get("findings_per_case") is not None:
        lines.append(
            f"- **Findings pro Fall:** {aggregate['findings_per_case']}"
            " — so lang ist die Liste, die ein Prüfer durchgeht"
        )
    lines.append(
        f"- **Belegtreue:** {cite['verified']} von {cite['total_findings']} Findings mit"
        " verifiziertem Zitat"
        + (f" ({cite['rate']:.0%})" if cite["rate"] is not None else "")
    )
    quality = aggregate.get("quality_metrics") or {}
    if quality:
        lines.extend(
            [
                "",
                "## Qualitätsmetriken",
                "",
                f"- Must-detect Recall: `{quality['must_detect_recall']}`",
                (
                    "- Wiederholungen: "
                    f"`{quality['redundant_finding_count']}`"
                    f" (Redundanzrate `{quality['redundancy_rate']}`)"
                ),
                f"- Unsupported Findings: `{quality['unsupported_finding_rate']}`",
                (
                    "- False-positive-Grenzverletzungen: "
                    f"`{quality['false_positive_boundary_violation_count']}`"
                ),
                (
                    "- Severity exact/under/over: "
                    f"`{quality['severity_exact_count']}/"
                    f"{quality['severity_undercall_count']}/"
                    f"{quality['severity_overcall_count']}`"
                ),
                (
                    "- Auto-clear mit blockierendem Gold: "
                    f"`{quality['auto_clear_false_negative_count']}`"
                ),
            ]
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
        "| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden "
        "| In Prüfmappe | Decoy-Fehlalarme | Entscheidung |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for case in case_results:
        lines.append(
            f"| {case['case_id']} | {case['pipeline_status']} | {case['claim_count']} "
            f"| {case['finding_count']} | {len(case.get('redundant_findings') or [])} "
            f"| {len(case['unmatched_findings'])} "
            f"| {len(case['matched_errors'])}/{case['gold_error_count']} "
            f"| {len(case.get('review_pack_matched_errors') or [])}/{case['gold_error_count']} "
            f"| {len(case['decoy_false_alarms'])}/{case['decoy_count']} "
            f"| {case['risk_decision'] or '-'} |"
        )
    lines.append("")
    failures_by_reason: dict[tuple[str, str], list[str]] = {}
    for case in case_results:
        for role, failure in (case.get("model_failures") or {}).items():
            key = (
                failure.get("error_type") or "unknown",
                (failure.get("error_summary") or "")[:160],
            )
            failures_by_reason.setdefault(key, []).append(f"{case['case_id']}/{role}")
    if failures_by_reason:
        lines.extend(["## Modellausfälle", ""])
        for (error_type, summary), occurrences in sorted(
            failures_by_reason.items(), key=lambda item: -len(item[1])
        ):
            lines.append(f"- **{error_type}** ({len(occurrences)}×): {summary or '-'}")
            lines.append(f"  - betroffen: {', '.join(occurrences[:6])}")
            if len(occurrences) > 6:
                lines.append(f"  - … und {len(occurrences) - 6} weitere")
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
        if case.get("redundant_findings"):
            lines.append(
                f"- 🔁 {len(case['redundant_findings'])} weitere Findings zu bereits"
                " gemeldeten Fehlern (Wiederholungen)"
            )
        if case["unmatched_findings"]:
            lines.append(
                f"- ℹ️ {len(case['unmatched_findings'])} Findings ohne Bezug zum"
                " Lösungsschlüssel (manuell prüfen)"
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
    parser.add_argument(
        "--package-dir",
        help="Run one package directory with source documents and a post-run GOLD_STANDARD.json.",
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--pipeline-timeout-seconds", type=float, default=300.0)
    parser.add_argument("--anthropic-model", default="claude-sonnet-4-6")
    parser.add_argument("--openai-model", default="gpt-5.4")
    parser.add_argument("--mistral-model", default="mistral-large-latest")
    args = parser.parse_args(argv)

    _configure_environment(
        args.mode, args.stack, args.anthropic_model, args.openai_model, args.mistral_model
    )

    # Imports happen after env setup because get_settings() is lru_cached.
    from fastapi.testclient import TestClient

    from app.core.config import get_settings
    from app.main import app
    from app.schemas.domain import RequirementSet

    GOLDSTANDARD_STORAGE_PARENT.mkdir(parents=True, exist_ok=True)
    isolated_storage_root = Path(
        tempfile.mkdtemp(prefix="run-", dir=GOLDSTANDARD_STORAGE_PARENT)
    )
    os.environ["QRM_LOCAL_STORAGE_ROOT"] = str(isolated_storage_root)
    get_settings.cache_clear()
    settings = get_settings()
    _validate_isolated_harness_environment(
        persistence_enabled=settings.persistence_enabled,
        storage_root=Path(settings.local_storage_root),
    )
    repository, audit_log, restore_route_bindings = _install_isolated_route_bindings()
    repository.reset()
    audit_log.clear()

    repository.create_requirement_set(RequirementSet.model_validate(_requirement_set()))
    client = TestClient(
        app,
        headers=_tenant_auth_headers(get_settings().api_key_to_tenant_id(), TENANT_ID),
    )

    cases_dir = Path(args.cases_dir)
    case_dirs = (
        [Path(args.package_dir)]
        if args.package_dir
        else sorted(
            path
            for path in cases_dir.iterdir()
            if path.is_dir() and path.name.startswith("case_")
            and (not args.cases or path.name in args.cases)
        )
    )
    if not case_dirs:
        restore_route_bindings()
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
            result = run_case(
                client,
                repository,
                audit_log,
                case_dir,
                pipeline_timeout_seconds=args.pipeline_timeout_seconds,
            )
        except Exception as exc:  # noqa: BLE001 - report per-case failure, keep going
            result = {
                "case_id": case_dir.name.upper(),
                "pipeline_status": "harness_error",
                "failed_step": None,
                "error": str(exc),
                "claim_count": 0,
                "finding_count": 0,
                "review_pack_finding_count": 0,
                "citation_verified_finding_count": 0,
                "risk_decision": None,
                "auto_clear_allowed": None,
                "gold_error_count": 0,
                "matched_errors": [],
                "missed_errors": [],
                "review_pack_matched_errors": [],
                "review_pack_missed_errors": [],
                "review_pack_error": str(exc),
                "decoy_count": 0,
                "decoy_false_alarms": [],
                "decoys_passed": [],
                "redundant_findings": [],
                "unmatched_findings": [],
                "findings": [],
                "quality_metrics": {},
            }
        case_results.append(result)
        print(
            f"    -> status={result['pipeline_status']} claims={result['claim_count']}"
            f" findings={result['finding_count']}"
            f" errors_found={len(result['matched_errors'])}/{result['gold_error_count']}",
            flush=True,
        )

    aggregate = _aggregate(case_results)
    package_release_gate = _package_release_gate(case_results) if args.package_dir else None
    run_label = args.mode if args.mode == "mock" else f"{args.mode}_{args.stack}"
    output_dir = Path(args.output_dir) / started_at.strftime(f"%Y%m%d_%H%M%S_{run_label}")
    output_dir.mkdir(parents=True, exist_ok=True)
    # The raw findings are what a rescore needs and they dwarf everything else,
    # so they live beside results.json rather than inside it.
    (output_dir / "findings.json").write_text(
        json.dumps(
            {case["case_id"]: case.pop("findings", []) for case in case_results},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (output_dir / "results.json").write_text(
        json.dumps(
            {
                "run": run_meta,
                "aggregate": aggregate,
                "cases": case_results,
                "package_release_gate": package_release_gate,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    markdown = _render_markdown(run_meta, aggregate, case_results)
    (output_dir / "report.md").write_text(markdown, encoding="utf-8")
    print()
    print(markdown)
    if package_release_gate is not None:
        gate_status = "PASS" if package_release_gate["passed"] else "FAIL"
        print(
            "\nPackage visible-ReviewPack release gate: "
            f"{gate_status} ({len(package_release_gate['missed_blocking_findings'])} "
            "blocking finding(s) missed)"
        )
    print(f"\nReports written to {output_dir}")
    restore_route_bindings()
    return _package_mode_exit_code(package_release_gate)


if __name__ == "__main__":
    raise SystemExit(main())
