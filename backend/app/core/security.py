from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, Response

from app.core.config import get_settings
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import DocumentSet, RequirementSet, RiskFinding

PUBLIC_PATHS = {"/health"}


async def api_key_auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    settings = get_settings()
    key_map = settings.api_key_to_tenant_id()
    if request.url.path in PUBLIC_PATHS or not key_map:
        request.state.tenant_id = None
        return await call_next(request)

    api_key = request.headers.get("X-API-Key")
    tenant_id = key_map.get(api_key or "")
    if tenant_id is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing or invalid API key"},
        )

    request.state.tenant_id = tenant_id
    return await call_next(request)


def current_tenant_id(request: Request) -> str | None:
    value = getattr(request.state, "tenant_id", None)
    return str(value) if value else None


def require_document_set_for_tenant(
    *,
    repository: InMemoryDocumentRepository,
    document_set_id: str,
    request: Request,
) -> DocumentSet:
    document_set = repository.get_document_set(document_set_id)
    tenant_id = current_tenant_id(request)
    if document_set is None or (tenant_id is not None and document_set.tenant_id != tenant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DocumentSet {document_set_id} not found",
        )
    return document_set


def require_requirement_set_for_tenant(
    *,
    repository: InMemoryDocumentRepository,
    requirement_set_id: str,
    request: Request,
) -> RequirementSet:
    requirement_set = repository.get_requirement_set(requirement_set_id)
    tenant_id = current_tenant_id(request)
    if requirement_set is None or (
        tenant_id is not None and requirement_set.tenant_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RequirementSet {requirement_set_id} not found",
        )
    return requirement_set


def require_finding_for_tenant(
    *,
    repository: InMemoryDocumentRepository,
    finding_id: str,
    request: Request,
) -> RiskFinding:
    finding = repository.find_risk_finding(finding_id)
    tenant_id = current_tenant_id(request)
    if finding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finding {finding_id} not found",
        )
    document_set = repository.get_document_set(finding.document_set_id)
    if document_set is None or (tenant_id is not None and document_set.tenant_id != tenant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finding {finding_id} not found",
        )
    return finding


def enforce_request_tenant(
    *,
    request: Request,
    requested_tenant_id: str,
) -> None:
    tenant_id = current_tenant_id(request)
    if tenant_id is not None and requested_tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated tenant cannot access requested tenant",
        )
