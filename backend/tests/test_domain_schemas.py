from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from app.schemas.domain import (
    Claim,
    Document,
    DocumentChunk,
    DocumentSet,
    EvidenceItem,
    ModelRun,
    Requirement,
    RequirementSet,
    ReviewDecision,
    ReviewDecisionValue,
    RiskFinding,
    Severity,
)

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


VALID_EXAMPLES: dict[str, type[BaseModel]] = {
    "document_set.json": DocumentSet,
    "document.json": Document,
    "document_chunk.json": DocumentChunk,
    "claim.json": Claim,
    "requirement.json": Requirement,
    "requirement_set.json": RequirementSet,
    "evidence_item.json": EvidenceItem,
    "risk_finding.json": RiskFinding,
    "model_run.json": ModelRun,
    "review_decision.json": ReviewDecision,
}


@pytest.mark.parametrize(("file_name", "schema"), VALID_EXAMPLES.items())
def test_example_json_is_valid_and_serializable(
    file_name: str,
    schema: type[BaseModel],
) -> None:
    payload = _load_example(file_name)

    parsed = schema.model_validate(payload)
    serialized = parsed.model_dump_json()
    reparsed = schema.model_validate_json(serialized)

    assert reparsed == parsed


def test_severity_is_enum() -> None:
    assert Severity.CRITICAL.value == "critical"
    payload = _load_example("risk_finding.json")
    payload["severity"] = "catastrophic"

    with pytest.raises(ValidationError):
        RiskFinding.model_validate(payload)


def test_review_decision_is_enum() -> None:
    assert ReviewDecisionValue.CONFIRM.value == "confirm"
    payload = _load_example("review_decision.json")
    payload["decision"] = "approve"

    with pytest.raises(ValidationError):
        ReviewDecision.model_validate(payload)


def test_ids_are_typed_with_expected_prefixes() -> None:
    payload = _load_example("document.json")
    payload["document_id"] = "123"

    with pytest.raises(ValidationError):
        Document.model_validate(payload)


def test_high_or_critical_risk_finding_cannot_auto_close() -> None:
    payload = _load_example("risk_finding.json")
    payload["auto_close_allowed"] = True

    with pytest.raises(ValidationError):
        RiskFinding.model_validate(payload)


def test_evidence_support_none_cannot_include_evidence_items() -> None:
    payload = _load_example("risk_finding.json")
    payload["severity"] = "medium"
    payload["auto_close_allowed"] = True
    payload["evidence_support"] = "none"

    with pytest.raises(ValidationError):
        RiskFinding.model_validate(payload)


def test_document_chunk_page_range_is_validated() -> None:
    payload = _load_example("document_chunk.json")
    payload["page_end"] = 0

    with pytest.raises(ValidationError):
        DocumentChunk.model_validate(payload)


def test_requirement_effective_dates_are_validated() -> None:
    payload = _load_example("requirement.json")
    payload["effective_to"] = "2025-12-31T00:00:00Z"

    with pytest.raises(ValidationError):
        Requirement.model_validate(payload)


def test_token_usage_total_must_match_parts() -> None:
    payload = _load_example("model_run.json")
    payload["token_usage"]["total_tokens"] = 999

    with pytest.raises(ValidationError):
        ModelRun.model_validate(payload)


def _load_example(file_name: str) -> dict[str, Any]:
    return json.loads((EXAMPLES_DIR / file_name).read_text(encoding="utf-8"))
