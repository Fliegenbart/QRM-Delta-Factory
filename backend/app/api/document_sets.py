from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile, status

from app.audit.events import audit_log
from app.core.config import get_settings
from app.core.security import (
    current_tenant_id,
    enforce_request_tenant,
    require_document_set_for_tenant,
)
from app.db.in_memory import repository
from app.schemas.domain import DocumentSet
from app.schemas.ingestion import CreateDocumentSetRequest, DocumentUploadResponse
from app.services.document_parser import ParserRegistry
from app.services.ingestion import (
    DocumentIngestionService,
    DocumentSetNotFoundError,
    RequirementSetInactiveError,
)
from app.storage.local import LocalFilesystemStorage

router = APIRouter(prefix="/document-sets", tags=["document-sets"])


def get_ingestion_service() -> DocumentIngestionService:
    settings = get_settings()
    return DocumentIngestionService(
        repository=repository,
        storage=LocalFilesystemStorage(Path(settings.local_storage_root)),
        parser_registry=ParserRegistry(),
        audit_log=audit_log,
        quality_threshold=settings.parsing_quality_threshold,
    )


@router.get("/{document_set_id}", response_model=DocumentSet)
def get_document_set(document_set_id: str, http_request: Request) -> DocumentSet:
    return require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=http_request,
    )


@router.delete("/{document_set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_set(document_set_id: str, http_request: Request) -> Response:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=http_request,
    )
    repository.delete_document_set(document_set_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", response_model=list[DocumentSet])
def list_document_sets(http_request: Request) -> list[DocumentSet]:
    return repository.list_document_sets(tenant_id=current_tenant_id(http_request))


@router.post("", response_model=DocumentSet, status_code=status.HTTP_201_CREATED)
def create_document_set(request: CreateDocumentSetRequest, http_request: Request) -> DocumentSet:
    enforce_request_tenant(request=http_request, requested_tenant_id=request.tenant_id)
    try:
        return get_ingestion_service().create_document_set(request)
    except RequirementSetInactiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.post(
    "/{document_set_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    document_set_id: str,
    http_request: Request,
    file: Annotated[UploadFile, File()],
    uploaded_by: Annotated[str, Form()],
) -> DocumentUploadResponse:
    require_document_set_for_tenant(
        repository=repository,
        document_set_id=document_set_id,
        request=http_request,
    )
    content = await file.read()
    mime_type = file.content_type or "application/octet-stream"
    filename = file.filename or "uploaded-document"
    try:
        return get_ingestion_service().upload_document(
            document_set_id=document_set_id,
            filename=filename,
            mime_type=mime_type,
            content=content,
            uploaded_by=uploaded_by,
        )
    except DocumentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
