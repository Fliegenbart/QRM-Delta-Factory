from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

DocumentSetId = Annotated[str, StringConstraints(pattern=r"^ds_[A-Za-z0-9_-]+$")]
TenantId = Annotated[str, StringConstraints(pattern=r"^tenant_[A-Za-z0-9_-]+$")]
DocumentId = Annotated[str, StringConstraints(pattern=r"^doc_[A-Za-z0-9_-]+$")]
ChunkId = Annotated[str, StringConstraints(pattern=r"^chunk_[A-Za-z0-9_-]+$")]
ClaimId = Annotated[str, StringConstraints(pattern=r"^claim_[A-Za-z0-9_-]+$")]
RequirementId = Annotated[str, StringConstraints(pattern=r"^req_[A-Za-z0-9_-]+$")]
RequirementSetId = Annotated[str, StringConstraints(pattern=r"^rset_[A-Za-z0-9_-]+$")]
FindingId = Annotated[str, StringConstraints(pattern=r"^finding_[A-Za-z0-9_-]+$")]
ChallengeId = Annotated[str, StringConstraints(pattern=r"^challenge_[A-Za-z0-9_-]+$")]
ReviewPackId = Annotated[str, StringConstraints(pattern=r"^rpack_[A-Za-z0-9_-]+$")]
PipelineRunId = Annotated[str, StringConstraints(pattern=r"^prun_[A-Za-z0-9_-]+$")]
ModelRunId = Annotated[str, StringConstraints(pattern=r"^run_[A-Za-z0-9_-]+$")]
ReviewId = Annotated[str, StringConstraints(pattern=r"^review_[A-Za-z0-9_-]+$")]
UserId = Annotated[str, StringConstraints(pattern=r"^user_[A-Za-z0-9_-]+$")]
ReviewerId = Annotated[str, StringConstraints(pattern=r"^reviewer_[A-Za-z0-9_-]+$")]
Sha256Hash = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DocumentSetStatus(StrEnum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    READY_FOR_ORCHESTRATION = "ready_for_orchestration"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    FAILED = "failed"
    ARCHIVED = "archived"


class ParsingStatus(StrEnum):
    PENDING = "pending"
    PARSED = "parsed"
    FAILED = "failed"


class ClaimType(StrEnum):
    BATCH_IDENTIFIER = "batch_identifier"
    DEVIATION_DESCRIPTION = "deviation_description"
    ROOT_CAUSE = "root_cause"
    IMPACT_ASSESSMENT = "impact_assessment"
    CAPA_ACTION = "capa_action"
    QA_APPROVAL = "qa_approval"
    EFFECTIVENESS_CHECK = "effectiveness_check"
    DATE_OR_DEADLINE = "date_or_deadline"
    RESPONSIBLE_PARTY = "responsible_party"
    ACCEPTANCE_CRITERION = "acceptance_criterion"
    TEST_RESULT = "test_result"
    MISSING_OR_UNCLEAR = "missing_or_unclear"


class RequirementSourceType(StrEnum):
    INTERNAL_SOP = "internal_sop"
    GUIDELINE = "guideline"
    REGULATION = "regulation"
    CHECKLIST = "checklist"
    PRODUCT_CONTROL_STRATEGY = "product_control_strategy"


class Criticality(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class EvidenceSupport(StrEnum):
    STRONG = "strong"
    PARTIAL = "partial"
    WEAK = "weak"
    NONE = "none"


class SupportType(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CONTEXTUAL = "contextual"


class FindingStatus(StrEnum):
    OPEN = "open"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    REQUEST_MORE_INFO = "request_more_info"
    CLOSED = "closed"


class ModelRunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ReviewDecisionValue(StrEnum):
    CONFIRM = "confirm"
    DOWNGRADE = "downgrade"
    REJECT = "reject"
    REJECT_FALSE_POSITIVE = "reject_false_positive"
    SEVERITY_INCORRECT = "severity_incorrect"
    EVIDENCE_INCORRECT = "evidence_incorrect"
    REQUIREMENT_INCORRECT = "requirement_incorrect"
    MISSED_FINDING = "missed_finding"
    REQUEST_MORE_INFO = "request_more_info"
    REQUEST_MORE_INFORMATION = "request_more_information"
    LINK_TO_CAPA = "link_to_capa"
    ESCALATE_TO_QA = "escalate_to_qa"


class BoundingBox(StrictSchema):
    page: int = Field(ge=1)
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)


class TokenUsage(StrictSchema):
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)

    @model_validator(mode="after")
    def total_must_match_parts(self) -> TokenUsage:
        if self.total_tokens != self.input_tokens + self.output_tokens:
            raise ValueError("total_tokens must equal input_tokens + output_tokens")
        return self


class EvidenceItem(StrictSchema):
    document_id: DocumentId
    chunk_id: ChunkId
    page: int = Field(ge=1)
    quote: str = Field(min_length=1)
    quote_hash: Sha256Hash
    support_type: SupportType
    verifier_score: float = Field(ge=0, le=1)


class DocumentSet(StrictSchema):
    document_set_id: DocumentSetId
    tenant_id: TenantId
    requirement_set_id: RequirementSetId
    upload_timestamp: datetime
    document_ids: list[DocumentId] = Field(default_factory=list)
    declared_document_type: str = Field(min_length=1)
    declared_process_area: str = Field(min_length=1)
    uploaded_by: UserId
    status: DocumentSetStatus


class Document(StrictSchema):
    document_id: DocumentId
    document_set_id: DocumentSetId
    filename: str = Field(min_length=1)
    file_hash_sha256: Sha256Hash
    mime_type: str = Field(min_length=1)
    page_count: int = Field(ge=1)
    storage_uri: str = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    parsing_status: ParsingStatus
    parsing_quality_score: float = Field(ge=0, le=1)
    language: str = Field(min_length=2, max_length=12)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(StrictSchema):
    chunk_id: ChunkId
    document_id: DocumentId
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    text: str = Field(min_length=1)
    token_count: int = Field(ge=1)
    extraction_confidence: float = Field(ge=0, le=1)
    bbox: BoundingBox | None = None
    source_hash: Sha256Hash

    @model_validator(mode="after")
    def page_end_must_not_precede_start(self) -> DocumentChunk:
        if self.page_end < self.page_start:
            raise ValueError("page_end must be greater than or equal to page_start")
        return self


class Claim(StrictSchema):
    claim_id: ClaimId
    document_id: DocumentId
    chunk_id: ChunkId
    page: int = Field(ge=1)
    claim_type: ClaimType
    normalized_subject: str = Field(min_length=1)
    normalized_predicate: str = Field(min_length=1)
    normalized_object: str = Field(min_length=1)
    raw_text_quote: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    dependencies: list[ClaimId] = Field(default_factory=list)
    created_by_model: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)


