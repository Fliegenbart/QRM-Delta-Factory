from __future__ import annotations

from pydantic import Field

from app.schemas.domain import StrictSchema


class OODGateResult(StrictSchema):
    score: float = Field(ge=0, le=1)
    threshold: float = Field(ge=0, le=1)
    signals: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    auto_clear_blocked: bool


class CoverageGateResult(StrictSchema):
    coverage_score: float = Field(ge=0, le=1)
    required_roles: list[str] = Field(default_factory=list)
    completed_roles: list[str] = Field(default_factory=list)
    missing_roles: list[str] = Field(default_factory=list)
    failed_roles: list[str] = Field(default_factory=list)
    requirement_coverage_sufficient: bool
    high_or_critical_coverage_gap: bool
    gap_reasons: list[str] = Field(default_factory=list)
