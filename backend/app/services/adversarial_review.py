from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256

from app.audit.events import InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import (
    AdversarialChallenge,
    Claim,
    ClaimType,
    Criticality,
    EvidenceItem,
    EvidenceSupport,
    FindingStatus,
    Requirement,
    RiskFinding,
    Severity,
    SupportType,
)
from app.schemas.review import AdversarialReviewResponse, CoverageSummary


class AdversarialReviewDocumentSetNotFoundError(Exception):
    pass


class AdversarialReviewMissingPrimaryReviewError(Exception):
    pass


@dataclass(frozen=True)
class AdversarialReviewContext:
    document_set_id: str
    claims: Sequence[Claim]
    requirements: Sequence[Requirement]
    primary_findings: Sequence[RiskFinding]
    coverage_summaries: Sequence[CoverageSummary]
    document_quality_summary: Sequence[str]


@dataclass(frozen=True)
class AdversarialAgentResult:
    additional_findings: list[RiskFinding]
    challenged_findings: list[AdversarialChallenge]
    challenged_no_issue_claims: list[AdversarialChallenge]
    unresolved_questions: list[str]
    escalation_reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AdversarialAgent:
    agent_id: str
    role: str

    def run(self, context: AdversarialReviewContext) -> AdversarialAgentResult:
        if self.role == "MissedCriticalRiskHunter":
            return _run_missed_critical_risk_hunter(context, self.role)
        if self.role == "MissingEvidenceHunter":
            return _run_missing_evidence_hunter(context, self.role)
        if self.role == "CrossDocumentContradictionHunter":
            return _run_cross_document_contradiction_hunter(context, self.role)
        if self.role == "FalsePositiveSkeptic":
            return _run_false_positive_skeptic(context, self.role)
        if self.role == "FalseClearanceChallenger":
            return _run_false_clearance_challenger(context, self.role)
        return AdversarialAgentResult(
            additional_findings=[],
            challenged_findings=[],
            challenged_no_issue_claims=[],
            unresolved_questions=[],
            escalation_reasons=[],
        )


class AdversarialReviewService:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
        agents: Sequence[AdversarialAgent] | None = None,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log
        self.agents = list(agents) if agents is not None else default_adversarial_agents()

    def run_adversarial_review(self, document_set_id: str) -> AdversarialReviewResponse:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise AdversarialReviewDocumentSetNotFoundError(
                f"DocumentSet {document_set_id} not found"
            )

        primary_findings = self.repository.list_risk_findings(document_set_id)
        coverage_summaries = self.repository.list_coverage_summaries(document_set_id)
        if not primary_findings and not coverage_summaries:
            raise AdversarialReviewMissingPrimaryReviewError(
                "Adversarial review requires primary findings or coverage summaries"
            )

        requirement_set = self.repository.get_requirement_set(document_set.requirement_set_id)
        requirements = requirement_set.requirements if requirement_set is not None else []
        context = AdversarialReviewContext(
            document_set_id=document_set_id,
            claims=self.repository.list_claims(document_set_id),
            requirements=requirements,
            primary_findings=primary_findings,
            coverage_summaries=coverage_summaries,
            document_quality_summary=_document_quality_summary(
                repository=self.repository,
                document_set_id=document_set_id,
            ),
        )

        additional_findings: list[RiskFinding] = []
        challenged_findings: list[AdversarialChallenge] = []
        challenged_no_issue_claims: list[AdversarialChallenge] = []
        unresolved_questions: list[str] = []
        escalation_reasons = list(context.document_quality_summary)

        for agent in self.agents:
            result = agent.run(context)
            additional_findings.extend(result.additional_findings)
            challenged_findings.extend(result.challenged_findings)
            challenged_no_issue_claims.extend(result.challenged_no_issue_claims)
            unresolved_questions.extend(result.unresolved_questions)
            escalation_reasons.extend(result.escalation_reasons)

        additional_findings = _dedupe_findings(additional_findings)
        all_challenges = [*challenged_findings, *challenged_no_issue_claims]
        escalation_reasons.extend(
            _high_or_critical_escalation_reasons(
                findings=additional_findings,
                challenges=all_challenges,
            )
        )
        if context.document_quality_summary:
            unresolved_questions.extend(
                "Resolve document quality limitations before accepting any no-issue "
                "position from the primary review."
                for _item in context.document_quality_summary[:1]
            )
        self.repository.append_adversarial_challenges(
            document_set_id=document_set_id,
            challenges=all_challenges,
        )
        risk_fusion_findings = self.repository.replace_risk_fusion_findings(
            document_set_id=document_set_id,
            findings=[*primary_findings, *additional_findings],
        )

        self.audit_log.append(
            event_type="adversarial_review_run",
            actor_id=document_set.uploaded_by,
            entity_type="DocumentSet",
            entity_id=document_set_id,
            payload={
                "agent_roles": [agent.role for agent in self.agents],
                "primary_finding_ids": [
                    finding.finding_id for finding in primary_findings
                ],
                "additional_finding_ids": [
                    finding.finding_id for finding in additional_findings
                ],
                "challenge_ids": [
                    challenge.challenge_id for challenge in all_challenges
                ],
                "challenge_count": len(all_challenges),
                "unresolved_question_count": len(unresolved_questions),
                "escalation_reasons": _dedupe_text(escalation_reasons),
            },
        )

        return AdversarialReviewResponse(
            document_set_id=document_set_id,
            new_findings=additional_findings,
            additional_findings=additional_findings,
            challenged_findings=challenged_findings,
            challenged_no_issue_claims=challenged_no_issue_claims,
            unresolved_questions=_dedupe_text(unresolved_questions),
            escalation_reasons=_dedupe_text(escalation_reasons),
            risk_fusion_findings=risk_fusion_findings,
        )


