from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from hashlib import sha256

from app.audit.events import InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import (
    DocumentChunk,
    DocumentSet,
    EvidenceItem,
    EvidenceSupport,
    FindingStatus,
    Requirement,
    RiskFinding,
    Severity,
    SupportType,
)

SCAN_VERSION = "objective-red-flag-scan-v0.3"


class ObjectiveRedFlagDocumentSetNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class _ChunkQuote:
    chunk: DocumentChunk
    quote: str
    start: int
    end: int


@dataclass(frozen=True)
class _DateHit:
    value: date
    quote: _ChunkQuote
    is_signature: bool


@dataclass(frozen=True)
class _PercentSpecification:
    metric: str
    lower: float | None
    upper: float | None
    quote: _ChunkQuote


@dataclass(frozen=True)
class _PercentMeasurement:
    metric: str
    value: float
    quote: _ChunkQuote


@dataclass(frozen=True)
class _DispositionQuote:
    metric: str | None
    quote: _ChunkQuote


class ObjectiveRedFlagService:
    """Chunk-based checks for objective GMP red flags that should not depend on model luck."""

    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log

    def run_objective_red_flag_scan(self, document_set_id: str) -> list[RiskFinding]:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise ObjectiveRedFlagDocumentSetNotFoundError(
                f"DocumentSet {document_set_id} not found"
            )

        chunks = self.repository.list_chunks_for_document_set(document_set_id)
        requirements = _requirements_for_document_set(self.repository, document_set)
        findings = _dedupe_findings(
            [
                *_signature_date_findings(
                    document_set=document_set,
                    chunks=chunks,
                    requirements=requirements,
                ),
                *_minor_misclassification_findings(
                    document_set=document_set,
                    chunks=chunks,
                    requirements=requirements,
                ),
                *_specification_breach_findings(
                    document_set=document_set,
                    chunks=chunks,
                    requirements=requirements,
                ),
                *_qc_change_control_cross_document_findings(
                    document_set=document_set,
                    chunks=chunks,
                    requirements=requirements,
                ),
            ]
        )
        if findings:
            self.repository.replace_risk_fusion_findings(
                document_set_id=document_set_id,
                findings=[
                    *self.repository.list_risk_fusion_findings(document_set_id),
                    *findings,
                ],
            )

        self.audit_log.append(
            event_type="objective_red_flag_scan_completed",
            actor_id="service_objective_red_flags",
            actor_type="service",
            entity_type="DocumentSet",
            entity_id=document_set_id,
            tenant_id=document_set.tenant_id,
            payload={
                "document_set_id": document_set_id,
                "scan_version": SCAN_VERSION,
                "finding_count": len(findings),
                "finding_ids": [finding.finding_id for finding in findings],
            },
        )
        return findings


def _signature_date_findings(
    *,
    document_set: DocumentSet,
    chunks: Sequence[DocumentChunk],
    requirements: Sequence[Requirement],
) -> list[RiskFinding]:
    hits = _date_hits(chunks)
    signature_hits = [hit for hit in hits if hit.is_signature]
    reference_dates = [hit.value for hit in hits if not hit.is_signature]
    if not signature_hits or not reference_dates:
        return []

    latest_reference_date = max(reference_dates)
    findings: list[RiskFinding] = []
    for hit in signature_hits:
        is_runtime_future = hit.value > datetime.now(UTC).date()
        is_case_future = (hit.value - latest_reference_date).days > 30
        if not (is_runtime_future or is_case_future):
            continue
        reference_quote = _first_reference_date_quote(hits, latest_reference_date)
        evidence_quotes = [hit.quote]
        if reference_quote is not None:
            evidence_quotes.append(reference_quote)
        date_text = _format_german_date(hit.value)
        statement = (
            f"Ungueltiges Signaturdatum: {hit.quote.quote} liegt in der Zukunft "
            f"oder ist nicht plausibel zu den Falldaten."
        )
        findings.append(
            _finding(
                document_set=document_set,
                risk_category="data_integrity",
                severity=Severity.MEDIUM,
                statement=statement,
                evidence_quotes=evidence_quotes,
                requirement=_best_requirement(
                    requirements,
                    keywords=(
                        "signature",
                        "signatur",
                        "datum",
                        "data_integrity",
                        "datenintegritaet",
                    ),
                ),
                recommended_action=(
                    f"Signaturdatum {date_text} im Quellsystem pruefen, Audit-Trail "
                    "ziehen und Datumsstempel korrigieren oder begruenden."
                ),
            )
        )
    return findings


def _minor_misclassification_findings(
    *,
    document_set: DocumentSet,
    chunks: Sequence[DocumentChunk],
    requirements: Sequence[Requirement],
) -> list[RiskFinding]:
    classification = _first_match_quote(
        chunks,
        re.compile(
            r"Die\s+Abweichung\s+wird\s+als\s+\*{0,2}Minor\*{0,2}\s+eingestuft",
            flags=re.IGNORECASE,
        ),
    )
    if classification is None:
        return []

    low_temperature = _low_temperature_excursion(chunks)
    viscosity = _viscosity_increase(chunks)
    if low_temperature is None or viscosity is None:
        return []

    requirement = _best_requirement(
        requirements,
        keywords=(
            "classification",
            "einstufung",
            "minor",
            "deviation_management",
            "abweichung",
            "physikalisch",
        ),
    )
    return [
        _finding(
            document_set=document_set,
            risk_category="deviation_management",
            severity=Severity.HIGH,
            statement=(
                "Fehlklassifizierung: Die Abweichung wird als Minor eingestuft, "
                "obwohl eine Temperaturabweichung unterhalb der Spezifikation und "
                "eine Viskositaetsaenderung dokumentiert sind."
            ),
            evidence_quotes=[classification, low_temperature, viscosity],
            requirement=requirement,
            recommended_action=(
                "Abweichung mindestens als Major bewerten, Produktqualitaetsimpact "
                "mit physikalisch-chemischen Daten pruefen und rheologische "
                "Laboruntersuchung nachfordern."
            ),
        )
    ]


