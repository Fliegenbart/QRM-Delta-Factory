from __future__ import annotations

import json
import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any

from app.agents.prompt_templates import PromptTemplate, PromptTemplateLoader
from app.agents.providers import (
    AnthropicProvider,
    BaseModelProvider,
    MistralProvider,
    MockProvider,
    OpenAIProvider,
    ProviderRuntimeOptions,
)
from app.audit.events import InMemoryAuditLog
from app.core.config import Settings, get_settings
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.calibration import CalibrationPromptExample
from app.schemas.domain import (
    Claim,
    DocumentSet,
    EvidenceItem,
    ModelRun,
    ModelRunStatus,
    RawModelOutputRecord,
    Requirement,
    RiskFinding,
    SupportType,
    TokenUsage,
)
from app.schemas.review import CoverageSummary, PrimaryReviewResponse, ReviewerAgentOutput
from app.services.review_calibration import ReviewCalibrationService
from app.verifiers.evidence import EvidenceVerifierService


class PrimaryReviewDocumentSetNotFoundError(Exception):
    pass


class MockModelProvider(MockProvider):
    def __init__(self, *, delay_seconds: float = 0.0) -> None:
        super().__init__(
            model_name="mock-reviewer",
            model_version="0.1.0",
            configured_model_id="mock-reviewer-v0.1",
            prompt_version="mock-primary-reviewer-v0.1",
            delay_seconds=delay_seconds,
        )

    def _run_structured_once(
        self,
        *,
        prompt: str,
        input_schema: dict[str, Any],
        output_schema: type[Any],
    ) -> dict[str, Any]:
        role = str(input_schema["agent_role"])
        document_set_id = str(input_schema["document_set_id"])
        claims = list(input_schema["claims"])
        requirements = list(input_schema["requirements"])
        findings = _mock_findings_for_role(
            role=role,
            document_set_id=document_set_id,
            claims=claims,
            requirements=requirements,
            provider=self,
            prompt_version=str(input_schema["prompt_version"]),
        )
        return {
            "findings": findings,
            "coverage_summary": (
                f"{role} reviewed {len(claims)} claims against {len(requirements)} "
                f"requirements and generated {len(findings)} finding(s)."
            ),
        }


@dataclass(frozen=True)
class KnowledgeRetrievalProfile:
    required_packs: tuple[str, ...]
    optional_packs: tuple[str, ...] = ()
    signal_packs: dict[str, tuple[str, ...]] | None = None
    keywords: tuple[str, ...] = ()
    broad_scope: bool = False

    def packs_for_signals(self, signals: Sequence[str]) -> list[str]:
        packs = list(self.required_packs)
        packs.extend(self.optional_packs)
        signal_set = set(signals)
        for signal, signal_packs in (self.signal_packs or {}).items():
            if signal in signal_set:
                packs.extend(signal_packs)
        return _dedupe_strings(packs)


@dataclass(frozen=True)
class ReviewerAgent:
    agent_id: str
    role: str
    prompt_version: str
    applicable_risk_categories: list[str]
    provider: BaseModelProvider
    prompt_template: PromptTemplate | None = None

    def run(
        self,
        claims: Sequence[Claim],
        requirements: Sequence[Requirement],
        *,
        document_set_id: str,
        case_signals: Sequence[str],
        knowledge_pack_ids: Sequence[str],
        missing_knowledge_pack_ids: Sequence[str],
        requirement_package_hash: str,
        calibration_examples: Sequence[CalibrationPromptExample],
        calibration_prompt_block: str,
        calibration_pack_hash: str | None,
    ) -> ReviewerAgentOutput:
        base_prompt = (
            self.prompt_template.content
            if self.prompt_template is not None
            else (
                f"{self.role} primary review. Use only supplied claims and requirements. "
                "Return structured findings with evidence or an explicit coverage summary."
            )
        )
        prompt = (
            f"{base_prompt}\n\n{calibration_prompt_block}"
            if calibration_prompt_block
            else base_prompt
        )
        raw_output = self.provider.run_structured(
            prompt=prompt,
            input_schema={
                "document_set_id": document_set_id,
                "agent_id": self.agent_id,
                "agent_role": self.role,
                "prompt_version": self.prompt_version,
                "prompt_template": self.prompt_template.file_name
                if self.prompt_template is not None
                else None,
                "applicable_risk_categories": self.applicable_risk_categories,
                "case_signals": list(case_signals),
                "knowledge_pack_ids": list(knowledge_pack_ids),
                "missing_knowledge_pack_ids": list(missing_knowledge_pack_ids),
                "requirement_package_hash": requirement_package_hash,
                "calibration_example_ids": [
                    example.calibration_example_id for example in calibration_examples
                ],
                "calibration_pack_hash": calibration_pack_hash,
                "calibration_prompt_block": calibration_prompt_block,
                "calibration_examples": [
                    example.model_dump(mode="json") for example in calibration_examples
                ],
                "claims": [claim.model_dump(mode="json") for claim in claims],
                "requirements": [
                    requirement.model_dump(mode="json") for requirement in requirements
                ],
            },
            output_schema=ReviewerAgentOutput,
        )
        return ReviewerAgentOutput.model_validate(raw_output)