def default_adversarial_agents() -> list[AdversarialAgent]:
    return [
        AdversarialAgent(
            agent_id="agent_missed_critical_risk_hunter",
            role="MissedCriticalRiskHunter",
        ),
        AdversarialAgent(
            agent_id="agent_missing_evidence_hunter",
            role="MissingEvidenceHunter",
        ),
        AdversarialAgent(
            agent_id="agent_cross_document_contradiction_hunter",
            role="CrossDocumentContradictionHunter",
        ),
        AdversarialAgent(
            agent_id="agent_false_positive_skeptic",
            role="FalsePositiveSkeptic",
        ),
        AdversarialAgent(
            agent_id="agent_false_clearance_challenger",
            role="FalseClearanceChallenger",
        ),
    ]


def _run_missed_critical_risk_hunter(
    context: AdversarialReviewContext,
    role: str,
) -> AdversarialAgentResult:
    high_risk_claims = [
        claim
        for claim in context.claims
        if claim.claim_type == ClaimType.IMPACT_ASSESSMENT and _looks_high_risk(claim)
    ]
    existing_high_risk_text = " ".join(
        finding.risk_statement.lower() for finding in context.primary_findings
    )

    findings: list[RiskFinding] = []
    questions: list[str] = []
    escalation_reasons: list[str] = []
    for claim in high_risk_claims:
        if claim.normalized_object.lower() in existing_high_risk_text:
            continue
        requirement = _first_high_or_critical_requirement(context.requirements)
        findings.append(
            _finding_from_claim(
                context=context,
                role=role,
                risk_category="missed_critical_risk",
                severity=Severity.HIGH,
                statement=(
                    "Adversarial review identified a potentially missed high-risk "
                    "impact claim that needs qualified human review."
                ),
                claim=claim,
                requirement=requirement,
                missing_information=["human assessment of whether the high-risk impact is covered"],
            )
        )
        questions.append(
            "Does the existing primary review fully address the high-risk impact claim "
            f"from {claim.document_id}/{claim.chunk_id}?"
        )
        escalation_reasons.append(
            "Potential High/Critical missed-risk claim requires human review."
        )

    for claim in context.claims:
        if not _is_unsupported_operator_error_root_cause(claim):
            continue
        requirement = _first_high_or_critical_requirement(context.requirements)
        findings.append(
            _finding_from_claim(
                context=context,
                role=role,
                risk_category="unsupported_root_cause",
                severity=Severity.HIGH,
                statement=(
                    "Adversarial review identified Root Cause 'Operator Error' without "
                    "sufficient documented rationale."
                ),
                claim=claim,
                requirement=requirement,
                missing_information=[
                    "documented rationale supporting Operator Error root cause",
                    "assessment of contributing process, training, equipment, or system factors",
                ],
            )
        )
        questions.append(
            "What documented evidence supports Operator Error as root cause, and were "
            "process, training, equipment, or system contributors evaluated?"
        )
        escalation_reasons.append(
            "Operator Error root cause lacks documented rationale and requires human review."
        )

    return AdversarialAgentResult(
        additional_findings=findings,
        challenged_findings=[],
        challenged_no_issue_claims=[],
        unresolved_questions=questions,
        escalation_reasons=escalation_reasons,
    )