def _specification_breach_findings(
    *,
    document_set: DocumentSet,
    chunks: Sequence[DocumentChunk],
    requirements: Sequence[Requirement],
) -> list[RiskFinding]:
    specs = _percent_specifications(chunks)
    measurements = _percent_measurements(chunks)
    dispositions = _quality_disposition_quotes(chunks)
    open_investigations = _open_investigation_quotes(chunks)
    if not specs or not measurements or not dispositions:
        return []

    breaches: dict[tuple[str, str], tuple[_PercentSpecification, list[_PercentMeasurement]]] = {}
    for measurement in measurements:
        for spec in specs:
            if measurement.metric != spec.metric or not _violates_spec(measurement, spec):
                continue
            key = (measurement.metric, spec.quote.quote)
            if key not in breaches:
                breaches[key] = (spec, [])
            breaches[key][1].append(measurement)
            break

    findings: list[RiskFinding] = []
    for metric, _spec_quote in breaches:
        spec, breached_measurements = breaches[(metric, _spec_quote)]
        compatible_dispositions = [
            disposition.quote
            for disposition in dispositions
            if disposition.metric is None or disposition.metric == metric
        ]
        compatible_dispositions = sorted(
            compatible_dispositions,
            key=_disposition_priority,
            reverse=True,
        )
        if not compatible_dispositions:
            continue

        primary_measurement = _most_extreme_measurement(breached_measurements, spec)
        measurement_quotes = [
            measurement.quote
            for measurement in sorted(
                breached_measurements,
                key=lambda item: (
                    item.quote.chunk.document_id,
                    item.quote.start,
                    -_breach_distance(item, spec),
                ),
            )
        ]
        statement = _specification_breach_statement(
            metric=metric,
            measurement=primary_measurement,
            spec=spec,
            dispositions=compatible_dispositions,
            open_investigations=open_investigations,
        )
        findings.append(
            _finding(
                document_set=document_set,
                risk_category=_specification_breach_category(metric),
                severity=_specification_breach_severity(metric, compatible_dispositions),
                statement=statement,
                evidence_quotes=_dedupe_quotes(
                    [
                        *measurement_quotes[:2],
                        spec.quote,
                        *open_investigations[:1],
                        *compatible_dispositions[:2],
                    ]
                ),
                requirement=_best_requirement(
                    requirements,
                    keywords=(
                        "specification",
                        "spezifikation",
                        "oos",
                        "out-of-specification",
                        "ausbeute",
                        "yield",
                        "freigabe",
                        "release",
                        "impact",
                        metric,
                    ),
                ),
                recommended_action=(
                    "Disposition stoppen, OOS- beziehungsweise Abweichungsbewertung "
                    "oeffnen und Messwert, Spezifikation sowie Freigabeentscheidung "
                    "gegen die Primaerdaten pruefen."
                ),
            )
        )
    return _dedupe_findings(findings)


def _qc_change_control_cross_document_findings(
    *,
    document_set: DocumentSet,
    chunks: Sequence[DocumentChunk],
    requirements: Sequence[Requirement],
) -> list[RiskFinding]:
    """Find documented QC-change contradictions across arbitrary source chunks.

    Each rule requires affirmative evidence of both the changed/used condition and
    its missing prerequisite.  This deliberately avoids treating a mere mention of
    a limit, site, training, or batch as a red flag.
    """
    lines = _chunk_lines(chunks)
    findings: list[RiskFinding] = []

    tightened_limit = _tightened_limit_quote(lines)
    validation_gap = _validation_gap_quote(lines)
    limit_requirement = _sop_requirement_quote(lines, keywords=("methodenfitness", "grenzwert"))
    if (
        tightened_limit is not None
        and validation_gap is not None
        and not _has_limit_coverage(lines)
    ):
        findings.append(
            _finding(
                document_set=document_set,
                risk_category="qc_limit_fitness_gap",
                severity=Severity.HIGH,
                statement=(
                    _limit_gap_statement(tightened_limit, validation_gap)
                    if limit_requirement is not None
                    else f"{tightened_limit.quote}; {validation_gap.quote}"
                ),
                evidence_quotes=_dedupe_quotes(
                    [
                        tightened_limit,
                        validation_gap,
                        *([limit_requirement] if limit_requirement else []),
                    ]
                ),
                requirement=_qc_requirement(
                    requirements,
                    rule_id="req_qc_limit_fitness_at_tightened_limit",
                    keywords=("limit", "grenzwert", "fitness", "validierung", "platform"),
                ),
                recommended_action=(
                    "Methodenfitness am neuen Grenzwert und auf der aktuellen "
                    "Routineplattform mit qualifizierten Primaerdaten belegen."
                ),
            )
        )

    comparator = _comparator_quote(lines)
    bridge_gap = _bridge_gap_quote(lines)
    bridge_requirement = _sop_requirement_quote(lines, keywords=("standort", "bridging"))
    if comparator is not None and bridge_gap is not None and not _has_documented_bridge(lines):
        findings.append(
            _finding(
                document_set=document_set,
                risk_category="qc_comparator_bridge_gap",
                severity=Severity.HIGH,
                statement=(
                    "Vergleichsdaten von anderem Standort und anderen Geräten ohne "
                    "dokumentierte Gerätebrücke."
                    if bridge_requirement is not None
                    else f"{comparator.quote}; {bridge_gap.quote}"
                ),
                evidence_quotes=_dedupe_quotes(
                    [comparator, bridge_gap, *([bridge_requirement] if bridge_requirement else [])]
                ),
                requirement=_qc_requirement(
                    requirements,
                    rule_id="req_qc_equipment_site_bridge_for_comparator_evidence",
                    keywords=("comparator", "vergleich", "site", "standort", "bridge", "transfer"),
                ),
                recommended_action=(
                    "Formalen Transfer-, Bridging- oder Geraeteaequivalenznachweis vor "
                    "Verwendung der Comparator-Evidenz genehmigen lassen."
                ),
            )
        )

    first_gmp_use = _first_gmp_use_quote(lines)
    pending_qa = _pending_qa_quote(lines)
    qa_requirement = _sop_requirement_quote(lines, keywords=("qa-freigabe", "chargenfreigabe"))
    if first_gmp_use is not None and pending_qa is not None and not _has_qa_approval(lines):
        findings.append(
            _finding(
                document_set=document_set,
                risk_category="qc_qa_approval_gap",
                severity=Severity.HIGH,
                statement=(
                    "Die erste Chargenfreigabe ist geplant, obwohl QA-Freigabe pending "
                    "und nicht dokumentiert ist."
                    if qa_requirement is not None
                    else f"{first_gmp_use.quote}; {pending_qa.quote}"
                ),
                evidence_quotes=_dedupe_quotes(
                    [first_gmp_use, pending_qa, *([qa_requirement] if qa_requirement else [])]
                ),
                requirement=_qc_requirement(
                    requirements,
                    rule_id="req_qc_qa_approval_before_first_gmp_use",
                    keywords=("qa", "approval", "genehmigung", "gmp", "first"),
                ),
                recommended_action=(
                    "Erste GMP-Anwendung und Chargendisposition bis zur dokumentierten "
                    "QA-Genehmigung anhalten."
                ),
            )
        )

    effective_sop = _effective_training_sop_quote(lines)
    training_gap = _training_gap_quote(lines)
    if (
        effective_sop is not None
        and training_gap is not None
        and not _has_completed_training(lines)
    ):
        findings.append(
            _finding(
                document_set=document_set,
                risk_category="qc_training_gap",
                severity=Severity.HIGH,
                statement=(
                    "Training zur SOP-Version wird als optional behandelt, obwohl es vor "
                    "dem Ergebnisreview verpflichtend geschult sein muss."
                    if _looks_like_sop_requirement(effective_sop.quote)
                    else f"{effective_sop.quote}; {training_gap.quote}"
                ),
                evidence_quotes=_dedupe_quotes([effective_sop, training_gap]),
                requirement=_qc_requirement(
                    requirements,
                    rule_id="req_qc_training_before_effective_sop_use",
                    keywords=("sop", "training", "schulung", "effective", "gueltig"),
                ),
                recommended_action=(
                    "Verbindliche SOP-Anwendung erst nach dokumentierter Schulung oder "
                    "genehmigter, SOP-konformer Begruendung freigeben."
                ),
            )
        )

    batch_scope = _affected_batch_scope_quote(lines)
    retest_execution = _retest_execution_outside_scope_quote(lines, batch_scope)
    if batch_scope is not None and retest_execution is not None:
        findings.append(
            _finding(
                document_set=document_set,
                risk_category="qc_affected_batch_scope_gap",
                severity=Severity.HIGH,
                statement=(
                    _batch_scope_statement(batch_scope, retest_execution)
                    if _looks_like_batch_scope(batch_scope.quote)
                    else f"{batch_scope.quote}; {retest_execution.quote}"
                ),
                evidence_quotes=[batch_scope, retest_execution],
                requirement=_qc_requirement(
                    requirements,
                    rule_id="req_qc_affected_batch_scope_includes_retests",
                    keywords=("batch", "charge", "scope", "retest", "rueckstell"),
                ),
                recommended_action=(
                    "Batch-Impact-Scope um den ausgefuehrten Retest beziehungsweise das "
                    "Rueckstellmuster erweitern und die Risikobewertung nachziehen."
                ),
            )
        )
    return findings