class PrimaryReviewOrchestrator:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
        agents: Sequence[ReviewerAgent] | None = None,
        encrypt_raw_outputs: bool = False,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log
        self.agents = list(agents) if agents is not None else default_reviewer_agents()
        self.encrypt_raw_outputs = encrypt_raw_outputs

    def run_primary_review(self, document_set_id: str) -> PrimaryReviewResponse:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise PrimaryReviewDocumentSetNotFoundError(f"DocumentSet {document_set_id} not found")

        claims = self.repository.list_claims(document_set_id)
        requirement_set = self.repository.get_requirement_set(document_set.requirement_set_id)
        requirements = requirement_set.requirements if requirement_set else []
        case_signals = _case_signals(document_set=document_set, claims=claims)

        agent_results = []
        with ThreadPoolExecutor(max_workers=max(1, len(self.agents))) as executor:
            futures = [
                executor.submit(
                    self._run_agent,
                    agent,
                    document_set,
                    claims,
                    requirements,
                    case_signals,
                )
                for agent in self.agents
            ]
            for future in as_completed(futures):
                agent_results.append(future.result())

        findings: list[RiskFinding] = []
        model_runs: list[ModelRun] = []
        failed_model_runs: list[ModelRun] = []
        coverage_summaries: list[CoverageSummary] = []

        for result in sorted(agent_results, key=lambda item: item.agent.agent_id):
            model_runs.append(result.model_run)
            if result.model_run.status == ModelRunStatus.FAILED:
                failed_model_runs.append(result.model_run)
            if result.output is not None:
                findings.extend(result.output.findings)
                coverage_summaries.append(
                    CoverageSummary(
                        agent_id=result.agent.agent_id,
                        role=result.agent.role,
                        coverage_summary=result.output.coverage_summary,
                        finding_count=len(result.output.findings),
                    )
                )

        verifier = EvidenceVerifierService(repository=self.repository, audit_log=self.audit_log)
        verified_findings = verifier.verify_findings(document_set_id, findings) if findings else []
        self.repository.replace_coverage_summaries(
            document_set_id=document_set_id,
            coverage_summaries=coverage_summaries,
        )
        self.audit_log.append(
            event_type="primary_review_run_completed",
            actor_id=document_set.uploaded_by,
            entity_type="DocumentSet",
            entity_id=document_set_id,
            payload={
                "agent_count": len(self.agents),
                "finding_count": len(verified_findings),
                "failed_model_run_count": len(failed_model_runs),
            },
        )
        return PrimaryReviewResponse(
            document_set_id=document_set_id,
            findings=verified_findings,
            model_runs=model_runs,
            failed_model_runs=failed_model_runs,
            coverage_summaries=coverage_summaries,
        )

    def _run_agent(
        self,
        agent: ReviewerAgent,
        document_set: DocumentSet,
        claims: Sequence[Claim],
        requirements: Sequence[Requirement],
        case_signals: Sequence[str],
    ) -> _AgentRunResult:
        document_set_id = document_set.document_set_id
        retrieval_profile = AGENT_RETRIEVAL_PROFILES.get(
            agent.role,
            DEFAULT_RETRIEVAL_PROFILE,
        )
        expected_knowledge_pack_ids = retrieval_profile.packs_for_signals(case_signals)
        agent_requirements = _requirements_for_agent(
            agent=agent,
            document_set=document_set,
            requirements=requirements,
            case_signals=case_signals,
            expected_knowledge_pack_ids=expected_knowledge_pack_ids,
        )
        requirement_ids = [
            requirement.requirement_id for requirement in agent_requirements
        ]
        knowledge_pack_ids = _knowledge_pack_ids(agent_requirements)
        missing_knowledge_pack_ids = [
            pack
            for pack in expected_knowledge_pack_ids
            if pack not in knowledge_pack_ids
        ]
        requirement_package_hash = _hash_json(
            {
                "agent_id": agent.agent_id,
                "role": agent.role,
                "case_signals": list(case_signals),
                "expected_knowledge_pack_ids": expected_knowledge_pack_ids,
                "knowledge_pack_ids": knowledge_pack_ids,
                "missing_knowledge_pack_ids": missing_knowledge_pack_ids,
                "requirement_ids": requirement_ids,
                "requirements": [
                    requirement.model_dump(mode="json")
                    for requirement in agent_requirements
                ],
            }
        )
        calibration_pack = ReviewCalibrationService(
            repository=self.repository,
            audit_log=self.audit_log,
        ).build_pack(
            document_set=document_set,
            agent_role=agent.role,
            requirements=agent_requirements,
            case_signals=case_signals,
        )
        calibration_pack_hash = (
            calibration_pack.pack_hash if calibration_pack.example_ids else None
        )
        input_hash = _hash_json(
            {
                "document_set_id": document_set_id,
                "agent_id": agent.agent_id,
                "role": agent.role,
                "claims": [claim.model_dump(mode="json") for claim in claims],
                "requirements": [
                    requirement.model_dump(mode="json") for requirement in agent_requirements
                ],
                "requirement_package_hash": requirement_package_hash,
                "knowledge_pack_ids": knowledge_pack_ids,
                "missing_knowledge_pack_ids": missing_knowledge_pack_ids,
                "case_signals": list(case_signals),
                "calibration_example_ids": calibration_pack.example_ids,
                "calibration_pack_hash": calibration_pack_hash,
            }
        )
        self.audit_log.append(
            event_type="model_run_started",
            actor_id=f"model_{agent.provider.model_name}",
            actor_type="model",
            entity_type="ReviewerAgent",
            entity_id=agent.agent_id,
            tenant_id=self._tenant_id_for_document_set(document_set_id),
            input_hash=input_hash,
            payload={
                "document_set_id": document_set_id,
                "agent_id": agent.agent_id,
                "role": agent.role,
                "provider": agent.provider.provider_name,
                "model_name": agent.provider.model_name,
                "model_version": agent.provider.model_version,
                "configured_model_id": _configured_model_id(agent.provider),
                "prompt_version": agent.prompt_version,
                "requirement_ids": requirement_ids,
                "requirement_package_hash": requirement_package_hash,
                "knowledge_pack_ids": knowledge_pack_ids,
                "missing_knowledge_pack_ids": missing_knowledge_pack_ids,
                "case_signals": list(case_signals),
                "calibration_example_ids": calibration_pack.example_ids,
                "calibration_pack_hash": calibration_pack_hash,
                "input_hash": input_hash,
            },
        )
        started_at = datetime.now(UTC)
        started_perf = time.perf_counter()
        output: ReviewerAgentOutput | None = None
        raw_output_text = ""
        status = ModelRunStatus.SUCCEEDED
        agent.provider.last_run_metadata = None
        try:
            output = agent.run(
                claims,
                agent_requirements,
                document_set_id=document_set_id,
                case_signals=case_signals,
                knowledge_pack_ids=knowledge_pack_ids,
                missing_knowledge_pack_ids=missing_knowledge_pack_ids,
                requirement_package_hash=requirement_package_hash,
                calibration_examples=calibration_pack.examples,
                calibration_prompt_block=calibration_pack.prompt_block,
                calibration_pack_hash=calibration_pack_hash,
            )
            _validate_agent_requirement_references(
                output=output,
                allowed_requirement_ids=set(requirement_ids),
            )
            raw_output_text = output.model_dump_json()
        except Exception as exc:
            raw_output_text = json.dumps({"error": str(exc)}, sort_keys=True)
            status = ModelRunStatus.FAILED

        completed_at = datetime.now(UTC)
        latency_ms = int((time.perf_counter() - started_perf) * 1000)
        output_hash = sha256(raw_output_text.encode()).hexdigest()
        model_run = ModelRun(
            model_run_id=f"run_{sha256((agent.agent_id + output_hash).encode()).hexdigest()[:20]}",
            agent_id=agent.agent_id,
            agent_role=agent.role,
            provider=agent.provider.provider_name,
            model_name=agent.provider.model_name,
            model_version=agent.provider.model_version,
            configured_model_id=_configured_model_id(agent.provider),
            prompt_version=agent.prompt_version,
            requirement_ids=requirement_ids,
            requirement_package_hash=requirement_package_hash,
            knowledge_pack_ids=knowledge_pack_ids,
            missing_knowledge_pack_ids=missing_knowledge_pack_ids,
            case_signals=list(case_signals),
            calibration_example_ids=calibration_pack.example_ids,
            calibration_pack_hash=calibration_pack_hash,
            input_hash=input_hash,
            output_hash=output_hash,
            started_at=started_at,
            completed_at=completed_at,
            latency_ms=latency_ms,
            token_usage=_token_usage_for_model_run(agent.provider, input_hash, raw_output_text),
            status=status,
        )
        self.repository.add_model_run(document_set_id=document_set_id, model_run=model_run)
        self.repository.store_raw_model_output(
            RawModelOutputRecord(
                model_run_id=model_run.model_run_id,
                output_hash=output_hash,
                raw_output=raw_output_text,
                encrypted=self.encrypt_raw_outputs,
            )
        )
        completed_event_type = (
            "model_run_completed" if status == ModelRunStatus.SUCCEEDED else "model_run_failed"
        )
        self.audit_log.append(
            event_type=completed_event_type,
            actor_id=f"model_{agent.provider.model_name}",
            actor_type="model",
            entity_type="ModelRun",
            entity_id=model_run.model_run_id,
            tenant_id=self._tenant_id_for_document_set(document_set_id),
            input_hash=input_hash,
            output_hash=output_hash,
            payload={
                "document_set_id": document_set_id,
                "agent_id": agent.agent_id,
                "role": agent.role,
                "status": status,
                "provider": model_run.provider,
                "model_name": model_run.model_name,
                "model_version": model_run.model_version,
                "configured_model_id": model_run.configured_model_id,
                "prompt_version": agent.prompt_version,
                "requirement_ids": model_run.requirement_ids,
                "requirement_package_hash": model_run.requirement_package_hash,
                "knowledge_pack_ids": model_run.knowledge_pack_ids,
                "missing_knowledge_pack_ids": model_run.missing_knowledge_pack_ids,
                "case_signals": model_run.case_signals,
                "calibration_example_ids": model_run.calibration_example_ids,
                "calibration_pack_hash": model_run.calibration_pack_hash,
                "input_hash": input_hash,
                "output_hash": output_hash,
            },
        )
        if output is not None:
            for finding in output.findings:
                self.audit_log.append(
                    event_type="finding_created",
                    actor_id=f"model_{agent.provider.model_name}",
                    actor_type="model",
                    entity_type="RiskFinding",
                    entity_id=finding.finding_id,
                    payload={
                        "document_set_id": document_set_id,
                        "model_run_id": model_run.model_run_id,
                        "agent_id": agent.agent_id,
                        "agent_role": agent.role,
                        "prompt_version": agent.prompt_version,
                        "risk_category": finding.risk_category,
                        "severity": finding.severity,
                        "requirement_references": finding.requirement_references,
                        "calibration_example_ids": model_run.calibration_example_ids,
                    },
                )
        event_type = (
            "model_run_recorded" if status == ModelRunStatus.SUCCEEDED else "failed_model_run"
        )
        self.audit_log.append(
            event_type=event_type,
            actor_id="user_system",
            entity_type="ModelRun",
            entity_id=model_run.model_run_id,
            tenant_id=self._tenant_id_for_document_set(document_set_id),
            payload={
                "document_set_id": document_set_id,
                "agent_id": agent.agent_id,
                "role": agent.role,
                "status": status,
                "provider": model_run.provider,
                "model_name": model_run.model_name,
                "model_version": model_run.model_version,
                "configured_model_id": model_run.configured_model_id,
                "prompt_version": agent.prompt_version,
                "requirement_ids": model_run.requirement_ids,
                "requirement_package_hash": model_run.requirement_package_hash,
                "knowledge_pack_ids": model_run.knowledge_pack_ids,
                "missing_knowledge_pack_ids": model_run.missing_knowledge_pack_ids,
                "case_signals": model_run.case_signals,
                "calibration_example_ids": model_run.calibration_example_ids,
                "calibration_pack_hash": model_run.calibration_pack_hash,
                "input_hash": input_hash,
                "output_hash": output_hash,
            },
        )
        return _AgentRunResult(agent=agent, output=output, model_run=model_run)

    def _tenant_id_for_document_set(self, document_set_id: str) -> str | None:
        document_set = self.repository.get_document_set(document_set_id)
        return document_set.tenant_id if document_set is not None else None


