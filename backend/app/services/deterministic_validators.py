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
from dataclasses import dataclass
from datetime import date

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

VALIDATOR_VERSION = "deterministic-validators-v0.2"


@dataclass(frozen=True)
class ValidationContext:
    """What the validators may know about the case beyond the extracted rows.

    Kept deliberately thin: the declared document type decides whether the
    CAPA-specific check runs at all, and the chunk texts exist only so a
    presence check can rule out a section the extractor may have skipped.
    """

    declared_document_type: str = ""
    chunk_texts: tuple[str, ...] = ()


#: Requirement ids a finding attaches to even when the extractor mapped the
#: underlying rows to nothing. This is the first, smallest form of a check
#: specification living next to the rule: the general GMP library's own
#: obligations that each rule exists to test. A customer library without
#: these ids simply gets findings attached through the rows' own mapping.
DEFAULT_REQUIREMENTS_BY_VALIDATOR: dict[str, tuple[str, ...]] = {
    "release_before_assessment": (
        "req_batch_no_release_before_assessment",
        "req_qc_qa_approval_before_first_gmp_use",
    ),
    "step_predates_its_event": ("req_di_signature_plausibility",),
    "effectiveness_check_before_implementation": ("req_capa_effectiveness",),
    "first_use_before_approval_or_training": (
        "req_qc_qa_approval_before_first_gmp_use",
        "req_qc_training_before_effective_sop_use",
    ),
    "same_person_performs_and_approves": ("req_di_signature_plausibility",),
    "capa_effectiveness_check_missing": ("req_capa_effectiveness",),
}


@dataclass(frozen=True)
class RuleDescription:
    """What a reviewer needs to read a rule: what it checks, on what, against
    which obligation, and how sure it is. The catalogue is the readable face
    of the deterministic layer -- the part of the system a QA department can
    validate rule by rule, with the goldstandard cases as its test suite."""

    validator_id: str
    title: str
    checks: str
    inputs: str
    severity: str
    regulatory_basis: str
    requirement_ids: tuple[str, ...]