def _run_missing_evidence_hunter(
    context: AdversarialReviewContext,
    role: str,
) -> AdversarialAgentResult:
    findings: list[RiskFinding] = []
    questions: list[str] = []
    escalation_reasons: list[str] = []
    supporting_claim = _first_claim(context.claims) or _first_primary_finding_claim_like(
        context.primary_findings
    )
    if supporting_claim is None:
        return AdversarialAgentResult([], [], [], [])

    claim_text = _claims_text(context.claims)
    for requirement in context.requirements:
        if requirement.criticality not in {Criticality.CRITICAL, Criticality.HIGH}:
            continue
        missing_evidence = [
            evidence
            for evidence in requirement.required_evidence
            if _required_evidence_missing(evidence, claim_text)
        ]
        if not missing_evidence:
            continue
        findings.append(
            _finding_from_claim(
                context=context,
                role=role,
                risk_category="missing_required_evidence",
                severity=_severity_from_criticality(requirement.criticality),
                statement=(
                    "Adversarial review found required evidence missing or not clearly "
                    "present in the claim ledger."
                ),
                claim=supporting_claim,
                requirement=requirement,
                missing_information=missing_evidence,
            )
        )
        questions.append(
            "Provide or cite the missing required evidence: " + ", ".join(missing_evidence)
        )
        escalation_reasons.append(
            "Required evidence is missing for a High/Critical requirement."
        )

    return AdversarialAgentResult(
        additional_findings=findings,
        challenged_findings=[],
        challenged_no_issue_claims=[],
        unresolved_questions=questions,
        escalation_reasons=escalation_reasons,
    )


def _run_cross_document_contradiction_hunter(
    context: AdversarialReviewContext,
    role: str,
) -> AdversarialAgentResult:
    challenges: list[AdversarialChallenge] = []
    seen: dict[str, Claim] = {}
    for claim in context.claims:
        existing = seen.get(claim.normalized_subject)
        if existing is None:
            seen[claim.normalized_subject] = claim
            continue
        if existing.normalized_object.lower() == claim.normalized_object.lower():
            continue
        severity = (
            Severity.HIGH
            if _looks_high_risk(claim) or _looks_high_risk(existing)
            else Severity.MEDIUM
        )
        challenges.append(
            AdversarialChallenge(
                challenge_id=_challenge_id(
                    role=role,
                    target_type="claim_contradiction",
                    target_id=claim.claim_id,
                    seed=existing.raw_text_quote + claim.raw_text_quote,
                ),
                document_set_id=context.document_set_id,
                target_type="claim_contradiction",
                target_id=claim.claim_id,
                agent_role=role,
                severity=severity,
                challenge_statement=(
                    "Potential contradiction detected for the same normalized subject."
                ),
                rationale=(
                    "Two claims share the same subject but state different normalized "
                    "objects. Human review should determine whether this is a real "
                    "document contradiction or contextual difference."
                ),
                evidence_items=[
                    _evidence_from_claim(existing, support_type=SupportType.CONTEXTUAL),
                    _evidence_from_claim(claim, support_type=SupportType.CONTRADICTS),
                ],
                missing_evidence=[],
                human_review_required=severity in {Severity.CRITICAL, Severity.HIGH},
                created_at=datetime.now(UTC),
            )
        )

    return AdversarialAgentResult(
        additional_findings=[],
        challenged_findings=challenges,
        challenged_no_issue_claims=[],
        unresolved_questions=[
            "Resolve cross-document contradiction before closing the related risk area."
        ]
        if challenges
        else [],
        escalation_reasons=[
            "Cross-document contradiction may affect a High/Critical risk area."
        ]
        if any(challenge.severity in {Severity.HIGH, Severity.CRITICAL} for challenge in challenges)
        else [],
    )