@dataclass(frozen=True)
class _AgentRunResult:
    agent: ReviewerAgent
    output: ReviewerAgentOutput | None
    model_run: ModelRun


def default_reviewer_agents() -> list[ReviewerAgent]:
    loader = PromptTemplateLoader()
    agents = [
        _agent_from_template(
            loader=loader,
            agent_id="agent_gmp_data_integrity",
            role="GMPDataIntegrityReviewer",
            template_name="gmp_data_integrity_reviewer_v1.md",
            applicable_risk_categories=["data_integrity", "audit_trail"],
        ),
        _agent_from_template(
            loader=loader,
            agent_id="agent_deviation",
            role="DeviationReviewer",
            template_name="deviation_reviewer_v1.md",
            applicable_risk_categories=["deviation_management"],
        ),
        _agent_from_template(
            loader=loader,
            agent_id="agent_capa",
            role="CAPAReviewer",
            template_name="capa_reviewer_v1.md",
            applicable_risk_categories=["capa"],
        ),
        _agent_from_template(
            loader=loader,
            agent_id="agent_batch_impact",
            role="BatchImpactReviewer",
            template_name="batch_impact_reviewer_v1.md",
            applicable_risk_categories=["batch_impact_assessment"],
        ),
        _agent_from_template(
            loader=loader,
            agent_id="agent_validation_sterility",
            role="ValidationAndSterilityReviewer",
            template_name="validation_and_sterility_reviewer_v1.md",
            applicable_risk_categories=[
                "validation",
                "cleaning_validation",
                "sterility_assurance",
            ],
        ),
        _agent_from_template(
            loader=loader,
            agent_id="agent_regulatory_consistency",
            role="RegulatoryConsistencyReviewer",
            template_name="regulatory_consistency_reviewer_v1.md",
            applicable_risk_categories=["qa_approval", "regulatory_consistency"],
        ),
        _agent_from_template(
            loader=loader,
            agent_id="agent_contradiction_hunter",
            role="ContradictionHunter",
            template_name="contradiction_hunter_v1.md",
            applicable_risk_categories=["contradiction"],
        ),
    ]
    agents.extend(_critic_agents(loader))
    return agents


