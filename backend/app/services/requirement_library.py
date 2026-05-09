from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from app.audit.events import InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import Criticality, Requirement, RequirementSet


class RequirementSetNotFoundError(Exception):
    pass


class RequirementLibraryImportError(Exception):
    pass


class RequirementTenantMismatchError(Exception):
    pass


class RequirementLibraryService:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log

    def import_requirement_set(
        self,
        *,
        filename: str,
        content: bytes,
        imported_by: str,
        expected_tenant_id: str | None = None,
    ) -> RequirementSet:
        payload = _parse_payload(filename=filename, content=content)
        payload["imported_at"] = payload.get("imported_at") or datetime.now(UTC)
        payload["imported_by"] = _with_prefix(imported_by, "user")

        try:
            requirement_set = RequirementSet.model_validate(payload)
        except ValidationError as exc:
            raise RequirementLibraryImportError(str(exc)) from exc

        if expected_tenant_id is not None and requirement_set.tenant_id != expected_tenant_id:
            raise RequirementTenantMismatchError(
                "RequirementSet tenant does not match authenticated tenant"
            )

        self.repository.create_requirement_set(requirement_set)
        self.audit_log.append(
            event_type="requirement_set_imported",
            actor_id=requirement_set.imported_by,
            entity_type="RequirementSet",
            entity_id=requirement_set.requirement_set_id,
            payload={
                "name": requirement_set.name,
                "version": requirement_set.version,
                "requirement_count": len(requirement_set.requirements),
                "active": requirement_set.active,
            },
        )
        return requirement_set

    def get_requirement_set(self, requirement_set_id: str) -> RequirementSet:
        requirement_set = self.repository.get_requirement_set(requirement_set_id)
        if requirement_set is None:
            raise RequirementSetNotFoundError(f"RequirementSet {requirement_set_id} not found")
        return requirement_set

    def activate_requirement_set(self, requirement_set_id: str) -> RequirementSet:
        requirement_set = self.get_requirement_set(requirement_set_id)
        updated = requirement_set.model_copy(update={"active": True})
        self.repository.update_requirement_set(updated)
        self.audit_log.append(
            event_type="requirement_set_activated",
            actor_id=updated.imported_by,
            entity_type="RequirementSet",
            entity_id=updated.requirement_set_id,
            payload={"version": updated.version},
        )
        return updated

    def deactivate_requirement_set(self, requirement_set_id: str) -> RequirementSet:
        requirement_set = self.get_requirement_set(requirement_set_id)
        updated = requirement_set.model_copy(update={"active": False})
        self.repository.update_requirement_set(updated)
        self.audit_log.append(
            event_type="requirement_set_deactivated",
            actor_id=updated.imported_by,
            entity_type="RequirementSet",
            entity_id=updated.requirement_set_id,
            payload={"version": updated.version},
        )
        return updated

    def search_requirements(
        self,
        *,
        tenant_id: str | None = None,
        document_type: str | None = None,
        process_area: str | None = None,
        criticality: Criticality | None = None,
    ) -> list[Requirement]:
        requirements = self.repository.search_requirements(
            tenant_id=tenant_id,
            document_type=document_type,
            process_area=process_area,
            criticality=criticality,
        )
        self.audit_log.append(
            event_type="requirements_retrieved",
            actor_id="user_system",
            entity_type="RequirementSearch",
            entity_id="requirements_search",
            payload={
                "document_type": document_type,
                "process_area": process_area,
                "criticality": criticality,
                "result_count": len(requirements),
            },
        )
        return requirements


def _parse_payload(*, filename: str, content: bytes) -> dict[str, Any]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RequirementLibraryImportError("Requirement import file must be UTF-8 text") from exc

    suffix = Path(filename).suffix.lower()
    try:
        if suffix == ".json":
            loaded = json.loads(text)
        elif suffix in {".yaml", ".yml"}:
            loaded = yaml.safe_load(text)
        else:
            raise RequirementLibraryImportError("Requirement import must be YAML or JSON")
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise RequirementLibraryImportError(f"Could not parse requirement import: {exc}") from exc

    if not isinstance(loaded, dict):
        raise RequirementLibraryImportError("Requirement import root must be an object")
    return loaded


def _with_prefix(value: str, prefix: str) -> str:
    expected = f"{prefix}_"
    return value if value.startswith(expected) else f"{expected}{value}"