def _run_false_positive_skeptic(
    context: AdversarialReviewContext,
    role: str,
) -> AdversarialAgentResult:
    challenges: list[AdversarialChallenge] = []
    for finding in context.primary_findings:
        evidence_text = " ".join(item.quote for item in finding.evidence_items)
        if not _looks_like_linguistic_false_positive(
            risk_statement=finding.risk_statement,
            evidence_text=evidence_text,
        ):
            continue
        challenges.append(
            AdversarialChallenge(
                challenge_id=_challenge_id(
                    role=role,
                    target_type="finding_false_positive_check",
                    target_id=finding.finding_id,
                    seed=finding.risk_statement + evidence_text,
                ),
                document_set_id=context.document_set_id,
                target_type="finding_false_positive_check",
                target_id=finding.finding_id,
                agent_role=role,
                severity=finding.severity,
                challenge_statement=(
                    "Primary finding may be a false-positive caused by wording mismatch "
                    "between the finding and cited evidence."
                ),
                rationale=(
                    "The finding describes a missing or incomplete item, while the cited "
                    "evidence appears to say that the item was assessed, documented, "
                    "performed, or present. This challenge does not close the finding; "
                    "it asks the human reviewer to decide whether this is a real gap or "
                    "a linguistic misunderstanding."
                ),
                evidence_items=finding.evidence_items,
                missing_evidence=[
                    "human rationale confirming real gap versus wording mismatch"
                ],
                human_review_required=True,
                created_at=datetime.now(UTC),
            )
        )

    return AdversarialAgentResult(
        additional_findings=[],
        challenged_findings=challenges,
        challenged_no_issue_claims=[],
        unresolved_questions=[
            "Is the cited evidence actually contradicting the finding, making it a "
            "false-positive candidate?"
        ]
        if challenges
        else [],
        escalation_reasons=[
            "Potential false-positive candidate requires targeted human review."
        ]
        if challenges
        else [],
    )


def _run_false_clearance_challenger(
    context: AdversarialReviewContext,
    role: str,
) -> AdversarialAgentResult:
    challenged_findings: list[AdversarialChallenge] = []
    no_issue_challenges: list[AdversarialChallenge] = []
    high_risk_claim = next(
        (claim for claim in context.claims if _looks_high_risk(claim)),
        None,
    )

    for finding in context.primary_findings:
        if _finding_has_weak_or_missing_support(finding):
            challenged_findings.append(
                AdversarialChallenge(
                    challenge_id=_challenge_id(
                        role=role,
                        target_type="finding",
                        target_id=finding.finding_id,
                        seed=finding.risk_statement,
                    ),
                    document_set_id=context.document_set_id,
                    target_type="finding",
                    target_id=finding.finding_id,
                    agent_role=role,
                    severity=finding.severity,
                    challenge_statement=(
                        "Primary finding must not be treated as cleared because evidence "
                        "support is weak, partial, or missing."
                    ),
                    rationale=(
                        "The adversarial layer may not close findings. This challenge "
                        "keeps the item visible until qualified human review resolves the "
                        "missing or weak support."
                    ),
                    evidence_items=finding.evidence_items,
                    missing_evidence=_missing_from_finding(finding),
                    human_review_required=finding.severity
                    in {Severity.CRITICAL, Severity.HIGH},
                    created_at=datetime.now(UTC),
                )
            )

    if high_risk_claim is not None:
        for coverage_summary in context.coverage_summaries:
            if coverage_summary.finding_count != 0:
                continue
            no_issue_challenges.append(
                AdversarialChallenge(
                    challenge_id=_challenge_id(
                        role=role,
                        target_type="no_issue_claim",
                        target_id=coverage_summary.agent_id,
                        seed=coverage_summary.coverage_summary + high_risk_claim.raw_text_quote,
                    ),
                    document_set_id=context.document_set_id,
                    target_type="no_issue_claim",
                    target_id=coverage_summary.agent_id,
                    agent_role=role,
                    severity=Severity.HIGH,
                    challenge_statement=(
                        "No-issue coverage summary conflicts with a high-risk claim in "
                        "the claim ledger."
                    ),
                    rationale=(
                        "A reviewer reported no findings while the claim ledger contains "
                        "a potentially high-risk impact. This is not an automatic error, "
                        "but it cannot be silently cleared."
                    ),
                    evidence_items=[
                        _evidence_from_claim(
                            high_risk_claim,
                            support_type=SupportType.CONTEXTUAL,
                        )
                    ],
                    missing_evidence=["coverage rationale explaining why no issue was found"],
                    human_review_required=True,
                    created_at=datetime.now(UTC),
                )
            )

    return AdversarialAgentResult(
        additional_findings=[],
        challenged_findings=challenged_findings,
        challenged_no_issue_claims=no_issue_challenges,
        unresolved_questions=[
            "Can the primary reviewer justify the no-issue or weak-support position "
            "against the cited high-risk evidence?"
        ]
        if challenged_findings or no_issue_challenges
        else [],
        escalation_reasons=[
            "No-issue or weak-support primary position conflicts with high-risk evidence."
        ]
        if challenged_findings or no_issue_challenges
        else [],
    )