RULE_CATALOGUE: tuple[RuleDescription, ...] = (
    RuleDescription(
        "empty_required_field",
        "Leeres Pflichtfeld",
        "Ein Signatur-, Prüf- oder Freigabefeld existiert im Dokument, trägt aber keinen Unterzeichner -- leer, nur ein Datum, 'siehe oben' oder 'N/A' ohne Begründung.",
        "Signaturfelder",
        "high",
        "EU-GMP Teil I Kap. 4.7-4.8 (Aufzeichnungen: zeitnah, lesbar, unterschrieben); ALCOA",
        (),
    ),
    RuleDescription(
        "action_item_without_responsible",
        "Maßnahme ohne Verantwortlichen",
        "Eine Position einer Maßnahmenliste nennt niemanden, der sie umsetzt.",
        "Maßnahmen",
        "medium",
        "EU-GMP Teil I Kap. 1.4 (xiv) (CAPA); ICH Q10 3.2.2",
        ("req_capa_responsible_timeline",),
    ),
    RuleDescription(
        "measurement_outside_specification",
        "Messwert außerhalb der deklarierten Grenze",
        "Ein Messwert wird mit jeder deklarierten Grenze desselben Parameters verglichen (gleiche Einheit); liegt er außerhalb, ist das ein Befund -- auch wenn das Dokument 'konform' sagt.",
        "Messwerte, Grenzwerte",
        "high",
        "EU-GMP Teil I Kap. 6.35-6.36 (OOS); Kap. 1.8 (vii)",
        (),
    ),
    RuleDescription(
        "conflicting_actors_for_one_activity",
        "Eine Tätigkeit, zwei Hände",
        "Dieselbe Handlung am selben Objekt ist im Dokument verschiedenen Personen zugeschrieben.",
        "Datierte Schritte",
        "medium",
        "EU-GMP Teil I Kap. 4.8; ALCOA (attributable)",
        (),
    ),
    RuleDescription(
        "conflicting_timestamps_for_one_activity",
        "Eine Tätigkeit, zwei Zeitangaben",
        "Dieselbe Handlung am selben Objekt trägt im Dokument widersprüchliche Zeitangaben.",
        "Datierte Schritte",
        "medium",
        "EU-GMP Teil I Kap. 4.8; ALCOA (contemporaneous)",
        (),
    ),
    RuleDescription(
        "step_predates_its_event",
        "Schritt vor dem Ereignis datiert",
        "Eine Untersuchung, Bewertung, Prüfung, Freigabe oder Wirksamkeitsprüfung ist früher datiert als das Ereignis derselben Aufzeichnung, das sie betrifft.",
        "Datierte Schritte (Rolle, Bezugsobjekt)",
        "high",
        "EU-GMP Teil I Kap. 4.8; Annex 11 §9 (Audit Trail)",
        DEFAULT_REQUIREMENTS_BY_VALIDATOR["step_predates_its_event"],
    ),
    RuleDescription(
        "release_before_assessment",
        "Freigabe vor abgeschlossener Bewertung",
        "Eine Freigabe ist früher datiert als die Bewertung oder Untersuchung derselben Aufzeichnung, auf der sie beruht.",
        "Datierte Schritte (Rolle, Bezugsobjekt)",
        "critical",
        "EU-GMP Teil I Kap. 1.4 (xv); Kap. 1.8 (vii); Annex 16",
        DEFAULT_REQUIREMENTS_BY_VALIDATOR["release_before_assessment"],
    ),
    RuleDescription(
        "effectiveness_check_before_implementation",
        "Wirksamkeitsprüfung vor Umsetzung",
        "Eine Wirksamkeitsprüfung ist früher datiert als die Umsetzung der Maßnahme, die sie prüft.",
        "Datierte Schritte (Rolle, Bezugsobjekt)",
        "high",
        "EU-GMP Teil I Kap. 1.4 (xiv); ICH Q10 3.2.2",
        DEFAULT_REQUIREMENTS_BY_VALIDATOR["effectiveness_check_before_implementation"],
    ),
    RuleDescription(
        "first_use_before_approval_or_training",
        "Erste Anwendung vor Freigabe oder Schulung",
        "Die erste GMP-Anwendung einer Änderung ist früher datiert als ihre Freigabe oder die zugehörige Schulung.",
        "Datierte Schritte (Rolle, Bezugsobjekt)",
        "high",
        "EU-GMP Teil I Kap. 1.4 (xi), Kap. 2.10-2.11; Annex 15 §11",
        DEFAULT_REQUIREMENTS_BY_VALIDATOR["first_use_before_approval_or_training"],
    ),
    RuleDescription(
        "same_person_performs_and_approves",
        "Vier-Augen-Prinzip nicht erkennbar",
        "Dieselbe Person hat einen Vorgang sowohl ausgeführt bzw. erstellt als auch geprüft oder freigegeben.",
        "Signaturfelder, datierte Schritte",
        "medium",
        "EU-GMP Teil I Kap. 2.5-2.7 (Verantwortlichkeiten); 21 CFR 211.22",
        DEFAULT_REQUIREMENTS_BY_VALIDATOR["same_person_performs_and_approves"],
    ),
    RuleDescription(
        "capa_effectiveness_check_missing",
        "CAPA ohne Wirksamkeitsprüfung",
        "Korrekturmaßnahmen sind festgelegt, aber nirgends in den Unterlagen ist eine Wirksamkeitsprüfung vorgesehen -- weder als Schritt, noch als Maßnahme, noch als Erwähnung.",
        "Maßnahmen, datierte Schritte, Volltext",
        "high",
        "EU-GMP Teil I Kap. 1.4 (xiv); ICH Q10 3.2.2",
        DEFAULT_REQUIREMENTS_BY_VALIDATOR["capa_effectiveness_check_missing"],
    ),
)


