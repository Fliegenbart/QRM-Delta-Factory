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
    GeminiProvider,
    MockProvider,
    OpenAIProvider,
    ProviderRuntimeOptions,
)
from app.audit.events import InMemoryAuditLog
from app.core.config import Settings, get_settings
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import (
    Claim,
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
    ) -> ReviewerAgentOutput:
        prompt = (
            self.prompt_template.content
            if self.prompt_template is not None
            else (
                f"{self.role} primary review. Use only supplied claims and requirements. "
                "Return structured findings with evidence or an explicit coverage summary."
            )
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

        agent_results = []
        with ThreadPoolExecutor(max_workers=max(1, len(self.agents))) as executor:
            futures = [
                executor.submit(self._run_agent, agent, document_set_id, claims, requirements)
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
        document_set_id: str,
        claims: Sequence[Claim],
        requirements: Sequence[Requirement],
    ) -> _AgentRunResult:
        input_hash = _hash_json(
            {
                "document_set_id": document_set_id,
                "agent_id": agent.agent_id,
                "role": agent.role,
                "claims": [claim.model_dump(mode="json") for claim in claims],
                "requirements": [
                    requirement.model_dump(mode="json") for requirement in requirements
                ],
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
            output = agent.run(claims, requirements, document_set_id=document_set_id)
            raw_output_text = output.model_dump_json()
        except Exception as exc:
            raw_output_text = json.dumps({"error": str(exc)}, sort_keys=True)
            status = ModelRunStatus.FAILED

        completed_at = datetime.now(UTC)
        latency_ms = int((time.perf_counter() - started_perf) * 1000)
        output_hash = sha256(raw_output_text.encode()).hexdigest()
        model_run = ModelRun(
            model_run_id=f"run_{sha256((agent.agent_id + output_hash).encode()).hexdigest()[:20]}",
            provider=agent.provider.provider_name,
            model_name=agent.provider.model_name,
            model_version=agent.provider.model_version,
            configured_model_id=_configured_model_id(agent.provider),
            prompt_version=agent.prompt_version,
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
    return [
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
    if role in {"GMPDataIntegrityReviewer", "BatchImpactReviewer"}:
        return OpenAIProvider(
            configured_model_id=settings.openai_model_id,
            runtime_options=runtime_options,
        )
    if role in {"DeviationReviewer", "RegulatoryConsistencyReviewer"}:
        return AnthropicProvider(
            configured_model_id=settings.anthropic_model_id,
            runtime_options=runtime_options,
        )
    if role in {"CAPAReviewer", "ContradictionHunter"}:
        return GeminiProvider(
            configured_model_id=settings.gemini_model_id,
            runtime_options=runtime_options,
        )
    return MockModelProvider()


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
        return TokenUsage(
            input_tokens=metadata.token_usage.input_tokens,
            output_tokens=metadata.token_usage.output_tokens,
            total_tokens=metadata.token_usage.total_tokens,
        )
    return _estimate_token_usage(input_hash, raw_output_text)


def _configured_model_id(provider: BaseModelProvider) -> str:
    return str(getattr(provider, "configured_model_id", "not_recorded"))