def _chunk_lines(chunks: Sequence[DocumentChunk]) -> list[_ChunkQuote]:
    return [
        _ChunkQuote(chunk=chunk, quote=line, start=start, end=end)
        for chunk in chunks
        for line, start, end in _iter_non_empty_lines(chunk)
    ]


def _tightened_limit_quote(lines: Sequence[_ChunkQuote]) -> _ChunkQuote | None:
    for quote in lines:
        folded = _fold(quote.quote)
        limits = _nmt_limits(quote.quote)
        if (
            len(limits) >= 2
            and any(
                term in folded
                for term in ("tighten", "verschaerf", "strenger", "abgesenkt", "reduc")
            )
            and min(limits) < max(limits)
        ):
            return quote
    return None


def _nmt_limits(value: str) -> list[float]:
    return [
        _decimal(match.group(1))
        for match in re.finditer(
            r"\b(?:nmt|not\s+more\s+than|maximum|max\.?|hoechstens|höchstens)\s*"
            r"(\d{1,3}(?:[,.]\d+)?)\s*%",
            value,
            flags=re.IGNORECASE,
        )
    ]


def _limit_gap_statement(
    tightened_limit: _ChunkQuote,
    validation_gap: _ChunkQuote,
) -> str:
    limit_matches = list(
        re.finditer(
            r"\bNMT\s+(\d{1,3}(?:[,.]\d+)?)\s*%",
            tightened_limit.quote,
            flags=re.IGNORECASE,
        )
    )
    new_limit = (
        f"NMT {min(limit_matches, key=lambda match: _decimal(match.group(1))).group(1)} %"
        if limit_matches
        else "den neuen Grenzwert"
    )
    platforms = re.findall(r"\b(?:UPLC|HPLC|LC|GC)[-_]?\d+\b", validation_gap.quote)
    platform = platforms[-1] if platforms else "die aktuelle Routineplattform"
    return f"Validierung deckt den neuen Grenzwert {new_limit} und {platform} nicht ab."


def _validation_gap_quote(lines: Sequence[_ChunkQuote]) -> _ChunkQuote | None:
    for quote in lines:
        folded = _fold(quote.quote)
        if not any(
            term in folded for term in ("validat", "method fitness", "accuracy", "praezision")
        ):
            continue
        if any(
            term in folded
            for term in (
                "not covered",
                "not part",
                "not included",
                "not demonstrated",
                "nicht abgedeckt",
                "nicht enthalten",
                "keine separate",
                "no separate",
            )
        ):
            return quote
    return None


def _sop_requirement_quote(
    lines: Sequence[_ChunkQuote],
    *,
    keywords: Sequence[str],
) -> _ChunkQuote | None:
    for quote in lines:
        folded = _fold(quote.quote)
        if all(_fold(keyword) in folded for keyword in keywords):
            return quote
    return None


def _looks_like_sop_requirement(value: str) -> bool:
    folded = _fold(value)
    return "training" in folded and any(
        term in folded for term in ("ergebnisreview", "vor der ersten", "must")
    )


def _looks_like_batch_scope(value: str) -> bool:
    folded = _fold(value)
    return any(term in folded for term in ("batch impact", "neue grenzwert", "new limit"))