class Requirement(StrictSchema):
    requirement_id: RequirementId
    title: str | None = None
    domain: str | None = None
    knowledge_packs: list[str] = Field(default_factory=list)
    applies_to_agents: list[str] = Field(default_factory=list)
    applies_when_signals_present: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    required_reviewer_roles: list[str] = Field(default_factory=list)
    source_type: RequirementSourceType
    source_name: str = Field(min_length=1)
    source_version: str = Field(min_length=1)
    section: str = Field(min_length=1)
    requirement_text: str = Field(min_length=1)
    applies_to_document_types: list[str] = Field(min_length=1)
    applies_to_process_areas: list[str] = Field(min_length=1)
    criticality: Criticality
    required_evidence: list[str] = Field(default_factory=list)
    auto_close_allowed: bool
    effective_from: datetime
    effective_to: datetime | None = None

    @model_validator(mode="after")
    def high_and_critical_require_evidence(self) -> Requirement:
        if (
            self.criticality in {Criticality.CRITICAL, Criticality.HIGH}
            and not self.required_evidence
        ):
            raise ValueError(
                "required_evidence must not be empty for high or critical requirements"
            )
        return self

    @model_validator(mode="after")
    def effective_to_must_be_after_effective_from(self) -> Requirement:
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be after effective_from")
        return self


class RequirementSet(StrictSchema):
    requirement_set_id: RequirementSetId
    tenant_id: TenantId
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    imported_at: datetime
    imported_by: UserId
    active: bool
    requirements: list[Requirement] = Field(min_length=1)

    @model_validator(mode="after")
    def requirement_ids_must_be_unique(self) -> RequirementSet:
        requirement_ids = [requirement.requirement_id for requirement in self.requirements]
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError("requirement_id values must be unique within a RequirementSet")
        return self