def _finding_from_claim(
    *,
    context: AdversarialReviewContext,
    role: str,
    risk_category: str,
    severity: Severity,
    statement: str,
    claim: Claim,
    requirement: Requirement | None,
    missing_information: list[str],
) -> RiskFinding:
    seed = "|".join([context.document_set_id, role, risk_category, claim.raw_text_quote])
    requirement_references = [requirement.requirement_id] if requirement is not None else []
    return RiskFinding(
        finding_id=f"finding_{sha256(seed.encode()).hexdigest()[:20]}",
        document_set_id=context.document_set_id,
        risk_category=risk_category,
        severity=severity,
        likelihood=3,
        detectability=3,
        risk_statement=statement,
        evidence_items=[_evidence_from_claim(claim, support_type=SupportType.CONTEXTUAL)],
        requirement_references=requirement_references,
        missing_information=missing_information,
        model_provider="adversarial-rule-layer",
        model_name=role,
        model_version="0.1.0",
        prompt_version="adversarial-review-v0.1",
        evidence_support=EvidenceSupport.PARTIAL if missing_information else EvidenceSupport.STRONG,
        recommended_action="Route to human review; adversarial layer cannot close findings.",
        auto_close_allowed=False,
        status=FindingStatus.NEEDS_HUMAN_REVIEW,
    )


def _evidence_from_claim(claim: Claim, *, support_type: SupportType) -> EvidenceItem:
    return EvidenceItem(
        document_id=claim.document_id,
        chunk_id=claim.chunk_id,
        page=claim.page,
        quote=claim.raw_text_quote,
        quote_hash=sha256(claim.raw_text_quote.encode()).hexdigest(),
        support_type=support_type,
        verifier_score=claim.confidence,
    )


def _first_high_or_critical_requirement(
    requirements: Sequence[Requirement],
) -> Requirement | None:
    return next(
        (
            requirement
            for requirement in requirements
            if requirement.criticality in {Criticality.CRITICAL, Criticality.HIGH}
        ),
        None,
    )


def _first_claim(claims: Sequence[Claim]) -> Claim | None:
    return next(iter(claims), None)


def _first_primary_finding_claim_like(
    primary_findings: Sequence[RiskFinding],
) -> Claim | None:
    if not primary_findings or not primary_findings[0].evidence_items:
        return None
    evidence = primary_findings[0].evidence_items[0]
    return Claim(
        claim_id="claim_adversarial_context_from_primary_finding",
        document_id=evidence.document_id,
        chunk_id=evidence.chunk_id,
        page=evidence.page,
        claim_type=ClaimType.MISSING_OR_UNCLEAR,
        normalized_subject=primary_findings[0].risk_category,
        normalized_predicate="has_missing_evidence",
        normalized_object=", ".join(primary_findings[0].missing_information)
        or primary_findings[0].risk_statement,
        raw_text_quote=evidence.quote,
        confidence=evidence.verifier_score,
        dependencies=[],
        created_by_model="adversarial-review-v0.1",
        prompt_version="adversarial-review-v0.1",
    )


def _looks_high_risk(claim: Claim) -> bool:
    text = " ".join(
        [
            claim.normalized_subject,
            claim.normalized_object,
            claim.raw_text_quote,
        ]
    ).lower()
    high_risk_terms = {
        "critical",
        "patient",
        "sterility",
        "contamination",
        "false accept",
        "defective container",
        "missing current validation",
        "no validation",
        "unvalidated",
    }
    return any(term in text for term in high_risk_terms)


def _looks_like_linguistic_false_positive(
    *,
    risk_statement: str,
    evidence_text: str,
) -> bool:
    statement = risk_statement.lower()
    evidence = evidence_text.lower()
    gap_markers = {
        "missing",
        "incomplete",
        "lacks",
        "lack of",
        "without",
        "not documented",
        "not assessed",
        "not justified",
    }
    completion_markers = {
        "was assessed",
        "were assessed",
        "is assessed",
        "documented",
        "completed",
        "approved",
        "included",
        "available",
        "performed",
        "present",
        "justified",
    }
    evidence_gap_markers = {
        "missing ",
        "not documented",
        "without ",
        "not assessed",
        "not justified",
        "incomplete",
    }
    return (
        any(marker in statement for marker in gap_markers)
        and any(marker in evidence for marker in completion_markers)
        and not any(marker in evidence for marker in evidence_gap_markers)
    )