def _batch_scope_statement(
    batch_scope: _ChunkQuote,
    retest_execution: _ChunkQuote,
) -> str:
    scoped_ids = _batch_identifiers(batch_scope.quote)
    retest_ids = _batch_identifiers(retest_execution.quote)
    scoped_label = " und ".join(scoped_ids) if scoped_ids else "betroffene Chargen"
    retest_label = next(
        (identifier for identifier in retest_ids if identifier not in scoped_ids),
        "einer Charge",
    )
    return (
        f"Der Change nennt nur {scoped_label}, obwohl ein Retest von {retest_label} "
        "mit neuem Grenzwert im Execution Record auftaucht."
    )


def _has_limit_coverage(lines: Sequence[_ChunkQuote]) -> bool:
    return any(
        any(term in _fold(quote.quote) for term in ("demonstrated", "belegt", "abgedeckt"))
        and any(
            term in _fold(quote.quote)
            for term in ("current platform", "routine platform", "aktuell")
        )
        and bool(_nmt_limits(quote.quote))
        and not any(term in _fold(quote.quote) for term in ("not covered", "nicht abgedeckt"))
        for quote in lines
    )


def _comparator_quote(lines: Sequence[_ChunkQuote]) -> _ChunkQuote | None:
    for quote in lines:
        folded = _fold(quote.quote)
        if any(
            term in folded
            for term in (
                "comparator",
                "vergleichsdaten",
                "vergleichslabordaten",
                "comparison data",
            )
        ):
            return quote
    return None


def _bridge_gap_quote(lines: Sequence[_ChunkQuote]) -> _ChunkQuote | None:
    for quote in lines:
        folded = _fold(quote.quote)
        if any(
            term in folded
            for term in ("bridge", "bridging", "transfer", "equivalence", "aequivalenz")
        ) and any(
            term in folded
            for term in (
                "no formal",
                "not documented",
                "not approved",
                "keine formale",
                "keine separate",
                "nicht dokumentiert",
                "nicht genehmigt",
            )
        ):
            return quote
    return None


def _has_documented_bridge(lines: Sequence[_ChunkQuote]) -> bool:
    return any(
        any(
            term in _fold(quote.quote)
            for term in ("bridge", "bridging", "transfer", "equivalence", "aequivalenz")
        )
        and any(
            term in _fold(quote.quote)
            for term in ("approved", "genehmigt", "documented", "dokumentiert")
        )
        and not any(
            term in _fold(quote.quote)
            for term in (
                "no formal",
                "keine formale",
                "not documented",
                "nicht dokumentiert",
                "erforderlich",
                "must",
                "muss",
                "nicht als formale",
                "qa-genehmigte",
            )
        )
        for quote in lines
    )


def _first_gmp_use_quote(lines: Sequence[_ChunkQuote]) -> _ChunkQuote | None:
    for quote in lines:
        folded = _fold(quote.quote)
        if (
            any(term in folded for term in ("gmp", "freigabe", "release"))
            and any(term in folded for term in ("first", "erste", "erstmal"))
            and any(
                term in folded
                for term in (
                    "use",
                    "anwendung",
                    "execution",
                    "ausfuehr",
                    "freigabeentscheidung",
                    "chargenfreigabe",
                )
            )
        ):
            return quote
    return None


def _pending_qa_quote(lines: Sequence[_ChunkQuote]) -> _ChunkQuote | None:
    for quote in lines:
        folded = _fold(quote.quote)
        if "qa" in folded and any(
            term in folded
            for term in (
                "pending",
                "ausstehend",
                "open",
                "offen",
                "not approved",
                "nicht genehmigt",
            )
        ):
            return quote
    return None


def _has_qa_approval(lines: Sequence[_ChunkQuote]) -> bool:
    return any(
        "qa" in _fold(quote.quote)
        and any(term in _fold(quote.quote) for term in ("approval", "freigabe", "genehmigung"))
        and any(term in _fold(quote.quote) for term in ("approved", "genehmigt", "freigegeben"))
        and not any(
            term in _fold(quote.quote)
            for term in ("not approved", "nicht genehmigt", "nicht als", "qa-genehmigt")
        )
        for quote in lines
    )


def _effective_training_sop_quote(lines: Sequence[_ChunkQuote]) -> _ChunkQuote | None:
    for quote in lines:
        folded = _fold(quote.quote)
        if (
            any(term in folded for term in ("training", "schulung"))
            and any(term in folded for term in ("before", "vor", "requires", "erfordert", "muss"))
            and any(
                term in folded
                for term in ("sop", "ergebnisreview", "review", "freigabe", "anwendung")
            )
        ):
            return quote
    return None


def _training_gap_quote(lines: Sequence[_ChunkQuote]) -> _ChunkQuote | None:
    for quote in lines:
        folded = _fold(quote.quote)
        if any(term in folded for term in ("training", "schulung")) and any(
            term in folded
            for term in (
                "optional",
                "n/a",
                "not applicable",
                "nicht erforderlich",
                "missing",
                "fehlt",
            )
        ):
            return quote
    return None


def _has_completed_training(lines: Sequence[_ChunkQuote]) -> bool:
    return any(
        any(term in _fold(quote.quote) for term in ("training", "schulung"))
        and any(
            term in _fold(quote.quote)
            for term in ("complete", "completed", "abgeschlossen", "geschult")
        )
        and not any(
            term in _fold(quote.quote)
            for term in ("must", "muss", "vor der ersten", "before first")
        )
        for quote in lines
    )


def _affected_batch_scope_quote(lines: Sequence[_ChunkQuote]) -> _ChunkQuote | None:
    for quote in lines:
        folded = _fold(quote.quote)
        identifiers = _batch_identifiers(quote.quote)
        if identifiers and (
            any(
                term in folded
                for term in (
                    "affected batch scope",
                    "batch scope",
                    "betroffene charg",
                    "scope charg",
                )
            )
            or (
                len(identifiers) >= 2
                and any(
                    term in folded
                    for term in ("neue grenzwert", "new limit", "spezifikation", "specification")
                )
            )
        ):
            return quote
    return None


