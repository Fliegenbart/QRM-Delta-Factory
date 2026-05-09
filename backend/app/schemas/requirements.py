from __future__ import annotations

from app.schemas.domain import Requirement, RequirementSet, StrictSchema


class RequirementSearchResponse(StrictSchema):
    requirements: list[Requirement]


class RequirementSetImportResponse(StrictSchema):
    requirement_set: RequirementSet