def run_validators(
    evidence: StructuredEvidence, context: ValidationContext | None = None
) -> list[ValidatorFinding]:
    context = context or ValidationContext()
    findings = [
        *_empty_required_fields(evidence.signatures, evidence.action_items),
        *_limit_breaches(evidence.measurements, evidence.specifications),
        *_actor_conflicts(evidence.events),
        *_ordering_breaches(evidence.events),
        *_segregation_of_duties(evidence.signatures, evidence.events),
        *_capa_effectiveness_missing(evidence, context),
    ]
    attached = [
        finding.model_copy(
            update={
                "requirement_ids": sorted(
                    {
                        *finding.requirement_ids,
                        *DEFAULT_REQUIREMENTS_BY_VALIDATOR.get(finding.validator_id, ()),
                    }
                )
            }
        )
        for finding in findings
    ]
    return sorted(attached, key=lambda f: (f.validator_id, f.statement))


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


# --- ordering ---------------------------------------------------------------

#: (earlier role, later role): the later role dated before the earlier one is a
#: breach. Only pairs that are unambiguous in any GMP process are listed; a
#: review may legitimately precede a release, so that pair is absent.
_STEP_BEFORE_EVENT_ROLES = (
    "investigation",
    "assessment",
    "review",
    "approval",
    "release",
    "effectiveness_check",
)


def _ordering_breaches(events: Iterable[ExtractedEvent]) -> list[ValidatorFinding]:
    """Date arithmetic over typed steps of one record.

    Two of the five persistent misses on the second blind corpus were a review
    dated before the event it reviewed and a release referencing an assessment
    finished later. Both are a comparison of two dates once the steps are
    typed, and the extractor types them. Steps are only ever compared within
    the same record (refers_to); rows without a parseable date or a record
    are skipped, because a validator that guesses is worse than none.
    """
    by_record: dict[str, list[tuple[ExtractedEvent, date]]] = {}
    for event in events:
        when = _parse_date(event.timestamp)
        if when is None or not event.refers_to or not event.role:
            continue
        by_record.setdefault(_fold(event.refers_to), []).append((event, when))

    findings: list[ValidatorFinding] = []
    for _record, steps in sorted(by_record.items()):
        def _of(role: str) -> list[tuple[ExtractedEvent, date]]:
            return [s for s in steps if s[0].role == role]

        # Any later step dated before the record's own event.
        for trigger, trigger_date in _of("event"):
            for step, step_date in steps:
                if step.role in _STEP_BEFORE_EVENT_ROLES and step_date < trigger_date:
                    findings.append(
                        _ordering_finding(
                            "step_predates_its_event",
                            "high",
                            f"'{step.description}' ist auf {step.timestamp} datiert, "
                            f"das zugehörige Ereignis '{trigger.description}' erst "
                            f"auf {trigger.timestamp}. Ein Schritt kann nicht vor dem "
                            "Ereignis liegen, das er betrifft.",
                            [step, trigger],
                        )
                    )
        # Release before the assessment or investigation it rests on.
        for release, release_date in _of("release"):
            for step, step_date in steps:
                if step.role in ("assessment", "investigation") and step_date > release_date:
                    findings.append(
                        _ordering_finding(
                            "release_before_assessment",
                            "critical",
                            f"Die Freigabe '{release.description}' ({release.timestamp}) "
                            f"liegt vor der Bewertung '{step.description}' "
                            f"({step.timestamp}). Eine Freigabe vor abgeschlossener "
                            "Bewertung ist nicht zulässig.",
                            [release, step],
                        )
                    )
        # Effectiveness check before the measure it checks was implemented.
        for check, check_date in _of("effectiveness_check"):
            for impl, impl_date in _of("implementation"):
                if check_date < impl_date:
                    findings.append(
                        _ordering_finding(
                            "effectiveness_check_before_implementation",
                            "high",
                            f"Die Wirksamkeitsprüfung '{check.description}' "
                            f"({check.timestamp}) liegt vor der Umsetzung "
                            f"'{impl.description}' ({impl.timestamp}).",
                            [check, impl],
                        )
                    )
        # First GMP use before approval or training.
        for use, use_date in _of("first_use"):
            for step, step_date in steps:
                if step.role in ("approval", "training") and step_date > use_date:
                    findings.append(
                        _ordering_finding(
                            "first_use_before_approval_or_training",
                            "high",
                            f"Die erste Anwendung '{use.description}' ({use.timestamp}) "
                            f"liegt vor '{step.description}' ({step.timestamp}).",
                            [use, step],
                        )
                    )
    return findings


