from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from app.audit.events import InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import (
    Document,
    DocumentSet,
    DocumentSetStatus,
    ParsingStatus,
)
from app.schemas.ingestion import CreateDocumentSetRequest, DocumentUploadResponse
from app.services.chunking import create_chunks
from app.services.document_parser import ParsedDocument, ParserError, ParserRegistry
from app.services.document_quality import score_parsing_quality
from app.storage.local import StorageBackend


class DocumentSetNotFoundError(Exception):
    pass


class RequirementSetInactiveError(Exception):
    pass


class DocumentIngestionService:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        storage: StorageBackend,
        parser_registry: ParserRegistry,
        audit_log: InMemoryAuditLog,
        quality_threshold: float,
    ) -> None:
        self.repository = repository
        self.storage = storage
        self.parser_registry = parser_registry
        self.audit_log = audit_log
        self.quality_threshold = quality_threshold

    def create_document_set(self, request: CreateDocumentSetRequest) -> DocumentSet:
        if not self.repository.is_active_requirement_set(request.requirement_set_id):
            raise RequirementSetInactiveError(
                f"RequirementSet {request.requirement_set_id} is not active"
            )

        document_set = DocumentSet(
            document_set_id=f"ds_{uuid4().hex}",
            tenant_id=_with_prefix(request.tenant_id, "tenant"),
            requirement_set_id=request.requirement_set_id,
            upload_timestamp=datetime.now(UTC),
            document_ids=[],
            declared_document_type=request.declared_document_type,
            declared_process_area=request.declared_process_area,
            uploaded_by=_with_prefix(request.uploaded_by, "user"),
            status=DocumentSetStatus.UPLOADED,
        )
        self.repository.create_document_set(document_set)
        self.audit_log.append(
            event_type="document_set_created",
            actor_id=document_set.uploaded_by,
            entity_type="DocumentSet",
            entity_id=document_set.document_set_id,
            payload={"tenant_id": document_set.tenant_id},
        )
        return document_set

    def upload_document(
        self,
        *,
        document_set_id: str,
        filename: str,
        mime_type: str,
        content: bytes,
        uploaded_by: str,
    ) -> DocumentUploadResponse:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise DocumentSetNotFoundError(f"DocumentSet {document_set_id} not found")

        document_id = f"doc_{uuid4().hex}"
        file_hash = sha256(content).hexdigest()
        storage_key = f"{document_set_id}/{document_id}/{Path(filename).name}"
        storage_uri = self.storage.put_object(key=storage_key, content=content)
        self.audit_log.append(
            event_type="document_uploaded",
            actor_id=_with_prefix(uploaded_by, "user"),
            entity_type="Document",
            entity_id=document_id,
            tenant_id=document_set.tenant_id,
            input_hash=file_hash,
            payload={
                "document_set_id": document_set_id,
                "filename": filename,
                "sha256": file_hash,
            },
        )

        parser_error: str | None = None
        try:
            parser = self.parser_registry.for_filename(filename, mime_type)
            parsed = parser.parse(filename=filename, content=content)
            parser_error = parsed.error
        except ParserError as exc:
            parser_error = str(exc)
            parsed = ParsedDocument(pages=[], parser_version="parser-error", error=parser_error)

        quality_score = score_parsing_quality(parsed, parser_error=parser_error)
        chunks = create_chunks(document_id=document_id, parsed=parsed)
        parsing_status = (
            ParsingStatus.FAILED if parser_error and not chunks else ParsingStatus.PARSED
        )
        set_status = (
            DocumentSetStatus.NEEDS_HUMAN_REVIEW
            if quality_score < self.quality_threshold
            else DocumentSetStatus.READY_FOR_ORCHESTRATION
        )
        page_count = max(1, len(parsed.pages))

        document = Document(
            document_id=document_id,
            document_set_id=document_set_id,
            filename=filename,
            file_hash_sha256=file_hash,
            mime_type=mime_type,
            page_count=page_count,
            storage_uri=storage_uri,
            parser_version=parsed.parser_version,
            parsing_status=parsing_status,
            parsing_quality_score=quality_score,
            language="en",
            metadata={"parser_error": parser_error} if parser_error else {},
        )
        self.repository.add_document(document=document, chunks=chunks)
        updated_set = self.repository.get_document_set(document_set_id)
        assert updated_set is not None
        updated_set = updated_set.model_copy(update={"status": set_status})
        self.repository.update_document_set(updated_set)
        self.audit_log.append(
            event_type="document_parsed",
            actor_id=_with_prefix(uploaded_by, "user"),
            entity_type="Document",
            entity_id=document_id,
            tenant_id=document_set.tenant_id,
            payload={
                "document_set_id": document_set_id,
                "parser_version": parsed.parser_version,
                "parsing_status": parsing_status,
                "quality_score": quality_score,
                "parser_error": parser_error,
            },
        )
        self.audit_log.append(
            event_type="chunks_created",
            actor_id=_with_prefix(uploaded_by, "user"),
            entity_type="Document",
            entity_id=document_id,
            tenant_id=document_set.tenant_id,
            payload={
                "document_set_id": document_set_id,
                "chunk_count": len(chunks),
                "chunk_ids": [chunk.chunk_id for chunk in chunks],
                "chunk_source_hashes": [chunk.source_hash for chunk in chunks],
            },
        )
        self.audit_log.append(
            event_type="document_parser_run",
            actor_id=_with_prefix(uploaded_by, "user"),
            entity_type="Document",
            entity_id=document_id,
            tenant_id=document_set.tenant_id,
            payload={
                "parser_version": parsed.parser_version,
                "parsing_status": parsing_status,
                "quality_score": quality_score,
                "chunk_count": len(chunks),
                "parser_error": parser_error,
            },
        )
        return DocumentUploadResponse(document_set=updated_set, document=document, chunks=chunks)


def _with_prefix(value: str, prefix: str) -> str:
    expected = f"{prefix}_"
    return value if value.startswith(expected) else f"{expected}{value}"
