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

SCAN_VERSION = "objective-red-flag-scan-v0.1"


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
    return (
        value.lower()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )


def _dedupe_findings(findings: Sequence[RiskFinding]) -> list[RiskFinding]:
    deduped: dict[str, RiskFinding] = {}
    for finding in findings:
        deduped[finding.finding_id] = finding
    return list(deduped.values())