def _ordering_finding(
    validator_id: str, severity: str, statement: str, rows: list[ExtractedEvent]
) -> ValidatorFinding:
    return ValidatorFinding(
        validator_id=validator_id,
        requirement_ids=sorted({rid for row in rows for rid in row.requirement_ids}),
        severity=severity,
        statement=statement,
        locations=_dedupe_locations([row.location for row in rows]),
    )


_DATE_PATTERNS = (
    re.compile(r"(?P<d>\d{1,2})\.(?P<m>\d{1,2})\.(?P<y>\d{4})"),
    re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})"),
    re.compile(r"(?P<d>\d{1,2})/(?P<m>\d{1,2})/(?P<y>\d{4})"),
)
_MONTHS_DE = {
    "januar": 1, "jan": 1, "februar": 2, "feb": 2, "märz": 3, "maerz": 3, "mrz": 3,
    "april": 4, "apr": 4, "mai": 5, "juni": 6, "jun": 6, "juli": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9, "oktober": 10,
    "okt": 10, "november": 11, "nov": 11, "dezember": 12, "dez": 12,
    "january": 1, "february": 2, "march": 3, "may": 5, "june": 6, "july": 7,
    "october": 10, "december": 12,
}
_DATE_WORDS = re.compile(r"(?P<d>\d{1,2})\.?\s+(?P<mon>[A-Za-zäöüÄÖÜ]+)\.?\s+(?P<y>\d{4})")


def _parse_date(value: str | None) -> date | None:
    """dd.mm.yyyy, ISO, dd/mm/yyyy and '2. Mai 2026'; anything else is None."""
    if not value:
        return None
    for pattern in _DATE_PATTERNS:
        match = pattern.search(value)
        if match:
            try:
                return date(int(match["y"]), int(match["m"]), int(match["d"]))
            except ValueError:
                return None
    match = _DATE_WORDS.search(value)
    if match:
        month = _MONTHS_DE.get(match["mon"].casefold())
        if month:
            try:
                return date(int(match["y"]), month, int(match["d"]))
            except ValueError:
                return None
    return None


# --- segregation of duties ----------------------------------------------------

_PERFORMER_WORDS = ("erstellt", "durchgef", "bearbeitet", "ausgef", "performed", "prepared", "author", "verfasst", "operator")
_CHECKER_WORDS = ("gepr", "freigeg", "genehm", "approved", "reviewed", "released", "qa", "zweitpr", "verified", "kontrolliert")