CRITIC_RISK_CATEGORIES = [
    "deviation_management",
    "capa",
    "data_integrity",
    "batch_impact_assessment",
    "validation",
    "qa_approval",
    "regulatory_consistency",
    "contradiction",
]

CRITIC_ROLES_BY_PROVIDER = {
    "anthropic": "RedTeamCriticAnthropic",
    "openai": "RedTeamCriticOpenAI",
    "mistral": "RedTeamCriticMistral",
}


def _critic_agents(loader: PromptTemplateLoader) -> list[ReviewerAgent]:
    settings = get_settings()
    providers = [
        entry.strip().lower()
        for entry in settings.critic_providers.split(",")
        if entry.strip()
    ]
    agents = []
    for provider_name in providers:
        role = CRITIC_ROLES_BY_PROVIDER.get(provider_name)
        if role is None:
            continue
        agents.append(
            _agent_from_template(
                loader=loader,
                agent_id=f"agent_red_team_critic_{provider_name}",
                role=role,
                template_name="red_team_critic_v1.md",
                applicable_risk_categories=list(CRITIC_RISK_CATEGORIES),
            )
        )
    return agents


def _agent_from_template(
    *,
    loader: PromptTemplateLoader,
    agent_id: str,
    role: str,
    template_name: str,
    applicable_risk_categories: list[str],
) -> ReviewerAgent:
    template = loader.load(template_name)
    return ReviewerAgent(
        agent_id=agent_id,
        role=role,
        prompt_version=template.prompt_version,
        applicable_risk_categories=applicable_risk_categories,
        provider=_provider_for_role(role),
        prompt_template=template,
    )