class FindingVerificationResult(StrictSchema):
    finding_id: FindingId
    evidence_support: EvidenceSupport
    quote_exists: bool
    quote_matches_chunk: bool
    requirement_applicable: bool
    unsupported_claims: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    verifier_rationale: str = Field(min_length=1)
    verifier_model_run_id: ModelRunId | None = None
    deterministic_checks_passed: bool


class RiskFinding(StrictSchema):
    finding_id: FindingId
    document_set_id: DocumentSetId
    risk_category: str = Field(min_length=1)
    severity: Severity
    likelihood: int = Field(ge=1, le=5)
    detectability: int = Field(ge=1, le=5)
    risk_statement: str = Field(min_length=1)
    evidence_items: list[EvidenceItem] = Field(min_length=1)
    requirement_references: list[RequirementId] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    model_provider: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    evidence_support: EvidenceSupport
    recommended_action: str = Field(min_length=1)
    auto_close_allowed: bool
    status: FindingStatus
    verification_result: FindingVerificationResult | None = None

    @field_validator("auto_close_allowed")
    @classmethod
    def high_or_critical_cannot_auto_close(cls, value: bool, info: Any) -> bool:
        severity = info.data.get("severity")
        if value and severity in {Severity.CRITICAL, Severity.HIGH}:
            raise ValueError("critical and high findings cannot be auto-closed")
        return value

    @model_validator(mode="after")
    def evidence_support_must_match_evidence_items(self) -> RiskFinding:
        if self.evidence_support == EvidenceSupport.NONE and self.evidence_items:
            raise ValueError("evidence_support none cannot include evidence_items")
        return self


class AdversarialChallenge(StrictSchema):
    challenge_id: ChallengeId
    document_set_id: DocumentSetId
    target_type: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    agent_role: str = Field(min_length=1)
    severity: Severity
    challenge_statement: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    human_review_required: bool
    created_at: datetime

    @model_validator(mode="after")
    def challenge_requires_support_or_named_gap(self) -> AdversarialChallenge:
        if not self.evidence_items and not self.missing_evidence:
            raise ValueError(
                "adversarial challenges require evidence_items or explicit missing_evidence"
            )
        return self

    @model_validator(mode="after")
    def high_or_critical_challenge_requires_human_review(
        self,
    ) -> AdversarialChallenge:
        if self.severity in {Severity.CRITICAL, Severity.HIGH} and not self.human_review_required:
            raise ValueError("high and critical adversarial challenges require human review")
        return self


class ModelRun(StrictSchema):
    model_run_id: ModelRunId
    agent_id: str = Field(default="not_recorded", min_length=1)
    agent_role: str = Field(default="not_recorded", min_length=1)
    provider: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    configured_model_id: str = Field(default="not_recorded", min_length=1)
    prompt_version: str = Field(min_length=1)
    requirement_ids: list[RequirementId] = Field(default_factory=list)
    requirement_package_hash: Sha256Hash | None = Field(default=None)
    knowledge_pack_ids: list[str] = Field(default_factory=list)
    missing_knowledge_pack_ids: list[str] = Field(default_factory=list)
    case_signals: list[str] = Field(default_factory=list)
    calibration_example_ids: list[str] = Field(default_factory=list)
    calibration_pack_hash: Sha256Hash | None = Field(default=None)
    input_hash: Sha256Hash
    output_hash: Sha256Hash
    started_at: datetime
    completed_at: datetime | None = None
    latency_ms: int | None = Field(default=None, ge=0)
    token_usage: TokenUsage
    status: ModelRunStatus

    @model_validator(mode="after")
    def completed_at_must_be_after_started_at(self) -> ModelRun:
        if self.completed_at is not None and self.completed_at < self.started_at:
            raise ValueError("completed_at must be after started_at")
        return self


class RawModelOutputRecord(StrictSchema):
    model_run_id: ModelRunId
    output_hash: Sha256Hash
    raw_output: str = Field(min_length=1)
    encrypted: bool


class ReviewDecision(StrictSchema):
    review_id: ReviewId
    finding_id: FindingId
    reviewer_id: ReviewerId
    decision: ReviewDecisionValue
    rationale: str = Field(min_length=1)
    created_at: datetime
