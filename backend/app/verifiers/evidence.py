from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Protocol

from app.audit.events import InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import (
    DocumentSet,
    EvidenceSupport,
    FindingVerificationResult,
    Requirement,
    RiskFinding,
    Severity,
)


class LLMEvidenceVerifier(Protocol):
    verifier_name: str
    verifier_version: str

    def verify(self, finding: RiskFinding) -> FindingVerificationResult:
        ...


class StubLLMEvidenceVerifier:
    verifier_name = "llm-evidence-verifier-stub"
    verifier_version = "0.1.0"

    def verify(self, finding: RiskFinding) -> FindingVerificationResult:
        raise NotImplementedError("LLM evidence verifier is a stub and makes no API calls.")


@dataclass(frozen=True)
class CitationCheckResult:
    quote_exists: bool
    quote_matches_chunk: bool
    page_plausible: bool
    claim_support: EvidenceSupport
    unsupported_claims: list[str]
    missing_evidence: list[str]


class CitationIntegrityChecker:
    def __init__(self, *, repository: InMemoryDocumentRepository) -> None:
        self.repository = repository

    def check(self, finding: RiskFinding) -> CitationCheckResult:
        quote_exists = True
        quote_matches_chunk = True
        page_plausible = True
        unsupported_claims: list[str] = []
        missing_evidence: list[str] = []
        quote_texts: list[str] = []

        for evidence_item in finding.evidence_items:
            document = self.repository.get_document(evidence_item.document_id)
            if document is None:
                quote_exists = False
                quote_matches_chunk = False
                page_plausible = False
                missing_evidence.append(f"document_id does not exist: {evidence_item.document_id}")
                continue

            chunk = self.repository.get_chunk(
                document_id=evidence_item.document_id,
                chunk_id=evidence_item.chunk_id,
            )
            if chunk is None:
                quote_exists = False
                quote_matches_chunk = False
                page_plausible = False
                missing_evidence.append(f"chunk_id does not exist: {evidence_item.chunk_id}")
                continue

            if not evidence_item.quote.strip():
                quote_exists = False
                quote_matches_chunk = False
                missing_evidence.append("evidence quote is empty")
                continue

            if not _quote_matches_chunk(evidence_item.quote, chunk.text):
                quote_exists = False
                quote_matches_chunk = False
                unsupported_claims.append(
                    f"quote does not match source chunk: {evidence_item.quote}"
                )
            else:
                quote_texts.append(evidence_item.quote)

            if not chunk.page_start <= evidence_item.page <= chunk.page_end:
                page_plausible = False
                missing_evidence.append(
                    f"page {evidence_item.page} is not plausible for chunk {chunk.chunk_id}"
                )

        claim_support, claim_issues = _claim_support(
            risk_statement=finding.risk_statement,
            evidence_quotes=quote_texts,
        )
        unsupported_claims.extend(claim_issues)
        return CitationCheckResult(
            quote_exists=quote_exists,
            quote_matches_chunk=quote_matches_chunk,
            page_plausible=page_plausible,
            claim_support=claim_support,
            unsupported_claims=unsupported_claims,
            missing_evidence=missing_evidence,
        )


@dataclass(frozen=True)
class RequirementMatchResult:
    requirement_applicable: bool
    auto_close_allowed_considered: bool
    missing_evidence: list[str]


class RequirementMatcherVerifier:
    def __init__(self, *, repository: InMemoryDocumentRepository) -> None:
        self.repository = repository

    def check(self, *, document_set_id: str, finding: RiskFinding) -> RequirementMatchResult:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            return RequirementMatchResult(
                requirement_applicable=False,
                auto_close_allowed_considered=False,
                missing_evidence=[f"document_set_id does not exist: {document_set_id}"],
            )

        requirement_set = self.repository.get_requirement_set(document_set.requirement_set_id)
        if requirement_set is None:
            return RequirementMatchResult(
                requirement_applicable=False,
                auto_close_allowed_considered=False,
                missing_evidence=[
                    f"requirement_set_id does not exist: {document_set.requirement_set_id}"
                ],
            )

        if not finding.requirement_references:
            return RequirementMatchResult(
                requirement_applicable=False,
                auto_close_allowed_considered=not finding.auto_close_allowed,
                missing_evidence=["finding has no requirement references"],
            )

        requirements_by_id = {
            requirement.requirement_id: requirement for requirement in requirement_set.requirements
        }
        missing_evidence: list[str] = []
        applicable_requirements: list[Requirement] = []
        auto_close_allowed_considered = True

        for requirement_id in finding.requirement_references:
            requirement = requirements_by_id.get(requirement_id)
            if requirement is None:
                missing_evidence.append(f"requirement_id does not exist: {requirement_id}")
                continue

            if not _requirement_applies(requirement, document_set):
                missing_evidence.append(
                    f"requirement_id is not applicable to document/process area: {requirement_id}"
                )
                continue

            applicable_requirements.append(requirement)
            if finding.auto_close_allowed and not requirement.auto_close_allowed:
                auto_close_allowed_considered = False
                missing_evidence.append(
                    f"auto_close_allowed conflicts with requirement: {requirement_id}"
                )

        if finding.severity in {Severity.HIGH, Severity.CRITICAL} and finding.auto_close_allowed:
            auto_close_allowed_considered = False
            missing_evidence.append("high or critical finding must not be auto-closed")

        return RequirementMatchResult(
            requirement_applicable=bool(applicable_requirements),
            auto_close_allowed_considered=auto_close_allowed_considered,
            missing_evidence=missing_evidence,
        )


