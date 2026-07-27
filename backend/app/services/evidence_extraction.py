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
    "aber keinen Unterzeichner trägt (leer, nur Datum, 'siehe oben', 'N/A' ohne "
    "Begründung). Ein leeres Pflichtfeld ist ein eigener Eintrag, kein "
    "Auslassungsgrund.\n"
    "2. measurements: Jeder konkrete Messwert mit Parameter, Wert (wörtlich, "
    "inklusive Komma- oder Punktschreibweise) und Einheit.\n"
    "3. specifications: Jede deklarierte Grenze (NMT, NLT, ≤, ≥, Bereich). "
    "Benutze für parameter DENSELBEN Namen wie bei der zugehörigen Messung, "
    "damit beide zusammenfinden.\n"
    "4. action_items: Jede Position einer Maßnahmen- oder Aufgabenliste "
    "(CAPA-Maßnahmen, Aufgaben) einzeln, mit responsible und due_date, sofern "
    "genannt -- fehlend heißt null, nicht raten.\n"
    "5. events: Datierte Handlungen (Review, Freigabe, Prüfung, Eingriff) mit "
    "timestamp, actor (Name oder Kürzel) und activity_key: Einträge, die "
    "dieselbe reale Tätigkeit beschreiben, bekommen denselben activity_key.\n\n"
    "Harte Regeln:\n"
    "- quote ist wortwörtlich und zusammenhängend aus dem genannten Chunk, mit "
    "document_id, chunk_id und page aus den Eingaben.\n"
    "- requirement_ids: die IDs der übergebenen Anforderungen, die der Eintrag "
    "betrifft (leer, wenn keine passt). Erfinde keine IDs.\n"
    "- Extrahiere vollständig: jede Zeile einer Maßnahmenliste, jedes "
    "Signaturfeld, jeden Messwert. Vollständigkeit schlägt Knappheit.\n"
    "- Keine Bewertungen, keine Findings, keine Interpretation."
)


class EvidenceExtractor:
    def __init__(self, *, provider: BaseModelProvider) -> None:
        self.provider = provider

    def extract(
        self,
        *,
        chunk_payload: list[dict[str, Any]],
        requirement_index: list[dict[str, str]],
        chunks: list[DocumentChunk],
    ) -> StructuredEvidence:
        raw = self.provider.run_structured(
            EXTRACTION_PROMPT,
            {"requirements": requirement_index, "chunks": chunk_payload},
            StructuredEvidence,
        )
        evidence = StructuredEvidence.model_validate(raw)
        return _ground_locations(evidence, chunks)


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