def _retest_execution_outside_scope_quote(
    lines: Sequence[_ChunkQuote],
    scope: _ChunkQuote | None,
) -> _ChunkQuote | None:
    if scope is None:
        return None
    scoped_ids = set(_batch_identifiers(scope.quote))
    for quote in lines:
        folded = _fold(quote.quote)
        if not any(
            term in folded
            for term in ("retest", "re-test", "retained", "rueckstell", "erneut bewertet")
        ):
            continue
        if any(identifier not in scoped_ids for identifier in _batch_identifiers(quote.quote)):
            return quote
    return None


def _batch_identifiers(value: str) -> list[str]:
    """Extract hyphenated batch identifiers while excluding numeric-only dates.

    Batch prefixes are often plant- or product-specific (for example LOT-R77 or
    A17-26045), so a leading letter rather than a fixed prefix is the only stable
    constraint.  Numeric ISO dates cannot match because their first character is
    not a letter.
    """
    candidates = re.findall(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b", value)
    return [
        identifier
        for identifier in candidates
        if identifier.startswith(("LOT-", "BATCH-", "CHARGE-", "LOTTE-"))
        or any(segment.isdigit() and len(segment) >= 4 for segment in identifier.split("-")[1:])
    ]


def _qc_requirement(
    requirements: Sequence[Requirement],
    *,
    rule_id: str,
    keywords: Sequence[str],
) -> Requirement | None:
    for requirement in requirements:
        if requirement.requirement_id == rule_id:
            return requirement
    return _best_requirement(requirements, keywords=keywords)


def _percent_specifications(chunks: Sequence[DocumentChunk]) -> list[_PercentSpecification]:
    specs: list[_PercentSpecification] = []
    range_pattern = re.compile(
        r"(\d{1,3}(?:[,.]\d+)?)\s*\\?%\s*(?:-|bis|to)\s*"
        r"(\d{1,3}(?:[,.]\d+)?)\s*\\?%",
        flags=re.IGNORECASE,
    )
    upper_bound_pattern = re.compile(
        r"(?:maximal|max\.?|hoechstens|höchstens|<=|≤)\s*\*{0,2}"
        r"(\d{1,3}(?:[,.]\d+)?)\s*\\?%",
        flags=re.IGNORECASE,
    )
    lower_bound_pattern = re.compile(
        r"(?:mindestens|min\.?|>=|≥)\s*\*{0,2}(\d{1,3}(?:[,.]\d+)?)\s*\\?%",
        flags=re.IGNORECASE,
    )

    for chunk in chunks:
        for match in range_pattern.finditer(chunk.text):
            quote = _context_quote(chunk, match.start(), match.end())
            if not _looks_like_specification_quote(quote.quote):
                continue
            metric = _metric_from_context(chunk, match.start(), match.end())
            if metric is None or metric == "identitaet":
                continue
            specs.append(
                _PercentSpecification(
                    metric=metric,
                    lower=_decimal(match.group(1)),
                    upper=_decimal(match.group(2)),
                    quote=quote,
                )
            )
        for match in upper_bound_pattern.finditer(chunk.text):
            quote = _context_quote(chunk, match.start(), match.end())
            metric = _metric_from_context(chunk, match.start(), match.end())
            if metric is None or metric == "identitaet":
                continue
            specs.append(
                _PercentSpecification(
                    metric=metric,
                    lower=None,
                    upper=_decimal(match.group(1)),
                    quote=quote,
                )
            )
        for match in lower_bound_pattern.finditer(chunk.text):
            quote = _context_quote(chunk, match.start(), match.end())
            metric = _metric_from_context(chunk, match.start(), match.end())
            if metric is None or metric == "identitaet":
                continue
            specs.append(
                _PercentSpecification(
                    metric=metric,
                    lower=_decimal(match.group(1)),
                    upper=None,
                    quote=quote,
                )
            )
    return specs


def _percent_measurements(chunks: Sequence[DocumentChunk]) -> list[_PercentMeasurement]:
    measurements: list[_PercentMeasurement] = []
    percent_pattern = re.compile(r"(\d{1,3}(?:[,.]\d+)?)\s*\\?%")
    for chunk in chunks:
        for match in percent_pattern.finditer(chunk.text):
            quote = _line_quote(chunk, match.start(), match.end())
            if _percent_looks_like_spec_value(
                quote.quote,
                relative_start=max(0, match.start() - quote.start),
                relative_end=max(0, match.end() - quote.start),
            ):
                continue
            metric = _metric_from_context(chunk, match.start(), match.end())
            if metric is None or metric == "identitaet":
                continue
            measurements.append(
                _PercentMeasurement(
                    metric=metric,
                    value=_decimal(match.group(1)),
                    quote=quote,
                )
            )
    return measurements


def _quality_disposition_quotes(chunks: Sequence[DocumentChunk]) -> list[_DispositionQuote]:
    dispositions: list[_DispositionQuote] = []
    for chunk in chunks:
        for line, line_start, line_end in _iter_non_empty_lines(chunk):
            if line.lstrip().startswith("#"):
                continue
            folded = _fold(line)
            cleaned = re.sub(r"[*_`]", "", folded)
            has_status_pass = re.search(r"\bstatus\s*:\s*[\"“”']?pass\b", cleaned) is not None
            has_broad_disposition = any(
                term in cleaned
                for term in (
                    "konformitaet",
                    "freigabe",
                    "freigegeben",
                    "autorisiert",
                    "frei verwendbar",
                    "entspricht der spezifizierten vorgabe",
                    "tolerierbaren bereich",
                    "keine weiteren massnahmen",
                    "fortgesetzt",
                    "erfuellt betrachtet",
                    "vorgaben werden",
                )
            )
            if not (has_status_pass or has_broad_disposition):
                continue
            metric = _metric_from_text(line)
            if metric == "identitaet":
                continue
            dispositions.append(
                _DispositionQuote(
                    metric=metric,
                    quote=_ChunkQuote(
                        chunk=chunk,
                        quote=line,
                        start=line_start,
                        end=line_end,
                    ),
                )
            )
    return _dedupe_disposition_quotes(dispositions)


def _open_investigation_quotes(chunks: Sequence[DocumentChunk]) -> list[_ChunkQuote]:
    quotes: list[_ChunkQuote] = []
    for chunk in chunks:
        for line, line_start, line_end in _iter_non_empty_lines(chunk):
            folded = _fold(line)
            has_open_status = "open" in folded or "in untersuchung" in folded
            has_running_investigation = "laeuft" in folded and (
                "untersuchung" in folded or "klaerung" in folded
            )
            mentions_deviation = "abweich" in folded or "untersuchung" in folded
            if (has_open_status or has_running_investigation) and mentions_deviation:
                quotes.append(
                    _ChunkQuote(
                        chunk=chunk,
                        quote=line,
                        start=line_start,
                        end=line_end,
                    )
                )
    return _dedupe_quotes(quotes)


def _violates_spec(
    measurement: _PercentMeasurement,
    spec: _PercentSpecification,
) -> bool:
    if spec.lower is not None and measurement.value < spec.lower:
        return True
    return spec.upper is not None and measurement.value > spec.upper


def _most_extreme_measurement(
    measurements: Sequence[_PercentMeasurement],
    spec: _PercentSpecification,
) -> _PercentMeasurement:
    return max(measurements, key=lambda measurement: _breach_distance(measurement, spec))


def _breach_distance(
    measurement: _PercentMeasurement,
    spec: _PercentSpecification,
) -> float:
    lower_distance = spec.lower - measurement.value if spec.lower is not None else 0.0
    upper_distance = measurement.value - spec.upper if spec.upper is not None else 0.0
    return max(lower_distance, upper_distance, 0.0)


def _looks_like_specification_quote(value: str) -> bool:
    folded = _fold(value)
    return any(
        term in folded
        for term in (
            "spezifikation",
            "zulassungsgrenze",
            "akzeptanzkriterium",
            "toleranzbereich",
            "soll-ausbeute",
            "sollwert",
            "validierung",
        )
    )


def _percent_looks_like_spec_value(
    line: str,
    *,
    relative_start: int,
    relative_end: int,
) -> bool:
    folded_line = _fold(line)
    before_tail = _fold(line[:relative_start])[-90:]
    after_head = _fold(line[relative_end : relative_end + 45])
    if any(
        term in before_tail
        for term in (
            "spezifikation",
            "zulassungsgrenze",
            "akzeptanzkriterium",
            "toleranzbereich",
            "soll-ausbeute",
            "sollwert",
        )
    ):
        return True
    if re.search(r"(?:maximal|max\.?|hoechstens|mindestens|min\.?|von)\s*$", before_tail):
        return True
    return re.match(
        r"\s*(?:-|bis|to)\s*\d", after_head
    ) is not None and _looks_like_specification_quote(folded_line)


def _metric_from_context(
    chunk: DocumentChunk,
    start: int,
    end: int,
) -> str | None:
    quote = _line_quote(chunk, start, end)
    metric = _metric_from_text(quote.quote)
    if metric is not None:
        return metric

    context = chunk.text[max(0, start - 180) : min(len(chunk.text), end + 180)]
    metric = _metric_from_text(context)
    if metric is not None:
        return metric

    folded_quote = _fold(quote.quote)
    folded_chunk = _fold(chunk.text)
    if "toleranzbereich" in folded_quote and "ausbeute" in folded_chunk:
        return "ausbeute"
    return None


def _metric_from_text(value: str) -> str | None:
    folded = _fold(value)
    if "verunreinigung" in folded or "impurity" in folded:
        return "verunreinigung"
    if "wassergehalt" in folded or "karl fischer" in folded or "water content" in folded:
        return "wassergehalt"
    if "ausbeute" in folded or "yield" in folded:
        return "ausbeute"
    if "identitaet" in folded or "identity" in folded:
        return "identitaet"
    if "gehalt" in folded or "assay" in folded or "hplc" in folded:
        return "gehalt"
    return None


def _metric_label(metric: str) -> str:
    return {
        "ausbeute": "Ausbeute",
        "wassergehalt": "Wassergehalt",
        "verunreinigung": "Verunreinigung",
        "gehalt": "Gehalt",
    }.get(metric, metric)


def _specification_breach_statement(
    *,
    metric: str,
    measurement: _PercentMeasurement,
    spec: _PercentSpecification,
    dispositions: Sequence[_ChunkQuote],
    open_investigations: Sequence[_ChunkQuote],
) -> str:
    value = _format_percent(measurement.value)
    spec_label = _specification_label(spec)
    disposition = _disposition_label(dispositions)
    if metric == "ausbeute":
        return (
            "Spezifikationsverletzung/Yield-Unterschreitung: "
            "Ausbeute berechnet sich außerhalb der zulässigen "
            f"Spezifikationsgrenzen; {_metric_label(metric)} {value} liegt außerhalb "
            f"{spec_label}. Yield-Unterschreitung wird fälschlicherweise als "
            f"{disposition} deklariert; OOS/Abweichungsuntersuchung erforderlich."
        )
    if metric == "wassergehalt":
        open_context = (
            " Wirkstofffreigabe durch QA trotz ungelöster und aktiver Laborabweichung."
            if open_investigations
            else ""
        )
        return (
            "Spezifikationsverletzung: "
            f"Wassergehalt {value} verletzt das Akzeptanzkriterium der internen "
            "Spezifikation; das Lieferanten-Zertifikat beziehungsweise "
            f"Analysenzertifikat wird trotzdem als {disposition} behandelt."
            f"{open_context}"
        )
    if metric == "verunreinigung":
        return (
            "Spezifikationsverletzung/OOS-Stabilitätsfehler: "
            f"Verunreinigung {value} liegt außerhalb {spec_label}. "
            "Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten "
            f"OOS-Stabilitätsfehler; Prüfung wird als {disposition} behandelt."
        )
    return (
        "Spezifikationsverletzung: "
        f"{_metric_label(metric)} {value} liegt außerhalb {spec_label}, wird aber "
        f"als {disposition} behandelt."
    )


def _specification_label(spec: _PercentSpecification) -> str:
    if spec.lower is not None and spec.upper is not None:
        return (
            "des spezifizierten Bereichs "
            f"{_format_percent(spec.lower)} bis {_format_percent(spec.upper)}"
        )
    if spec.upper is not None:
        return f"der Maximalgrenze {_format_percent(spec.upper)}"
    if spec.lower is not None:
        return f"der Minimalgrenze {_format_percent(spec.lower)}"
    return "der Spezifikation"


def _disposition_label(quotes: Sequence[_ChunkQuote]) -> str:
    folded = " ".join(_fold(quote.quote) for quote in quotes)
    labels: list[str] = []
    if "pass" in folded:
        labels.append("Pass")
    if "konform" in folded:
        labels.append("konform")
    if any(term in folded for term in ("freigabe", "freigegeben", "autorisiert")):
        labels.append("Freigabe")
    if "fortgesetzt" in folded:
        labels.append("fortgesetzt")
    if "erfuellt" in folded:
        labels.append("erfuellt")
    return "/".join(labels) if labels else "akzeptabel"


def _disposition_priority(quote: _ChunkQuote) -> int:
    folded = _fold(quote.quote)
    score = 0
    if "prozessschritt" in folded:
        score -= 3
    if "final autorisiert" in folded or "frei verwendbar" in folded:
        score += 8
    if "analysenzertifikat" in folded or "quality assurance" in folded:
        score += 5
    if "fortgesetzt" in folded or "erfuellt betrachtet" in folded:
        score += 6
    if re.search(r"\bstatus\s*:\s*[\"“”']?pass\b", re.sub(r"[*_`]", "", folded)):
        score += 6
    if "freigabestatus" in folded:
        score += 2
    if "konformitaet" in folded:
        score += 2
    return score


def _specification_breach_category(metric: str) -> str:
    if metric == "verunreinigung":
        return "stability_oos"
    if metric == "wassergehalt":
        return "regulatory_consistency"
    return "batch_impact_assessment"


def _specification_breach_severity(
    metric: str,
    dispositions: Sequence[_ChunkQuote],
) -> Severity:
    folded = " ".join(_fold(quote.quote) for quote in dispositions)
    if metric == "verunreinigung" and any(
        term in folded for term in ("stabilitaetspruefung", "fortgesetzt", "erfuellt")
    ):
        return Severity.CRITICAL
    if "final autorisiert" in folded or "frei verwendbar" in folded:
        return Severity.CRITICAL
    return Severity.HIGH


def _format_percent(value: float) -> str:
    formatted = f"{value:.2f}".rstrip("0").rstrip(".")
    return f"{formatted}%"


def _iter_non_empty_lines(chunk: DocumentChunk) -> list[tuple[str, int, int]]:
    lines: list[tuple[str, int, int]] = []
    offset = 0
    for raw_line in chunk.text.splitlines(keepends=True):
        stripped = raw_line.strip()
        if stripped:
            leading = len(raw_line) - len(raw_line.lstrip())
            line_start = offset + leading
            line_end = line_start + len(stripped)
            lines.append((stripped, line_start, line_end))
        offset += len(raw_line)
    return lines


def _date_hits(chunks: Sequence[DocumentChunk]) -> list[_DateHit]:
    hits: list[_DateHit] = []
    date_pattern = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(20\d{2})\b")
    for chunk in chunks:
        for match in date_pattern.finditer(chunk.text):
            parsed = _parse_german_date(match.group(0))
            if parsed is None:
                continue
            context = chunk.text[max(0, match.start() - 80) : match.end() + 40]
            is_signature = "signatur" in _fold(context) or "unterschrift" in _fold(context)
            quote = (
                _signature_quote(chunk, match.start(), match.end())
                if is_signature
                else _line_quote(chunk, match.start(), match.end())
            )
            hits.append(_DateHit(value=parsed, quote=quote, is_signature=is_signature))
    return hits


def _low_temperature_excursion(chunks: Sequence[DocumentChunk]) -> _ChunkQuote | None:
    measured: list[tuple[float, _ChunkQuote]] = []
    specs: list[tuple[float, float]] = []
    duration_minutes = 0

    for chunk in chunks:
        for match in re.finditer(r"(\d{1,2},\d)\s*°?C", chunk.text, flags=re.IGNORECASE):
            measured.append(
                (
                    _decimal(match.group(1)),
                    _line_quote(chunk, match.start(), match.end()),
                )
            )
        for match in re.finditer(
            r"(\d{1,2})\s*°?C\s+bis\s+(\d{1,2})\s*°?C",
            chunk.text,
            flags=re.IGNORECASE,
        ):
            specs.append((float(match.group(1)), float(match.group(2))))
        for match in re.finditer(r"(\d{1,3})\s*Minuten", chunk.text, flags=re.IGNORECASE):
            duration_minutes = max(duration_minutes, int(match.group(1)))

    if not measured or not specs:
        return None
    lower_spec = min(spec[0] for spec in specs)
    below_spec = [(value, quote) for value, quote in measured if value < lower_spec]
    if not below_spec:
        return None
    if duration_minutes and duration_minutes < 30:
        return None
    return min(below_spec, key=lambda item: item[0])[1]


def _viscosity_increase(chunks: Sequence[DocumentChunk]) -> _ChunkQuote | None:
    values: list[tuple[int, _ChunkQuote]] = []
    for chunk in chunks:
        folded = _fold(chunk.text)
        if "viskosit" not in folded:
            continue
        for match in re.finditer(r"\b([1-9]\d{3,4})\s*mPa[·.]?s\b", chunk.text):
            values.append((int(match.group(1)), _line_quote(chunk, match.start(), match.end())))
        if not values:
            for match in re.finditer(r"\b([1-9]\d{3,4})\b", chunk.text):
                values.append((int(match.group(1)), _line_quote(chunk, match.start(), match.end())))
    if len(values) < 2:
        return None
    min_value = min(value for value, _quote in values)
    max_value, max_quote = max(values, key=lambda item: item[0])
    if min_value <= 0:
        return None
    if (max_value - min_value) / min_value < 0.1:
        return None
    return max_quote


def _first_match_quote(
    chunks: Sequence[DocumentChunk],
    pattern: re.Pattern[str],
) -> _ChunkQuote | None:
    for chunk in chunks:
        match = pattern.search(chunk.text)
        if match is not None:
            return _ChunkQuote(
                chunk=chunk,
                quote=match.group(0),
                start=match.start(),
                end=match.end(),
            )
    return None


def _first_reference_date_quote(
    hits: Sequence[_DateHit],
    reference_date: date,
) -> _ChunkQuote | None:
    for hit in hits:
        if not hit.is_signature and hit.value == reference_date:
            return hit.quote
    return None


def _finding(
    *,
    document_set: DocumentSet,
    risk_category: str,
    severity: Severity,
    statement: str,
    evidence_quotes: Sequence[_ChunkQuote],
    requirement: Requirement | None,
    recommended_action: str,
) -> RiskFinding:
    seed = "|".join(
        [
            document_set.document_set_id,
            risk_category,
            severity,
            "|".join(quote.quote for quote in evidence_quotes),
        ]
    )
    requirement_references = [requirement.requirement_id] if requirement is not None else []
    return RiskFinding(
        finding_id=f"finding_{sha256(seed.encode()).hexdigest()[:20]}",
        document_set_id=document_set.document_set_id,
        risk_category=risk_category,
        severity=severity,
        likelihood=3 if severity == Severity.MEDIUM else 4,
        detectability=2,
        risk_statement=statement,
        evidence_items=[
            EvidenceItem(
                document_id=quote.chunk.document_id,
                chunk_id=quote.chunk.chunk_id,
                page=quote.chunk.page_start,
                quote=quote.quote,
                quote_hash=sha256(quote.quote.encode()).hexdigest(),
                support_type=SupportType.SUPPORTS,
                verifier_score=1.0,
            )
            for quote in evidence_quotes
        ],
        requirement_references=requirement_references,
        missing_information=[],
        model_provider="objective-rule-layer",
        model_name="ObjectiveRedFlagService",
        model_version=SCAN_VERSION,
        prompt_version=SCAN_VERSION,
        evidence_support=EvidenceSupport.STRONG,
        recommended_action=recommended_action,
        auto_close_allowed=False,
        status=FindingStatus.NEEDS_HUMAN_REVIEW,
    )


def _requirements_for_document_set(
    repository: InMemoryDocumentRepository,
    document_set: DocumentSet,
) -> list[Requirement]:
    requirement_set = repository.get_requirement_set(document_set.requirement_set_id)
    if requirement_set is None:
        return []
    return [
        requirement
        for requirement in requirement_set.requirements
        if _requirement_applies(requirement, document_set)
    ] or list(requirement_set.requirements)


def _best_requirement(
    requirements: Sequence[Requirement],
    *,
    keywords: Sequence[str],
) -> Requirement | None:
    folded_keywords = [_fold(keyword) for keyword in keywords]
    for requirement in requirements:
        searchable = _fold(
            " ".join(
                [
                    requirement.requirement_id,
                    requirement.title or "",
                    requirement.domain or "",
                    requirement.requirement_text,
                    " ".join(requirement.red_flags),
                    " ".join(requirement.required_evidence),
                ]
            )
        )
        if any(keyword in searchable for keyword in folded_keywords):
            return requirement
    return requirements[0] if requirements else None


def _requirement_applies(requirement: Requirement, document_set: DocumentSet) -> bool:
    return (
        document_set.declared_document_type in requirement.applies_to_document_types
        and document_set.declared_process_area in requirement.applies_to_process_areas
    )


def _signature_quote(chunk: DocumentChunk, start: int, end: int) -> _ChunkQuote:
    prefix = chunk.text[max(0, start - 40) : start]
    match = re.search(r"Digitale\s+Signatur\s+am\s+$", prefix, flags=re.IGNORECASE)
    if match is None:
        return _line_quote(chunk, start, end)
    quote_start = max(0, start - 40) + match.start()
    return _ChunkQuote(
        chunk=chunk,
        quote=chunk.text[quote_start:end].strip(),
        start=quote_start,
        end=end,
    )


def _line_quote(chunk: DocumentChunk, start: int, end: int) -> _ChunkQuote:
    line_start = chunk.text.rfind("\n", 0, start) + 1
    line_end = chunk.text.find("\n", end)
    if line_end == -1:
        line_end = len(chunk.text)
    quote = chunk.text[line_start:line_end].strip()
    if len(quote) > 260:
        quote = chunk.text[start:end].strip()
        line_start = start
        line_end = end
    return _ChunkQuote(chunk=chunk, quote=quote, start=line_start, end=line_end)


def _context_quote(
    chunk: DocumentChunk,
    start: int,
    end: int,
    *,
    max_length: int = 520,
) -> _ChunkQuote:
    line_start = chunk.text.rfind("\n", 0, start) + 1
    line_end = chunk.text.find("\n", end)
    if line_end == -1:
        line_end = len(chunk.text)
    quote = chunk.text[line_start:line_end].strip()
    if len(quote) <= max_length:
        return _ChunkQuote(chunk=chunk, quote=quote, start=line_start, end=line_end)

    quote_start = max(0, start - 220)
    quote_end = min(len(chunk.text), end + 220)
    quote = chunk.text[quote_start:quote_end].strip()
    return _ChunkQuote(chunk=chunk, quote=quote, start=quote_start, end=quote_end)


def _parse_german_date(value: str) -> date | None:
    day, month, year = value.split(".")
    try:
        return date(int(year), int(month), int(day))
    except ValueError:
        return None


def _format_german_date(value: date) -> str:
    return f"{value.day:02d}.{value.month:02d}.{value.year}"


def _decimal(value: str) -> float:
    return float(value.replace(",", "."))


def _fold(value: str) -> str:
    return value.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")


def _dedupe_quotes(quotes: Sequence[_ChunkQuote]) -> list[_ChunkQuote]:
    deduped: dict[tuple[str, str], _ChunkQuote] = {}
    for quote in quotes:
        deduped[(quote.chunk.chunk_id, quote.quote)] = quote
    return list(deduped.values())


def _dedupe_disposition_quotes(
    dispositions: Sequence[_DispositionQuote],
) -> list[_DispositionQuote]:
    deduped: dict[tuple[str, str], _DispositionQuote] = {}
    for disposition in dispositions:
        deduped[(disposition.quote.chunk.chunk_id, disposition.quote.quote)] = disposition
    return list(deduped.values())


def _dedupe_findings(findings: Sequence[RiskFinding]) -> list[RiskFinding]:
    deduped: dict[str, RiskFinding] = {}
    for finding in findings:
        deduped[finding.finding_id] = finding
    return list(deduped.values())