def _provider_for_role(role: str) -> BaseModelProvider:
    settings = get_settings()
    if not settings.external_model_calls_enabled:
        return MockModelProvider()

    runtime_options = _runtime_options_from_settings(settings)
    if role == "RedTeamCriticAnthropic":
        return AnthropicProvider(
            configured_model_id=settings.anthropic_model_id,
            runtime_options=runtime_options,
        )
    if role == "RedTeamCriticOpenAI":
        return OpenAIProvider(
            configured_model_id=settings.openai_model_id,
            runtime_options=runtime_options,
        )
    if role == "RedTeamCriticMistral":
        return MistralProvider(
            configured_model_id=settings.mistral_model_id,
            runtime_options=runtime_options,
        )
    if settings.reviewer_provider_override == "mistral":
        return MistralProvider(
            configured_model_id=settings.mistral_model_id,
            runtime_options=runtime_options,
        )
    if role == "BatchImpactReviewer":
        return OpenAIProvider(
            configured_model_id=settings.openai_model_id,
            runtime_options=runtime_options,
        )
    if role in {
        "GMPDataIntegrityReviewer",
        "DeviationReviewer",
        "CAPAReviewer",
        "ValidationAndSterilityReviewer",
        "RegulatoryConsistencyReviewer",
    }:
        return AnthropicProvider(
            configured_model_id=settings.anthropic_model_id,
            runtime_options=runtime_options,
        )
    if role == "ContradictionHunter":
        return OpenAIProvider(
            configured_model_id=settings.openai_model_id,
            runtime_options=runtime_options,
        )
    return MockModelProvider()


ROLE_REQUIREMENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "BatchImpactReviewer": (
        "batch",
        "charge",
        "chargen",
        "disposition",
        "release",
        "freigabe",
    ),
    "GMPDataIntegrityReviewer": (
        "data",
        "daten",
        "audit trail",
        "alcoa",
        "record",
        "integrity",
    ),
    "DeviationReviewer": (
        "deviation",
        "abweichung",
        "investigation",
        "root cause",
        "ursache",
    ),
    "CAPAReviewer": (
        "capa",
        "corrective",
        "preventive",
        "effectiveness",
        "wirksamkeit",
    ),
    "RegulatoryConsistencyReviewer": (
        "sop",
        "regulatory",
        "qa",
        "approval",
        "change",
        "validation",
        "validierung",
    ),
    "ValidationAndSterilityReviewer": (
        "validation",
        "validierung",
        "cleaning",
        "reinigung",
        "sterility",
        "steril",
        "aseptic",
        "aseptisch",
        "cci",
        "e&l",
        "extractables",
        "leachables",
    ),
}


DEFAULT_RETRIEVAL_PROFILE = KnowledgeRetrievalProfile(
    required_packs=("universal_gmp_qrm_base",),
    keywords=("gmp", "qrm", "risk", "requirement", "review"),
)


AGENT_RETRIEVAL_PROFILES: dict[str, KnowledgeRetrievalProfile] = {
    "GMPDataIntegrityReviewer": KnowledgeRetrievalProfile(
        required_packs=(
            "universal_gmp_qrm_base",
            "data_integrity",
            "audit_trail_review",
            "electronic_records",
        ),
        signal_packs={
            "user_access": ("user_access",),
            "manual_override": ("manual_override",),
            "system_validation": ("system_validation",),
        },
        keywords=(
            "data integrity",
            "datenintegritaet",
            "audit trail",
            "alcoa",
            "electronic record",
            "admin",
            "override",
            "timestamp",
        ),
    ),
    "DeviationReviewer": KnowledgeRetrievalProfile(
        required_packs=(
            "universal_gmp_qrm_base",
            "deviation_management",
            "impact_assessment",
            "root_cause_analysis",
        ),
        signal_packs={
            "batch_impact": ("batch_impact",),
            "capa": ("capa_management",),
        },
        keywords=(
            "deviation",
            "abweichung",
            "root cause",
            "ursache",
            "impact assessment",
            "recurrence",
        ),
    ),
    "CAPAReviewer": KnowledgeRetrievalProfile(
        required_packs=(
            "universal_gmp_qrm_base",
            "capa_management",
            "effectiveness_check",
        ),
        signal_packs={
            "training": ("training_effectiveness",),
            "deviation": ("deviation_management",),
        },
        keywords=(
            "capa",
            "corrective action",
            "preventive action",
            "effectiveness",
            "wirksamkeit",
            "closure",
        ),
    ),
    "BatchImpactReviewer": KnowledgeRetrievalProfile(
        required_packs=(
            "universal_gmp_qrm_base",
            "batch_impact",
            "disposition",
            "material_traceability",
        ),
        signal_packs={
            "supplier_change": ("supplier_quality",),
            "rework": ("rework_reprocessing",),
        },
        keywords=(
            "batch",
            "charge",
            "lot",
            "disposition",
            "release",
            "genealogy",
            "traceability",
        ),
    ),
    "ValidationAndSterilityReviewer": KnowledgeRetrievalProfile(
        required_packs=(
            "universal_gmp_qrm_base",
            "validation",
            "cleaning_validation",
            "sterility_assurance",
        ),
        signal_packs={
            "aseptic_processing": ("aseptic_processing",),
            "primary_packaging_component": ("primary_packaging",),
            "material_change": ("product_contact_material_change",),
            "method_change": ("method_validation",),
            "cci_el": ("cci_el",),
            "em_alert": ("environmental_monitoring",),
        },
        keywords=(
            "validation",
            "validierung",
            "cleaning",
            "reinigung",
            "sterility",
            "sterilitaet",
            "aseptic",
            "aseptisch",
            "worst case",
            "cci",
            "e&l",
        ),
    ),
    "RegulatoryConsistencyReviewer": KnowledgeRetrievalProfile(
        required_packs=(
            "universal_gmp_qrm_base",
            "regulatory_consistency",
            "change_control",
            "approval_matrix",
        ),
        signal_packs={
            "supplier_change": ("supplier_quality",),
            "validation_scope": ("validation",),
            "cleaning_validation": ("cleaning_validation",),
            "aseptic_processing": ("sterility_assurance",),
            "approval_pending": ("document_control",),
        },
        keywords=(
            "sop",
            "regulatory",
            "qa",
            "approval",
            "change",
            "scope",
            "effective",
            "requirement",
        ),
    ),
    "ContradictionHunter": KnowledgeRetrievalProfile(
        required_packs=(
            "universal_gmp_qrm_base",
            "contradiction_patterns",
            "red_flag_patterns",
        ),
        signal_packs={
            "unsupported_no_impact": ("no_impact_red_flags",),
            "approval_pending": ("pending_approval_patterns",),
            "validation_scope": ("old_evidence_patterns",),
            "missing_attachment": ("missing_attachment_patterns",),
        },
        keywords=(
            "contradiction",
            "widerspruch",
            "missing",
            "pending",
            "no impact",
            "not applicable",
            "appendix",
        ),
        broad_scope=True,
    ),
    "RedTeamCriticAnthropic": KnowledgeRetrievalProfile(
        required_packs=("universal_gmp_qrm_base",),
        broad_scope=True,
    ),
    "RedTeamCriticOpenAI": KnowledgeRetrievalProfile(
        required_packs=("universal_gmp_qrm_base",),
        broad_scope=True,
    ),
    "RedTeamCriticMistral": KnowledgeRetrievalProfile(
        required_packs=("universal_gmp_qrm_base",),
        broad_scope=True,
    ),
}


