from __future__ import annotations

from app.schemas.domain import Document, DocumentChunk, DocumentSet, RequirementSetId, StrictSchema


class CreateDocumentSetRequest(StrictSchema):
    tenant_id: str
    requirement_set_id: RequirementSetId
    declared_document_type: str
    declared_process_area: str
    uploaded_by: str


class DocumentUploadResponse(StrictSchema):
    document_set: DocumentSet
    document: Document
    chunks: list[DocumentChunk]


class DocumentSummary(StrictSchema):
    """What a reviewer needs to tell one uploaded document from another.

    Deliberately not the full Document: storage_uri and file_hash_sha256 are
    internal and have no business crossing the API boundary just so the case
    view can print a filename.
    """

    document_id: str
    filename: str
    mime_type: str
    page_count: int
    parsing_status: str
    parsing_quality_score: float
    language: str
