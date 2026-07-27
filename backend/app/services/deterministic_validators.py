"""Deterministic validators over structured evidence.

These are the mechanical checks a prose-level model read keeps getting wrong:
the one empty field in an otherwise complete block, the one measurement past
its limit, the one action item of four without a responsible. Each validator
is pure arithmetic and set comparison over rows whose quotes were already
grounded against the stored chunks -- no model, no heuristics, no fuzz. Their
findings can only ever escalate a requirement verdict towards VIOLATED, and
every finding names the rule and the grounded rows it rests on.

Unlike the retired objective red-flag layer, no rule here knows any corpus:
there is no "NMT 0.10 %" and no site name, only shapes -- a value and its
declared limit, a field and its emptiness, one activity signed by two hands.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

from app.schemas.structured_evidence import (
    EvidenceLocation,
    ExtractedActionItem,
    ExtractedEvent,
    ExtractedMeasurement,
    ExtractedSignature,
    ExtractedSpecification,
    StructuredEvidence,
    ValidatorFinding,
)

VALIDATOR_VERSION = "deterministic-validators-v0.1"


def run_validators(evidence: StructuredEvidence) -> list[ValidatorFinding]:
    findings = [
        *_empty_required_fields(evidence.signatures, evidence.action_items),
        *_limit_breaches(evidence.measurements, evidence.specifications),
        *_actor_conflicts(evidence.events),
    ]
    return sorted(findings, key=lambda f: (f.validator_id, f.statement))


def _empty_required_fields(
    signatures: Iterable[ExtractedSignature],
    action_items: Iterable[ExtractedActionItem],
) -> list[ValidatorFinding]:
    findings = []
    for signature in signatures:
        if not signature.is_empty:
            continue
        role = f" ({signature.role})" if signature.role else ""
        findings.append(
            ValidatorFinding(
                validator_id="empty_required_field",
                requirement_ids=list(signature.requirement_ids),
                severity="high",
                statement=(
                    f"Das Pflichtfeld '{signature.field_label}'{role} ist nicht "
                    "gezeichnet: Das Feld existiert, trägt aber keinen "
                    "Unterzeichner."
                ),
                locations=[signature.location],
            )
        )
    for item in action_items:
        if item.responsible and item.responsible.strip():
            continue
        findings.append(
            ValidatorFinding(
                validator_id="action_item_without_responsible",
                requirement_ids=list(item.requirement_ids),
                severity="medium",
                statement=(
                    f"Die Maßnahme '{item.item_label}' in '{item.list_label}' "
                    "hat keinen benannten Verantwortlichen."
                ),
                locations=[item.location],
            )
        )
    return findings


_NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")

#: Units whose strings may differ in writing but denote the same scale.
_UNIT_ALIASES = {
    "%": "%",
    "prozent": "%",
    "°c": "°c",
    "grad c": "°c",
    "grad celsius": "°c",
    "mg/ml": "mg/ml",
    "g/l": "mg/ml",  # numerically identical scale
    "min": "min",
    "minuten": "min",
    "h": "h",
    "stunden": "h",
}


def _limit_breaches(
    measurements: Iterable[ExtractedMeasurement],
    specifications: Iterable[ExtractedSpecification],
) -> list[ValidatorFinding]:
    """Compare each measurement against every specification of its parameter.

    The join is by normalised parameter name plus compatible unit. Comparable
    means both sides parse to numbers on the same scale; anything else is
    silently skipped, because a validator that guesses is worse than none.
    """
    specs_by_parameter: dict[str, list[ExtractedSpecification]] = {}
    for spec in specifications:
        specs_by_parameter.setdefault(_fold(spec.parameter), []).append(spec)

    findings = []
    for measurement in measurements:
        value = _parse_number(measurement.value)
        if value is None:
            continue
        for spec in specs_by_parameter.get(_fold(measurement.parameter), []):
            if not _units_compatible(measurement.unit, spec.unit):
                continue
            breach = _breach_description(value, spec)
            if breach is None:
                continue
            findings.append(
                ValidatorFinding(
                    validator_id="measurement_outside_specification",
                    requirement_ids=sorted(
                        {*measurement.requirement_ids, *spec.requirement_ids}
                    ),
                    severity="high",
                    statement=(
                        f"Der Messwert {measurement.value}"
                        f"{' ' + measurement.unit if measurement.unit else ''} für "
                        f"'{measurement.parameter}' liegt außerhalb der "
                        f"deklarierten Grenze ({breach})."
                    ),
                    locations=_dedupe_locations(
                        [measurement.location, spec.location]
                    ),
                )
            )
    return findings


def _breach_description(value: float, spec: ExtractedSpecification) -> str | None:
    low = _parse_number(spec.limit_low) if spec.limit_low else None
    high = _parse_number(spec.limit_high) if spec.limit_high else None
    operator = _fold(spec.operator)
    if operator in {"nmt", "<=", "≤", "max", "maximal", "hoechstens"}:
        limit = high if high is not None else low
        if limit is not None and value > limit:
            return f"{spec.operator} {spec.limit_high or spec.limit_low}"
        return None
    if operator in {"nlt", ">=", "≥", "min", "mindestens"}:
        limit = low if low is not None else high
        if limit is not None and value < limit:
            return f"{spec.operator} {spec.limit_low or spec.limit_high}"
        return None
    if operator in {"range", "bereich", "-", "bis"}:
        if low is not None and value < low:
            return f"Bereich {spec.limit_low}–{spec.limit_high}"
        if high is not None and value > high:
            return f"Bereich {spec.limit_low}–{spec.limit_high}"
        return None
    return None


def _actor_conflicts(events: Iterable[ExtractedEvent]) -> list[ValidatorFinding]:
    """Flag one activity carrying different hands or times.

    Only rows sharing an activity_key are ever compared -- the extraction
    already decided what belongs together, which is exactly the semantic step
    that made these checks impossible to run on raw text.
    """
    by_key: dict[str, list[ExtractedEvent]] = {}
    for event in events:
        if event.activity_key:
            by_key.setdefault(event.activity_key, []).append(event)

    findings = []
    for _key, group in sorted(by_key.items()):
        if len(group) < 2:
            continue
        actors = sorted({_fold(e.actor) for e in group if e.actor})
        if len(actors) > 1:
            shown = sorted({e.actor for e in group if e.actor})
            findings.append(
                ValidatorFinding(
                    validator_id="conflicting_actors_for_one_activity",
                    requirement_ids=sorted(
                        {rid for e in group for rid in e.requirement_ids}
                    ),
                    severity="medium",
                    statement=(
                        f"Dieselbe Tätigkeit ('{group[0].description}') ist von "
                        f"unterschiedlichen Personen gezeichnet: {', '.join(shown)}. "
                        "Ohne dokumentierte Erklärung ist die Zurechenbarkeit "
                        "nicht gegeben."
                    ),
                    locations=_dedupe_locations([e.location for e in group]),
                )
            )
        timestamps = sorted({e.timestamp for e in group if e.timestamp})
        if len(timestamps) > 1:
            findings.append(
                ValidatorFinding(
                    validator_id="conflicting_timestamps_for_one_activity",
                    requirement_ids=sorted(
                        {rid for e in group for rid in e.requirement_ids}
                    ),
                    severity="medium",
                    statement=(
                        f"Dieselbe Tätigkeit ('{group[0].description}') trägt "
                        f"widersprüchliche Zeitangaben: {', '.join(timestamps)}."
                    ),
                    locations=_dedupe_locations([e.location for e in group]),
                )
            )
    return findings


def _parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    match = _NUMBER.search(value.replace(" ", " "))
    if match is None:
        return None
    return float(match.group(0).replace(",", "."))


def _units_compatible(left: str | None, right: str | None) -> bool:
    if not left or not right:
        # A missing unit on either side makes the comparison a guess; refuse.
        return bool(left) == bool(right)
    return _unit_key(left) == _unit_key(right)


def _unit_key(unit: str) -> str:
    folded = _fold(unit)
    return _UNIT_ALIASES.get(folded, folded)


def _fold(value: str | None) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(text.split())


def _dedupe_locations(locations: list[EvidenceLocation]) -> list[EvidenceLocation]:
    seen: dict[tuple[str, str, str], EvidenceLocation] = {}
    for location in locations:
        seen.setdefault(
            (location.document_id, location.chunk_id, location.quote), location
        )
    return list(seen.values())