SIGNAL_PATTERNS: dict[str, tuple[str, ...]] = {
    "approval_pending": ("pending", "planned", "to be attached", "offen", "geplant"),
    "aseptic_processing": ("aseptic", "aseptisch", "sterile filling", "sterile abfuellung"),
    "batch_impact": ("batch", "batches", "charge", "chargen", "lot", "disposition"),
    "capa": ("capa", "corrective action", "preventive action", "korrekturmassnahme"),
    "cci_el": ("cci", "container closure", "extractables", "leachables", "e&l"),
    "cleaning_validation": ("cleaning validation", "reinigungsvalidierung", "cleaning matrix"),
    "deviation": ("deviation", "abweichung", "root cause", "investigation"),
    "em_alert": ("em alert", "environmental monitoring", "umgebungsmonitoring"),
    "manual_override": ("manual override", "override", "manual change", "manuelle aenderung"),
    "material_change": ("material change", "materialaenderung", "coating", "beschichtung"),
    "method_change": ("method changed", "test method", "methode", "pruefmethode"),
    "missing_attachment": ("missing attachment", "fehlender anhang", "not attached"),
    "primary_packaging_component": (
        "primary packaging",
        "primaerpackmittel",
        "stopper",
        "closure",
        "product contact",
        "produktkontakt",
    ),
    "rework": ("rework", "reprocessing", "nacharbeit", "wiederaufarbeitung"),
    "silicone_oil_change": ("silicone oil", "silikonoel", "silicone"),
    "specification_change": ("specification changed", "spezifikation", "specification"),
    "supplier_change": ("supplier change", "supplier", "lieferant", "vendor"),
    "system_validation": ("computerized system", "csv", "csa", "system validation"),
    "training": ("training", "schulung", "trained"),
    "unsupported_no_impact": ("no impact", "kein einfluss", "keine auswirkung"),
    "user_access": ("user access", "user role", "benutzerrolle", "shared login"),
    "validation_scope": ("validation", "validierung", "validation report", "addendum"),
}


def _requirements_for_agent(
    *,
    agent: ReviewerAgent,
    document_set: DocumentSet,
    requirements: Sequence[Requirement],
    case_signals: Sequence[str],
    expected_knowledge_pack_ids: Sequence[str],
) -> list[Requirement]:
    scoped = [
        requirement
        for requirement in requirements
        if _requirement_matches_document_set(requirement, document_set)
    ]
    if not scoped:
        scoped = list(requirements)

    if AGENT_RETRIEVAL_PROFILES.get(agent.role, DEFAULT_RETRIEVAL_PROFILE).broad_scope:
        return scoped

    profile = AGENT_RETRIEVAL_PROFILES.get(agent.role, DEFAULT_RETRIEVAL_PROFILE)
    keywords = (*ROLE_REQUIREMENT_KEYWORDS.get(agent.role, ()), *profile.keywords)
    role_matches = [
        requirement
        for requirement in scoped
        if _requirement_matches_agent(
            requirement,
            agent,
            keywords,
            case_signals=case_signals,
            expected_knowledge_pack_ids=expected_knowledge_pack_ids,
        )
    ]
    return role_matches or scoped


def _requirement_matches_document_set(
    requirement: Requirement,
    document_set: DocumentSet,
) -> bool:
    document_type_matches = (
        not requirement.applies_to_document_types
        or document_set.declared_document_type in requirement.applies_to_document_types
    )
    process_area_matches = (
        not requirement.applies_to_process_areas
        or document_set.declared_process_area in requirement.applies_to_process_areas
    )
    return document_type_matches and process_area_matches


