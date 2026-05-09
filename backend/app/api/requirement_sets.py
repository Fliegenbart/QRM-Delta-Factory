from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile, status

from app.audit.events import audit_log
from app.core.security import (
    current_tenant_id,
    require_requirement_set_for_tenant,
)
from app.db.in_memory import repository
from app.schemas.domain import Criticality, Requirement, RequirementSet
from app.services.requirement_library import (
    RequirementLibraryImportError,
    RequirementLibraryService,
    RequirementSetNotFoundError,
    RequirementTenantMismatchError,
)

router = APIRouter(tags=["requirement-library"])


def get_requirement_library_service() -> RequirementLibraryService:
    return RequirementLibraryService(repository=repository, audit_log=audit_log)


@router.post(
    "/requirement-sets/import",
    response_model=RequirementSet,
    status_code=status.HTTP_201_CREATED,
)
async def import_requirement_set(
    request: Request,
    file: Annotated[UploadFile, File()],
    imported_by: Annotated[str, Form()],
) -> RequirementSet:
    content = await file.read()
    try:
        return get_requirement_library_service().import_requirement_set(
            filename=file.filename or "requirements.yaml",
            content=content,
            imported_by=imported_by,
            expected_tenant_id=current_tenant_id(request),
        )
    except RequirementLibraryImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except RequirementTenantMismatchError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/requirement-sets/{requirement_set_id}", response_model=RequirementSet)
def get_requirement_set(requirement_set_id: str, request: Request) -> RequirementSet:
    try:
        require_requirement_set_for_tenant(
            repository=repository,
            requirement_set_id=requirement_set_id,
            request=request,
        )
        requirement_set = get_requirement_library_service().get_requirement_set(requirement_set_id)
        audit_log.append(
            event_type="requirements_retrieved",
            actor_id="user_system",
            entity_type="RequirementSet",
            entity_id=requirement_set.requirement_set_id,
            tenant_id=requirement_set.tenant_id,
            payload={
                "requirement_set_id": requirement_set.requirement_set_id,
                "version": requirement_set.version,
                "requirement_count": len(requirement_set.requirements),
            },
        )
        return requirement_set
    except RequirementSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/requirement-sets/{requirement_set_id}/activate", response_model=RequirementSet)
def activate_requirement_set(requirement_set_id: str, request: Request) -> RequirementSet:
    try:
        require_requirement_set_for_tenant(
            repository=repository,
            requirement_set_id=requirement_set_id,
            request=request,
        )
        return get_requirement_library_service().activate_requirement_set(requirement_set_id)
    except RequirementSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/requirement-sets/{requirement_set_id}/deactivate", response_model=RequirementSet)
def deactivate_requirement_set(requirement_set_id: str, request: Request) -> RequirementSet:
    try:
        require_requirement_set_for_tenant(
            repository=repository,
            requirement_set_id=requirement_set_id,
            request=request,
        )
        return get_requirement_library_service().deactivate_requirement_set(requirement_set_id)
    except RequirementSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/requirements/search", response_model=list[Requirement])
def search_requirements(
    request: Request,
    document_type: Annotated[str | None, Query()] = None,
    process_area: Annotated[str | None, Query()] = None,
    criticality: Annotated[Criticality | None, Query()] = None,
) -> list[Requirement]:
    return get_requirement_library_service().search_requirements(
        tenant_id=current_tenant_id(request),
        document_type=document_type,
        process_area=process_area,
        criticality=criticality,
    )