def _is_unsupported_operator_error_root_cause(claim: Claim) -> bool:
    if claim.claim_type != ClaimType.ROOT_CAUSE:
        return False
    text = " ".join(
        [
            claim.normalized_subject,
            claim.normalized_object,
            claim.raw_text_quote,
        ]
    ).lower()
    if "operator error" not in text:
        return False
    rationale_markers = {
        "because",
        "due to",
        "based on",
        "investigation found",
        "training record",
        "interview",
        "documented rationale",
    }
    return not any(marker in text for marker in rationale_markers)


def _document_quality_summary(
    *,
    repository: InMemoryDocumentRepository,
    document_set_id: str,
) -> list[str]:
    document_set = repository.get_document_set(document_set_id)
    if document_set is None:
        return [f"Document quality summary unavailable for {document_set_id}."]
    reasons: list[str] = []
    for document_id in document_set.document_ids:
        document = repository.get_document(document_id)
        if document is None:
            reasons.append(f"Document quality issue: referenced document missing: {document_id}.")
            continue
        if document.parsing_quality_score < 0.65:
            reasons.append(
                "Document quality issue: "
                f"{document.document_id} parsing_quality_score="
                f"{document.parsing_quality_score:.2f}."
            )
        if str(document.parsing_status) != "parsed":
            reasons.append(
                "Document quality issue: "
                f"{document.document_id} parsing_status={document.parsing_status}."
            )
    return reasons


def _claims_text(claims: Sequence[Claim]) -> str:
    parts: list[str] = []
    for claim in claims:
        parts.extend(
            [
            claim.normalized_subject,
            claim.normalized_predicate,
            claim.normalized_object,
            claim.raw_text_quote,
            ]
        )
    return " ".join(parts).lower()


def _required_evidence_missing(required_evidence: str, claim_text: str) -> bool:
    normalized = required_evidence.lower()
    return not (normalized in claim_text and not any(
        marker in claim_text
        for marker in [
            f"missing {normalized}",
            f"no {normalized}",
            f"without {normalized}",
        ]
    ))


def _severity_from_criticality(criticality: Criticality) -> Severity:
    if criticality == Criticality.CRITICAL:
        return Severity.CRITICAL
    if criticality == Criticality.HIGH:
        return Severity.HIGH
    if criticality == Criticality.MEDIUM:
        return Severity.MEDIUM
    if criticality == Criticality.LOW:
        return Severity.LOW
    return Severity.INFORMATIONAL


def _finding_has_weak_or_missing_support(finding: RiskFinding) -> bool:
    if finding.evidence_support in {
        EvidenceSupport.PARTIAL,
        EvidenceSupport.WEAK,
        EvidenceSupport.NONE,
    }:
        return True
    if finding.missing_information:
        return True
    if finding.verification_result is None:
        return False
    return not finding.verification_result.deterministic_checks_passed


def _missing_from_finding(finding: RiskFinding) -> list[str]:
    missing = list(finding.missing_information)
    if finding.verification_result is not None:
        missing.extend(finding.verification_result.missing_evidence)
        missing.extend(finding.verification_result.unsupported_claims)
    return _dedupe_text(missing) or ["human rationale for clearance is missing or weak"]


def _high_or_critical_escalation_reasons(
    *,
    findings: Sequence[RiskFinding],
    challenges: Sequence[AdversarialChallenge],
) -> list[str]:
    reasons: list[str] = []
    for finding in findings:
        if finding.severity in {Severity.CRITICAL, Severity.HIGH}:
            reasons.append(
                f"{finding.severity} adversarial finding requires human review: "
                f"{finding.risk_category}."
            )
    for challenge in challenges:
        if challenge.severity in {Severity.CRITICAL, Severity.HIGH}:
            reasons.append(
                f"{challenge.severity} adversarial challenge requires human review: "
                f"{challenge.target_type}."
            )
    return reasons


def _challenge_id(*, role: str, target_type: str, target_id: str, seed: str) -> str:
    digest = sha256("|".join([role, target_type, target_id, seed]).encode()).hexdigest()
    return f"challenge_{digest[:20]}"


def _dedupe_findings(findings: Sequence[RiskFinding]) -> list[RiskFinding]:
    deduplicated: dict[str, RiskFinding] = {}
    for finding in findings:
        deduplicated[finding.finding_id] = finding
    return list(deduplicated.values())


def _dedupe_text(items: Sequence[str]) -> list[str]:
    deduplicated: list[str] = []
    for item in items:
        if item and item not in deduplicated:
            deduplicated.append(item)
    return deduplicated
