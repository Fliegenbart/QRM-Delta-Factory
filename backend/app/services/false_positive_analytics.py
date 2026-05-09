from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256

from app.audit.events import AuditEvent, InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.analytics import (
    FalsePositiveAnalyticsReport,
    FalsePositiveCluster,
    FalsePositiveClusterGroup,
    FalsePositiveRecommendation,
    FalsePositiveRecommendationType,
)
from app.schemas.domain import (
    DocumentSet,
    ReviewDecision,
    ReviewDecisionValue,
    RiskFinding,
    Severity,
)

OVERRIDE_DECISIONS = {
    ReviewDecisionValue.REJECT_FALSE_POSITIVE,
    ReviewDecisionValue.DOWNGRADE,
}
NO_REQUIREMENT_REFERENCE = "NO_REQUIREMENT_REFERENCE"

_SEVERITY_RANK = {
    Severity.INFORMATIONAL: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


class HumanOverrideAnalyzer:
    """Analyzes human false-positive overrides without changing system behavior."""

    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log

    def analyze(self, *, tenant_id: str | None = None) -> FalsePositiveAnalyticsReport:
        override_contexts = self._collect_override_contexts(tenant_id=tenant_id)
        grouped_contexts: dict[_ClusterKey, list[_OverrideContext]] = defaultdict(list)
        for context in override_contexts:
            grouped_contexts[context.key].append(context)

        clusters = [
            self._build_cluster(key=key, contexts=contexts)
            for key, contexts in grouped_contexts.items()
        ]
        clusters.sort(
            key=lambda cluster: (
                -_SEVERITY_RANK[cluster.max_severity],
                -cluster.override_decision_count,
                cluster.group.risk_category,
                cluster.group.requirement_id,
            )
        )
        report = FalsePositiveAnalyticsReport(
            generated_at=datetime.now(UTC),
            total_override_decisions=len(override_contexts),
            cluster_count=len(clusters),
            clusters=clusters,
            limitations=[
                "Recommendations are advisory only and do not change Risk Fusion behavior.",
                (
                    "Prompt, requirement, verifier, or policy changes require a new version "
                    "and an evaluation run before use."
                ),
                (
                    "High and Critical findings remain protected by recall guards and are "
                    "not auto-closed by false-positive patterns."
                ),
            ],
        )
        self.audit_log.append(
            event_type="false_positive_analysis_run",
            actor_id="service_false_positive_analytics",
            actor_type="service",
            entity_type="Analytics",
            entity_id="false_positive_overrides",
            tenant_id=tenant_id,
            payload={
                "total_override_decisions": report.total_override_decisions,
                "cluster_count": report.cluster_count,
                "cluster_ids": [cluster.cluster_id for cluster in report.clusters],
            },
        )
        return report

    def _collect_override_contexts(
        self,
        *,
        tenant_id: str | None,
    ) -> list[_OverrideContext]:
        contexts: list[_OverrideContext] = []
        for decision in self.repository.list_review_decisions_all():
            if decision.decision not in OVERRIDE_DECISIONS:
                continue
            finding = self.repository.find_risk_finding(decision.finding_id)
            if finding is None:
                continue
            document_set = self.repository.get_document_set(finding.document_set_id)
            if document_set is None:
                continue
            if tenant_id is not None and document_set.tenant_id != tenant_id:
                continue

            audit_context = _finding_audit_context(
                audit_log=self.audit_log,
                finding=finding,
            )
            requirement_ids = finding.requirement_references or [NO_REQUIREMENT_REFERENCE]
            for requirement_id in requirement_ids:
                key = _ClusterKey(
                    requirement_id=str(requirement_id),
                    risk_category=finding.risk_category,
                    agent_role=audit_context.agent_role,
                    prompt_version=audit_context.prompt_version,
                    evidence_support=str(finding.evidence_support),
                    document_type=document_set.declared_document_type,
                )
                contexts.append(
                    _OverrideContext(
                        key=key,
                        decision=decision,
                        finding=finding,
                        document_set=document_set,
                    )
                )
        return contexts

    def _build_cluster(
        self,
        *,
        key: _ClusterKey,
        contexts: list[_OverrideContext],
    ) -> FalsePositiveCluster:
        finding_ids = _unique_preserving_order(
            [context.finding.finding_id for context in contexts]
        )
        reject_false_positive_count = sum(
            1
            for context in contexts
            if context.decision.decision == ReviewDecisionValue.REJECT_FALSE_POSITIVE
        )
        downgrade_count = sum(
            1 for context in contexts if context.decision.decision == ReviewDecisionValue.DOWNGRADE
        )
        max_severity = max(
            (context.finding.severity for context in contexts),
            key=lambda severity: _SEVERITY_RANK[severity],
        )
        high_critical_recall_guard = max_severity in {Severity.HIGH, Severity.CRITICAL}
        return FalsePositiveCluster(
            cluster_id=_cluster_id(key),
            group=FalsePositiveClusterGroup(
                requirement_id=key.requirement_id,
                risk_category=key.risk_category,
                agent_role=key.agent_role,
                prompt_version=key.prompt_version,
                evidence_support=key.evidence_support,
                document_type=key.document_type,
            ),
            finding_ids=finding_ids,
            override_decision_count=len(contexts),
            reject_false_positive_count=reject_false_positive_count,
            downgrade_count=downgrade_count,
            max_severity=max_severity,
            high_critical_recall_guard=high_critical_recall_guard,
            auto_rule_change_allowed=False,
            recommendations=_recommendations(
                key=key,
                count=len(contexts),
                high_critical_recall_guard=high_critical_recall_guard,
            ),
        )


@dataclass(frozen=True)
class _ClusterKey:
    requirement_id: str
    risk_category: str
    agent_role: str
    prompt_version: str
    evidence_support: str
    document_type: str


@dataclass(frozen=True)
class _OverrideContext:
    key: _ClusterKey
    decision: ReviewDecision
    finding: RiskFinding
    document_set: DocumentSet


@dataclass(frozen=True)
class _FindingAuditContext:
    agent_role: str
    prompt_version: str


def _finding_audit_context(
    *,
    audit_log: InMemoryAuditLog,
    finding: RiskFinding,
) -> _FindingAuditContext:
    events = audit_log.get_events_for_entity("RiskFinding", finding.finding_id)
    created_event = _latest_finding_created_event(events)
    if created_event is None:
        return _FindingAuditContext(
            agent_role=finding.model_name,
            prompt_version=finding.prompt_version,
        )
    metadata = created_event.metadata
    return _FindingAuditContext(
        agent_role=str(
            metadata.get("agent_role")
            or metadata.get("role")
            or metadata.get("agent_id")
            or finding.model_name
        ),
        prompt_version=str(metadata.get("prompt_version") or finding.prompt_version),
    )


def _latest_finding_created_event(events: list[AuditEvent]) -> AuditEvent | None:
    for event in reversed(events):
        if event.event_type == "finding_created":
            return event
    return None


def _recommendations(
    *,
    key: _ClusterKey,
    count: int,
    high_critical_recall_guard: bool,
) -> list[FalsePositiveRecommendation]:
    common_follow_up = [
        "Create a new version of the affected prompt, requirement, verifier, or policy.",
        "Run the evaluation harness before any operational use.",
        "Confirm that High/Critical recall is not reduced.",
    ]
    recommendations = [
        FalsePositiveRecommendation(
            recommendation_type=(
                FalsePositiveRecommendationType.PROMPT_CLARIFICATION_CANDIDATE
            ),
            rationale=(
                f"{count} human override(s) occurred for {key.agent_role} using "
                f"prompt {key.prompt_version}; clarify when this pattern should be "
                "raised as a finding."
            ),
            required_follow_up=common_follow_up,
        ),
        FalsePositiveRecommendation(
            recommendation_type=(
                FalsePositiveRecommendationType.REQUIREMENT_RULE_CLARIFICATION_CANDIDATE
            ),
            rationale=(
                f"Requirement {key.requirement_id} is repeatedly associated with "
                f"{key.risk_category} overrides for {key.document_type} documents."
            ),
            required_follow_up=[
                "Create a new requirement-library version before changing rule text.",
                "Run requirement match accuracy and recall evaluation.",
                "Record QA/Regulatory rationale for the rule clarification.",
            ],
        ),
        FalsePositiveRecommendation(
            recommendation_type=(
                FalsePositiveRecommendationType.DETERMINISTIC_VERIFIER_RULE_CANDIDATE
            ),
            rationale=(
                f"Evidence support was {key.evidence_support}; consider a deterministic "
                "verifier check that separates weak support from missing evidence."
            ),
            required_follow_up=[
                "Create a new verifier or policy version before using the rule.",
                "Run citation precision and false omission evaluation.",
                "Keep High/Critical findings reviewable unless independently resolved.",
            ],
        ),
    ]
    if not high_critical_recall_guard:
        recommendations.append(
            FalsePositiveRecommendation(
                recommendation_type=(
                    FalsePositiveRecommendationType.DO_NOT_AUTO_ESCALATE_PATTERN_CANDIDATE
                ),
                rationale=(
                    "This cluster is below High/Critical severity, so it can be reviewed "
                    "as a candidate pattern for avoiding unnecessary escalation."
                ),
                required_follow_up=[
                    "Create a new policy version before changing escalation behavior.",
                    "Run evals proving no High/Critical recall degradation.",
                    "Keep the recommendation advisory until human governance accepts it.",
                ],
            )
        )
    return recommendations


def _unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique_values.append(value)
    return unique_values


def _cluster_id(key: _ClusterKey) -> str:
    seed = "|".join(
        [
            key.requirement_id,
            key.risk_category,
            key.agent_role,
            key.prompt_version,
            key.evidence_support,
            key.document_type,
        ]
    )
    return f"fpcluster_{sha256(seed.encode()).hexdigest()[:16]}"
