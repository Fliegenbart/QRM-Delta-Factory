from __future__ import annotations

from pydantic import Field, model_validator

from app.schemas.domain import AdversarialChallenge, ModelRun, RiskFinding, StrictSchema


class CoverageSummary(StrictSchema):
    agent_id: str = Field(min_length=1)
    role: str = Field(min_length=1)
    coverage_summary: str = Field(min_length=1)
    finding_count: int = Field(ge=0)


class ReviewerAgentOutput(StrictSchema):
    findings: list[RiskFinding] = Field(default_factory=list)
    coverage_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def findings_must_have_evidence(self) -> ReviewerAgentOutput:
        for finding in self.findings:
            if not finding.evidence_items:
                raise ValueError("Reviewer findings must include at least one EvidenceItem")
        return self


class PrimaryReviewResponse(StrictSchema):
    document_set_id: str
    findings: list[RiskFinding]
    model_runs: list[ModelRun]
    failed_model_runs: list[ModelRun]
    coverage_summaries: list[CoverageSummary]


class AdversarialReviewResponse(StrictSchema):
    document_set_id: str
    new_findings: list[RiskFinding] = Field(default_factory=list)
    additional_findings: list[RiskFinding]
    challenged_findings: list[AdversarialChallenge]
    challenged_no_issue_claims: list[AdversarialChallenge]
    unresolved_questions: list[str]
    escalation_reasons: list[str] = Field(default_factory=list)
    risk_fusion_findings: list[RiskFinding]