def _requirement_matches_agent(
    requirement: Requirement,
    agent: ReviewerAgent,
    keywords: Sequence[str],
    *,
    case_signals: Sequence[str],
    expected_knowledge_pack_ids: Sequence[str],
) -> bool:
    searchable = " ".join(
        [
            requirement.requirement_id,
            requirement.title or "",
            requirement.domain or "",
            requirement.source_name,
            requirement.section,
            requirement.requirement_text,
            " ".join(requirement.knowledge_packs),
            " ".join(requirement.applies_to_agents),
            " ".join(requirement.applies_when_signals_present),
            " ".join(requirement.red_flags),
            " ".join(requirement.source_refs),
            " ".join(requirement.required_reviewer_roles),
            " ".join(requirement.required_evidence),
            " ".join(requirement.applies_to_document_types),
            " ".join(requirement.applies_to_process_areas),
        ]
    ).lower()
    explicit_agent_match = agent.role in requirement.applies_to_agents
    requirement_signal_match = bool(
        set(_normalise_keys(requirement.applies_when_signals_present))
        & set(_normalise_keys(case_signals))
    )
    pack_match = bool(
        set(_normalise_keys(_requirement_pack_candidates(requirement)))
        & set(_normalise_keys(expected_knowledge_pack_ids))
    )
    categories_match = any(
        category.lower() in searchable for category in agent.applicable_risk_categories
    )
    keywords_match = any(keyword.lower() in searchable for keyword in keywords)
    return (
        explicit_agent_match
        or requirement_signal_match
        or pack_match
        or categories_match
        or keywords_match
    )


def _case_signals(*, document_set: DocumentSet, claims: Sequence[Claim]) -> list[str]:
    fragments = [
        document_set.declared_document_type,
        document_set.declared_process_area,
    ]
    for claim in claims:
        fragments.extend(
            [
                str(claim.claim_type),
                claim.normalized_subject,
                claim.normalized_predicate,
                claim.normalized_object,
                claim.raw_text_quote,
            ]
        )
    searchable = " ".join(fragments).lower()
    signals = [
        signal
        for signal, patterns in SIGNAL_PATTERNS.items()
        if any(pattern.lower() in searchable for pattern in patterns)
    ]
    return _dedupe_strings(signals)


def _knowledge_pack_ids(requirements: Sequence[Requirement]) -> list[str]:
    packs: list[str] = []
    for requirement in requirements:
        packs.extend(_requirement_pack_candidates(requirement))
    return _dedupe_strings(packs)


def _requirement_pack_candidates(requirement: Requirement) -> list[str]:
    packs: list[str] = ["universal_gmp_qrm_base"]
    packs.extend(requirement.knowledge_packs)
    if requirement.domain:
        packs.append(requirement.domain)
    searchable = " ".join(
        [
            requirement.requirement_id,
            requirement.title or "",
            requirement.domain or "",
            requirement.source_name,
            requirement.section,
            requirement.requirement_text,
            " ".join(requirement.required_evidence),
            " ".join(requirement.applies_to_document_types),
            " ".join(requirement.applies_to_process_areas),
            " ".join(requirement.red_flags),
            " ".join(requirement.source_refs),
        ]
    ).lower()
    inferred_pack_keywords: dict[str, tuple[str, ...]] = {
        "approval_matrix": ("approval", "freigabe", "qa approval", "matrix"),
        "aseptic_processing": ("aseptic", "aseptisch"),
        "audit_trail_review": ("audit trail",),
        "batch_impact": ("batch", "charge", "lot", "disposition"),
        "capa_management": ("capa", "corrective", "preventive"),
        "change_control": ("change", "aenderung", "change control"),
        "cleaning_validation": ("cleaning", "reinigung"),
        "contradiction_patterns": ("contradiction", "widerspruch"),
        "data_integrity": ("data integrity", "datenintegritaet", "alcoa"),
        "deviation_management": ("deviation", "abweichung"),
        "disposition": ("disposition", "release", "freigabe"),
        "document_control": ("document", "version", "effective", "attachment"),
        "effectiveness_check": ("effectiveness", "wirksamkeit"),
        "electronic_records": ("electronic record", "signature", "esignature"),
        "impact_assessment": ("impact", "auswirkung"),
        "material_traceability": ("traceability", "genealogy", "material", "supplier"),
        "method_validation": ("method", "methode"),
        "red_flag_patterns": ("red flag", "pending", "no impact"),
        "regulatory_consistency": ("sop", "regulatory", "requirement"),
        "root_cause_analysis": ("root cause", "ursache"),
        "sterility_assurance": ("sterility", "steril"),
        "supplier_quality": ("supplier", "lieferant", "vendor"),
        "validation": ("validation", "validierung"),
    }
    for pack, keywords in inferred_pack_keywords.items():
        if any(keyword in searchable for keyword in keywords):
            packs.append(pack)
    return _dedupe_strings(packs)


def _normalise_keys(values: Sequence[str]) -> list[str]:
    return [value.strip().lower() for value in values if value and value.strip()]