class EvidenceVerifierService:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log
        self.citation_checker = CitationIntegrityChecker(repository=repository)
        self.requirement_checker = RequirementMatcherVerifier(repository=repository)

    def verify_findings(
        self,
        document_set_id: str,
        findings: Sequence[RiskFinding],
    ) -> list[RiskFinding]:
        results = [self.verify_finding(document_set_id, finding) for finding in findings]
        verified_findings = [
            finding.model_copy(update={"verification_result": result})
            for finding, result in zip(findings, results, strict=True)
        ]
        self.repository.replace_verification_results(
            document_set_id=document_set_id,
            results=results,
        )
        self.repository.replace_risk_findings(
            document_set_id=document_set_id,
            findings=verified_findings,
        )
        for result in results:
            self.audit_log.append(
                event_type="finding_verified",
                actor_id="service_evidence_verifier",
                actor_type="service",
                entity_type="RiskFinding",
                entity_id=result.finding_id,
                payload={
                    "document_set_id": document_set_id,
                    "evidence_support": result.evidence_support,
                    "deterministic_checks_passed": result.deterministic_checks_passed,
                    "quote_exists": result.quote_exists,
                    "quote_matches_chunk": result.quote_matches_chunk,
                    "requirement_applicable": result.requirement_applicable,
                    "missing_evidence_count": len(result.missing_evidence),
                    "unsupported_claim_count": len(result.unsupported_claims),
                },
            )
        self.audit_log.append(
            event_type="evidence_verifier_run",
            actor_id="user_system",
            entity_type="DocumentSet",
            entity_id=document_set_id,
            payload={
                "finding_count": len(findings),
                "strong_count": sum(
                    1 for result in results if result.evidence_support == EvidenceSupport.STRONG
                ),
                "partial_count": sum(
                    1 for result in results if result.evidence_support == EvidenceSupport.PARTIAL
                ),
                "weak_count": sum(
                    1 for result in results if result.evidence_support == EvidenceSupport.WEAK
                ),
                "none_count": sum(
                    1 for result in results if result.evidence_support == EvidenceSupport.NONE
                ),
            },
        )
        return verified_findings

    def verify_finding(
        self,
        document_set_id: str,
        finding: RiskFinding,
    ) -> FindingVerificationResult:
        citation_result = self.citation_checker.check(finding)
        requirement_result = self.requirement_checker.check(
            document_set_id=document_set_id,
            finding=finding,
        )
        missing_evidence = [
            *citation_result.missing_evidence,
            *requirement_result.missing_evidence,
            *finding.missing_information,
        ]
        deterministic_checks_passed = (
            citation_result.quote_exists
            and citation_result.quote_matches_chunk
            and citation_result.page_plausible
            and citation_result.claim_support == EvidenceSupport.STRONG
            and requirement_result.requirement_applicable
            and requirement_result.auto_close_allowed_considered
            and not missing_evidence
        )
        evidence_support = _classify_support(
            citation_result=citation_result,
            requirement_result=requirement_result,
            finding=finding,
            missing_evidence=missing_evidence,
        )
        rationale = _rationale(
            evidence_support=evidence_support,
            deterministic_checks_passed=deterministic_checks_passed,
            requirement_applicable=requirement_result.requirement_applicable,
        )
        return FindingVerificationResult(
            finding_id=finding.finding_id,
            evidence_support=evidence_support,
            quote_exists=citation_result.quote_exists,
            quote_matches_chunk=citation_result.quote_matches_chunk,
            requirement_applicable=requirement_result.requirement_applicable,
            unsupported_claims=citation_result.unsupported_claims,
            missing_evidence=missing_evidence,
            verifier_rationale=rationale,
            verifier_model_run_id=None,
            deterministic_checks_passed=deterministic_checks_passed,
        )


def _quote_matches_chunk(quote: str, chunk_text: str) -> bool:
    normalized_quote = _normalize(quote)
    normalized_chunk = _normalize(chunk_text)
    if normalized_quote in normalized_chunk:
        return True
    return SequenceMatcher(None, normalized_quote, normalized_chunk).ratio() >= 0.82


