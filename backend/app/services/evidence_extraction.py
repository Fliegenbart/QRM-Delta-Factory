"""Structured evidence extraction: the semantic front half of the validators.

One model call per case reads the chunks into typed rows -- signatures,
measurements, specifications, action items, events -- each with a verbatim
quote and the requirement_ids it concerns. The server then resolves every
quote against the stored chunks exactly like reviewer evidence; rows whose
quotes cannot be grounded are dropped before any validator sees them. What
remains is data the deterministic layer can do arithmetic on without ever
touching prose.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.agents.providers import BaseModelProvider
from app.schemas.domain import DocumentChunk
from app.schemas.structured_evidence import StructuredEvidence

EXTRACTION_PROMPT = (
    "Du bist ein präziser Dokumenten-Extraktor für GMP-Unterlagen. Du erhältst "
    "Dokumentauszüge (chunks) und eine Liste von Anforderungen. Extrahiere "
    "strukturiert, ohne zu bewerten:\n\n"
    "1. signatures: Jedes Signatur-, Prüf- oder Freigabefeld. field_label ist "
    "die Feldbezeichnung im Dokument. is_empty=true, wenn das Feld existiert, "
    "aber keinen Unterzeichner trägt -- also leer ist, NUR ein Datum ohne "
    "Namen oder Kürzel enthält, 'siehe oben' sagt oder 'N/A' ohne Begründung. "
    "Ein Datum ist kein Unterzeichner. Gehe Signaturblöcke Feld für Feld "
    "durch; ein leeres Pflichtfeld ist ein eigener Eintrag, kein "
    "Auslassungsgrund.\n"
    "2. measurements: Jeder konkrete Messwert mit Parameter, Wert (wörtlich, "
    "inklusive Komma- oder Punktschreibweise) und Einheit.\n"
    "3. specifications: Jede deklarierte Grenze (NMT, NLT, ≤, ≥, Bereich). "
    "Benutze für parameter DENSELBEN Namen wie bei der zugehörigen Messung, "
    "damit beide zusammenfinden.\n"
    "4. action_items: NUR Positionen von Listen mit Handlungscharakter -- "
    "CAPA-Maßnahmen, Aufgaben, Korrekturmaßnahmen, also Dinge, die jemand tun "
    "muss -- einzeln, mit responsible und due_date, sofern genannt; fehlend "
    "heißt null, nicht raten. Dokumentlisten, Inhaltsverzeichnisse, "
    "Anlagenverzeichnisse, Verteilerlisten und Aufzählungen vorhandener "
    "Unterlagen sind KEINE action_items -- ein Dokument hat keinen "
    "Verantwortlichen und keine Frist.\n"
    "5. events: Datierte Handlungen (Review, Freigabe, Prüfung, Eingriff) mit "
    "timestamp, actor (Name oder Kürzel) und activity_key. Denselben "
    "activity_key bekommen nur Einträge, die dieselbe Handlung am SELBEN "
    "Objekt beschreiben -- gleiche Charge, gleiches Gerät, gleiche Probe. "
    "Nimm die Objektkennung in den Schlüssel auf (z. B. "
    "'filterintegritaetstest_OP-24-0501'); dieselbe Tätigkeit an zwei "
    "Chargen sind zwei Aktivitäten.\n\n"
    "Harte Regeln:\n"
    "- quote ist wortwörtlich und zusammenhängend aus dem genannten Chunk, mit "
    "document_id, chunk_id und page aus den Eingaben.\n"
    "- requirement_ids: die IDs der übergebenen Anforderungen, die der Eintrag "
    "betrifft (leer, wenn keine passt). Erfinde keine IDs.\n"
    "- Extrahiere vollständig: jede Zeile einer Maßnahmenliste, jedes "
    "Signaturfeld, jeden Messwert. Vollständigkeit schlägt Knappheit.\n"
    "- Keine Bewertungen, keine Findings, keine Interpretation."
)


@dataclass
class ExtractionOutcome:
    evidence: StructuredEvidence
    #: (document_id, exception) per failed per-document call.
    failures: list[tuple[str, Exception]]
    succeeded_document_ids: list[str]


class EvidenceExtractor:
    def __init__(self, *, provider: BaseModelProvider) -> None:
        self.provider = provider

    def extract(
        self,
        *,
        chunk_payload: list[dict[str, Any]],
        requirement_index: list[dict[str, str]],
        chunks: list[DocumentChunk],
    ) -> ExtractionOutcome:
        """Extract per document, so one bad call costs one document.

        The blind run showed why the single whole-case call was wrong twice
        over: extracting every row of five or six documents in one response
        ran into the output token cap on mistral (truncated, retried,
        truncated again -- truncation is deterministic at this size), and the
        one dead call silenced the entire validator layer for the case. Both
        of the corpus's zero-detection cases were exactly this. Per-document
        calls bound the output to what one document can produce, and a
        failure surfaces as a named per-document gap instead of a silent
        whole-case blackout.
        """
        by_document: dict[str, list[dict[str, Any]]] = {}
        for chunk in chunk_payload:
            by_document.setdefault(str(chunk.get("document_id")), []).append(chunk)

        merged = StructuredEvidence()
        failures: list[tuple[str, Exception]] = []
        succeeded: list[str] = []
        for document_id in sorted(by_document):
            try:
                from app.services.requirement_review import _run_with_one_reask

                raw = _run_with_one_reask(
                    self.provider,
                    EXTRACTION_PROMPT,
                    {
                        "requirements": requirement_index,
                        "chunks": by_document[document_id],
                    },
                    StructuredEvidence,
                )
                evidence = StructuredEvidence.model_validate(raw)
            except Exception as exc:  # noqa: BLE001 - recorded per document
                failures.append((document_id, exc))
                continue
            succeeded.append(document_id)
            merged = StructuredEvidence(
                signatures=[*merged.signatures, *evidence.signatures],
                measurements=[*merged.measurements, *evidence.measurements],
                specifications=[*merged.specifications, *evidence.specifications],
                action_items=[*merged.action_items, *evidence.action_items],
                events=[*merged.events, *evidence.events],
            )
        return ExtractionOutcome(
            evidence=_ground_locations(merged, chunks),
            failures=failures,
            succeeded_document_ids=succeeded,
        )


def _ground_locations(
    evidence: StructuredEvidence, chunks: list[DocumentChunk]
) -> StructuredEvidence:
    """Drop rows whose quote cannot be found in their cited chunk.

    Reuses the same quote resolver as reviewer evidence, so presentation-level
    drift (markdown emphasis, ellipses, umlaut transliteration) is repaired
    rather than fatal. A row that still cannot be grounded is removed: the
    validators' authority rests entirely on every input row being checkable.
    """
    from app.services.requirement_review import _ground_quote

    chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}

    def _grounded(rows: list[Any]) -> list[Any]:
        kept = []
        for row in rows:
            chunk = chunks_by_id.get(row.location.chunk_id)
            if chunk is None or chunk.document_id != row.location.document_id:
                continue
            resolved = _ground_quote(row.location.quote, chunk.text)
            if resolved is None:
                continue
            if not chunk.page_start <= row.location.page <= chunk.page_end:
                continue
            # A single resolved span replaces the model's rendition with the
            # exact source text; a stitched multi-fragment quote keeps the
            # model's rendition, its parts having each been grounded.
            quote = resolved[0] if len(resolved) == 1 else row.location.quote
            kept.append(
                row.model_copy(
                    update={"location": row.location.model_copy(update={"quote": quote})}
                )
            )
        return kept

    return StructuredEvidence(
        signatures=_grounded(evidence.signatures),
        measurements=_grounded(evidence.measurements),
        specifications=_grounded(evidence.specifications),
        action_items=_grounded(evidence.action_items),
        events=_grounded(evidence.events),
    )
