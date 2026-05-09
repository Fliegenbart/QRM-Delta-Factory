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