def _normalize(value: str) -> str:
    return " ".join(value.lower().split())


def _claim_support(
    *,
    risk_statement: str,
    evidence_quotes: Sequence[str],
) -> tuple[EvidenceSupport, list[str]]:
    if not evidence_quotes:
        return EvidenceSupport.NONE, ["risk statement has no matching evidence quote"]

    evidence_text = " ".join(evidence_quotes)
    evidence_tokens = _meaningful_tokens(evidence_text)
    if not evidence_tokens:
        return EvidenceSupport.NONE, ["evidence quote has no meaningful support tokens"]

    clause_scores = [
        _token_support_score(clause, evidence_tokens)
        for clause in _risk_statement_clauses(risk_statement)
    ]
    if not clause_scores:
        return EvidenceSupport.NONE, ["risk statement has no verifiable claim text"]

    unsupported_clauses = [
        clause for clause, score in clause_scores if score < 0.2 and clause.strip()
    ]
    partially_supported_clauses = [
        clause for clause, score in clause_scores if 0.2 <= score < 0.5 and clause.strip()
    ]
    if len(unsupported_clauses) == len(clause_scores):
        return EvidenceSupport.NONE, [
            "risk statement is not supported by linked evidence quote"
        ]
    if unsupported_clauses or partially_supported_clauses:
        issues = [
            f"risk statement clause is not fully supported by linked evidence: {clause}"
            for clause in [*unsupported_clauses, *partially_supported_clauses]
        ]
        return EvidenceSupport.PARTIAL, issues
    return EvidenceSupport.STRONG, []


def _risk_statement_clauses(risk_statement: str) -> list[str]:
    import re

    return [
        clause.strip()
        for clause in re.split(r"\b(?:but|and|while|with|without)\b|[.;:]", risk_statement)
        if clause.strip()
    ]


def _token_support_score(clause: str, evidence_tokens: set[str]) -> tuple[str, float]:
    claim_tokens = _meaningful_tokens(clause)
    if not claim_tokens:
        return clause, 1.0
    supported_tokens = claim_tokens.intersection(evidence_tokens)
    return clause, len(supported_tokens) / len(claim_tokens)


def _meaningful_tokens(value: str) -> set[str]:
    import re

    tokens = {
        token
        for token in re.findall(r"[a-zA-Z0-9]+", value.lower())
        if len(token) >= 3 and token not in _SUPPORT_STOPWORDS
    }
    return {_TOKEN_SYNONYMS.get(token, token) for token in tokens}


def _requirement_applies(requirement: Requirement, document_set: DocumentSet) -> bool:
    document_type = document_set.declared_document_type
    process_area = document_set.declared_process_area
    return (
        document_type in requirement.applies_to_document_types
        and process_area in requirement.applies_to_process_areas
    )


def _classify_support(
    *,
    citation_result: CitationCheckResult,
    requirement_result: RequirementMatchResult,
    finding: RiskFinding,
    missing_evidence: list[str],
) -> EvidenceSupport:
    if not citation_result.quote_exists:
        return EvidenceSupport.NONE
    if citation_result.claim_support == EvidenceSupport.NONE:
        return EvidenceSupport.NONE
    if citation_result.quote_matches_chunk and requirement_result.requirement_applicable:
        if citation_result.claim_support == EvidenceSupport.PARTIAL:
            return EvidenceSupport.PARTIAL
        if missing_evidence:
            return EvidenceSupport.PARTIAL
        return EvidenceSupport.STRONG
    if citation_result.quote_matches_chunk or requirement_result.requirement_applicable:
        return EvidenceSupport.WEAK
    return EvidenceSupport.NONE


def _rationale(
    *,
    evidence_support: EvidenceSupport,
    deterministic_checks_passed: bool,
    requirement_applicable: bool,
) -> str:
    if deterministic_checks_passed:
        return "Deterministic citation and requirement checks passed."
    if not requirement_applicable:
        return (
            f"Deterministic checks found {evidence_support} evidence; "
            "at least one referenced requirement is missing or not applicable."
        )
    return (
        f"Deterministic checks found {evidence_support} evidence; "
        "human review remains required before relying on the finding."
    )


_SUPPORT_STOPWORDS = {
    "about",
    "accepted",
    "assessment",
    "claim",
    "closed",
    "concrete",
    "documented",
    "finding",
    "identified",
    "identifies",
    "indicate",
    "indicated",
    "indicates",
    "issue",
    "possible",
    "review",
    "risk",
    "should",
    "statement",
    "supported",
    "unsupported",
}

_TOKEN_SYNONYMS = {
    "accept": "accept",
    "accepted": "accept",
    "acceptance": "accept",
    "approval": "approval",
    "approved": "approval",
    "defect": "defective",
    "defects": "defective",
    "deviation": "deviation",
    "deviations": "deviation",
}
