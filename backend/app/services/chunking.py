from __future__ import annotations

from hashlib import sha256

from app.schemas.domain import DocumentChunk, DocumentId
from app.services.document_parser import ParsedDocument


def create_chunks(*, document_id: DocumentId, parsed: ParsedDocument) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for page in parsed.pages:
        text = page.text.strip()
        if not text:
            continue
        chunks.append(
            DocumentChunk(
                chunk_id=f"chunk_{document_id.removeprefix('doc_')}_p{page.page_number}",
                document_id=document_id,
                page_start=page.page_number,
                page_end=page.page_number,
                text=text,
                token_count=max(1, len(text.split())),
                extraction_confidence=page.extraction_confidence,
                bbox=None,
                source_hash=sha256(text.encode("utf-8")).hexdigest(),
            )
        )
    return chunks