def _dedupe_strings(values: Sequence[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = value.strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(cleaned)
    return deduped


def _validate_agent_requirement_references(
    *,
    output: ReviewerAgentOutput,
    allowed_requirement_ids: set[str],
) -> None:
    for finding in output.findings:
        if not finding.requirement_references:
            raise ValueError(
                f"Finding {finding.finding_id} has no requirement reference"
            )
        unknown_ids = [
            requirement_id
            for requirement_id in finding.requirement_references
            if requirement_id not in allowed_requirement_ids
        ]
        if unknown_ids:
            raise ValueError(
                f"Finding {finding.finding_id} references requirements not supplied "
                f"to the agent: {', '.join(unknown_ids)}"
            )


def _runtime_options_from_settings(settings: Settings) -> ProviderRuntimeOptions:
    return ProviderRuntimeOptions(
        timeout_seconds=settings.model_provider_timeout_seconds,
        max_retries=settings.model_provider_max_retries,
        circuit_breaker_failure_threshold=settings.model_provider_circuit_breaker_threshold,
    )


def _mock_findings_for_role(
    *,
    role: str,
    document_set_id: str,
    claims: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    provider: BaseModelProvider,
    prompt_version: str,
) -> list[dict[str, Any]]:
    if role == "DeviationReviewer":
        claim = _first_claim(claims, "deviation_description") or _first_claim(
            claims,
            "impact_assessment",
        )
        if claim:
            return [
                _finding_payload(
                    document_set_id=document_set_id,
                    role=role,
                    risk_category="deviation_management",
                    severity="high",
                    statement=(
                        "Deviation impact needs human review against documented requirements."
                    ),
                    claim=claim,
                    requirements=requirements,
                    provider=provider,
                    prompt_version=prompt_version,
                    missing_information=_missing_if_absent(
                        claims,
                        "root_cause",
                        "root cause claim",
                    ),
                )
            ]
    if role == "BatchImpactReviewer":
        claim = _first_claim(claims, "batch_identifier")
        if claim:
            return [
                _finding_payload(
                    document_set_id=document_set_id,
                    role=role,
                    risk_category="batch_impact_assessment",
                    severity="medium",
                    statement="Batch-linked deviation requires documented batch impact trace.",
                    claim=claim,
                    requirements=requirements,
                    provider=provider,
                    prompt_version=prompt_version,
                    missing_information=_missing_if_absent(
                        claims,
                        "impact_assessment",
                        "batch-specific impact assessment",
                    ),
                )
            ]
    if role == "CAPAReviewer":
        claim = _first_claim(claims, "capa_action")
        if claim:
            return [
                _finding_payload(
                    document_set_id=document_set_id,
                    role=role,
                    risk_category="capa",
                    severity="medium",
                    statement=(
                        "CAPA reference requires effectiveness evidence if linked to quality risk."
                    ),
                    claim=claim,
                    requirements=requirements,
                    provider=provider,
                    prompt_version=prompt_version,
                    missing_information=_missing_if_absent(
                        claims,
                        "effectiveness_check",
                        "CAPA effectiveness check evidence",
                    ),
                )
            ]
    if role == "RegulatoryConsistencyReviewer":
        claim = _first_claim(claims, "qa_approval")
        if claim and "pending" in str(claim["normalized_object"]).lower():
            return [
                _finding_payload(
                    document_set_id=document_set_id,
                    role=role,
                    risk_category="qa_approval",
                    severity="medium",
                    statement="QA approval appears pending and should not be treated as closed.",
                    claim=claim,
                    requirements=requirements,
                    provider=provider,
                    prompt_version=prompt_version,
                    missing_information=["documented QA approval decision"],
                )
            ]
    return []


def _finding_payload(
    *,
    document_set_id: str,
    role: str,
    risk_category: str,
    severity: str,
    statement: str,
    claim: dict[str, Any],
    requirements: list[dict[str, Any]],
    provider: BaseModelProvider,
    prompt_version: str,
    missing_information: list[str],
) -> dict[str, Any]:
    quote = str(claim["raw_text_quote"])
    finding_seed = "|".join([document_set_id, role, risk_category, quote])
    return {
        "finding_id": f"finding_{sha256(finding_seed.encode()).hexdigest()[:20]}",
        "document_set_id": document_set_id,
        "risk_category": risk_category,
        "severity": severity,
        "likelihood": 3,
        "detectability": 3,
        "risk_statement": statement,
        "evidence_items": [
            EvidenceItem(
                document_id=claim["document_id"],
                chunk_id=claim["chunk_id"],
                page=claim["page"],
                quote=quote,
                quote_hash=sha256(quote.encode()).hexdigest(),
                support_type=SupportType.SUPPORTS,
                verifier_score=float(claim["confidence"]),
            ).model_dump(mode="json")
        ],
        "requirement_references": [
            requirement["requirement_id"] for requirement in requirements[:2]
        ],
        "missing_information": missing_information,
        "model_provider": provider.provider_name,
        "model_name": provider.model_name,
        "model_version": provider.model_version,
        "prompt_version": prompt_version,
        "evidence_support": "partial" if missing_information else "strong",
        "recommended_action": "Route to qualified human reviewer; do not auto-clear.",
        "auto_close_allowed": False,
        "status": "needs_human_review",
    }


def _first_claim(claims: list[dict[str, Any]], claim_type: str) -> dict[str, Any] | None:
    return next((claim for claim in claims if claim.get("claim_type") == claim_type), None)


def _missing_if_absent(
    claims: list[dict[str, Any]],
    claim_type: str,
    missing_label: str,
) -> list[str]:
    return [] if _first_claim(claims, claim_type) else [missing_label]


def _hash_json(payload: dict[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def _estimate_token_usage(input_hash: str, raw_output_text: str) -> TokenUsage:
    output_tokens = max(1, len(raw_output_text.split()))
    input_tokens = max(1, len(input_hash) // 4)
    return TokenUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
    )


def _token_usage_for_model_run(
    provider: BaseModelProvider,
    input_hash: str,
    raw_output_text: str,
) -> TokenUsage:
    metadata = provider.last_run_metadata
    if metadata is not None and metadata.token_usage is not None:
        input_tokens = metadata.token_usage.input_tokens
        output_tokens = metadata.token_usage.output_tokens
        return TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )
    return _estimate_token_usage(input_hash, raw_output_text)


def _configured_model_id(provider: BaseModelProvider) -> str:
    return str(getattr(provider, "configured_model_id", "not_recorded"))