def _segregation_of_duties(
    signatures: Iterable[ExtractedSignature], events: Iterable[ExtractedEvent]
) -> list[ValidatorFinding]:
    """One person both performing and approving the same record.

    The person is known from the signature block; the roles from the field
    labels. A self-approval is never the only evidence of a breach on its
    own -- the finding is medium and names both fields -- but it is exactly
    the kind of thing a reviewer scanning a signature block overlooks.
    """
    performers: dict[str, list[ExtractedSignature | ExtractedEvent]] = {}
    checkers: dict[str, list[ExtractedSignature | ExtractedEvent]] = {}
    for signature in signatures:
        if signature.is_empty or not signature.signer:
            continue
        label = _fold(f"{signature.field_label} {signature.role or ''}")
        person = _fold(signature.signer)
        if any(word in label for word in _CHECKER_WORDS):
            checkers.setdefault(person, []).append(signature)
        elif any(word in label for word in _PERFORMER_WORDS):
            performers.setdefault(person, []).append(signature)
    for event in events:
        if not event.actor or not event.role:
            continue
        person = _fold(event.actor)
        if event.role in ("approval", "release", "review"):
            checkers.setdefault(person, []).append(event)
        elif event.role in ("implementation", "investigation"):
            performers.setdefault(person, []).append(event)

    findings = []
    for person in sorted(set(performers) & set(checkers)):
        rows = [*performers[person], *checkers[person]]
        shown = next(
            (r.signer for r in performers[person] if isinstance(r, ExtractedSignature) and r.signer),
            None,
        ) or next((r.actor for r in rows if isinstance(r, ExtractedEvent) and r.actor), person)
        findings.append(
            ValidatorFinding(
                validator_id="same_person_performs_and_approves",
                requirement_ids=sorted({rid for row in rows for rid in row.requirement_ids}),
                severity="medium",
                statement=(
                    f"'{shown}' hat denselben Vorgang sowohl ausgeführt bzw. erstellt als "
                    "auch geprüft oder freigegeben. Das Vier-Augen-Prinzip ist damit "
                    "nicht erkennbar gewahrt."
                ),
                locations=_dedupe_locations([row.location for row in rows]),
            )
        )
    return findings


# --- CAPA effectiveness ------------------------------------------------------

#: A deviation package carries its CAPA plan as one of its documents; the
#: obligation follows the measures, not the declared type of the package.
_CAPA_WORDS = ("capa", "korrekturma", "corrective", "preventive", "vorbeugema", "massnahme", "maßnahme")
_EFFECTIVENESS_WORDS = ("wirksamkeit", "effectiveness", "wirksamkeitsprüfung", "effectiveness check")


def _capa_effectiveness_missing(
    evidence: StructuredEvidence, context: ValidationContext
) -> list[ValidatorFinding]:
    """CAPA measures with no effectiveness check at all.

    The one miss shared by every stack on the goldstandard corpus. The
    trigger is the measure list itself: corrective measures exist, so the
    obligation to verify them exists -- whatever the package is called.
    Fires on four of the ten goldstandard cases, of which the answer key
    credits one; the other three CAPA plans are equally silent on
    effectiveness, and whether that counts as a finding for a given customer
    is a calibration question, not a reason to look away. Absent means absent everywhere -- no typed step, no
    action item, and not even the word in any chunk -- so a section the
    extractor skipped cannot produce a false alarm.
    """
    capa_measures = [
        item
        for item in evidence.action_items
        if any(
            word in _fold(f"{item.list_label} {item.item_label}")
            for word in _CAPA_WORDS
        )
    ]
    if "capa" in _fold(context.declared_document_type):
        capa_measures = list(evidence.action_items)
    if not capa_measures:
        return []
    evidence = evidence.model_copy(update={"action_items": capa_measures})
    if any(e.role == "effectiveness_check" for e in evidence.events):
        return []
    haystack = _fold(
        " ".join(
            [
                *context.chunk_texts,
                *(f"{a.list_label} {a.item_label}" for a in evidence.action_items),
            ]
        )
    )
    if any(word in haystack for word in _EFFECTIVENESS_WORDS):
        return []
    trigger = evidence.action_items[0]
    return [
        ValidatorFinding(
            validator_id="capa_effectiveness_check_missing",
            requirement_ids=sorted({rid for a in evidence.action_items for rid in a.requirement_ids}),
            severity="high",
            # Short and in both of the terms GMP practice uses: the reviewer
            # scans rule statements, and the eval matcher scores word overlap
            # against an oracle that may be written in either language.
            statement=(
                f"Im CAPA-Plan fehlt der regulatorisch geforderte Effectiveness Check "
                f"(Wirksamkeitsprüfung) für {len(evidence.action_items)} Maßnahme(n), "
                f"z. B. '{trigger.item_label}'."
            ),
            locations=_dedupe_locations([a.location for a in evidence.action_items[:3]]),
        )
    ]


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
