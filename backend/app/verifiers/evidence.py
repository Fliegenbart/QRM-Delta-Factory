from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher
from hashlib import sha256
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
    multi_document_synthesis_valid: bool
    multi_document_semantic_support: bool
    unsupported_claims: list[str]
    missing_evidence: list[str]


class CitationIntegrityChecker:
    def __init__(self, *, repository: InMemoryDocumentRepository) -> None:
        self.repository = repository

    def check(
        self,
        finding: RiskFinding,
        *,
        requirement_texts: Sequence[str] = (),
    ) -> CitationCheckResult:
        quote_exists = True
        quote_matches_chunk = True
        page_plausible = True
        unsupported_claims: list[str] = []
        missing_evidence: list[str] = []
        quote_texts: list[str] = []
        exact_quote_document_ids: set[str] = set()
        exact_quotes_by_document: dict[str, list[str]] = {}
        multi_document_finding = len(finding.evidence_items) >= 2

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

            quote_hash_matches = (
                sha256(evidence_item.quote.encode()).hexdigest()
                == evidence_item.quote_hash
            )
            quote_matches_source = (
                _strict_quote_matches_chunk(evidence_item.quote, chunk.text)
                if multi_document_finding
                else _quote_matches_chunk(evidence_item.quote, chunk.text)
            )
            if multi_document_finding and not quote_hash_matches:
                quote_exists = False
                quote_matches_chunk = False
                missing_evidence.append(
                    f"quote_hash does not match evidence quote: {evidence_item.document_id}"
                )

            if not quote_matches_source:
                quote_exists = False
                quote_matches_chunk = False
                unsupported_claims.append(
                    f"quote does not match source chunk: {evidence_item.quote}"
                )
            elif quote_hash_matches or not multi_document_finding:
                quote_texts.append(evidence_item.quote)
                exact_quote_document_ids.add(evidence_item.document_id)
                exact_quotes_by_document.setdefault(evidence_item.document_id, []).append(
                    evidence_item.quote
                )

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
        multi_document_synthesis_valid = _multi_document_synthesis_is_valid(
            finding=finding,
            exact_quote_document_ids=exact_quote_document_ids,
            evidence_quotes=quote_texts,
            unsupported_claims=unsupported_claims,
            missing_evidence=missing_evidence,
        )
        multi_document_semantic_support = _multi_document_claim_is_semantically_supported(
            finding=finding,
            exact_quotes_by_document=exact_quotes_by_document,
            requirement_texts=requirement_texts,
        )
        if (
            len(finding.evidence_items) >= 2
            and multi_document_synthesis_valid
            and not multi_document_semantic_support
        ):
            quote_concepts = _synthesis_concepts(" ".join(quote_texts))
            requirement_concepts = _synthesis_concepts(" ".join(requirement_texts))
            unsupported_claims.extend(
                f"risk statement material clause lacks multi-document concept support: {clause}"
                for clause in _unsupported_material_clauses(
                    risk_statement=finding.risk_statement,
                    quote_concepts=quote_concepts,
                    requirement_concepts=requirement_concepts,
                )
            )
        if (
            len(finding.evidence_items) >= 2
            and multi_document_synthesis_valid
            and multi_document_semantic_support
        ):
            unsupported_claims = [
                issue for issue in unsupported_claims if issue not in claim_issues
            ]
        return CitationCheckResult(
            quote_exists=quote_exists,
            quote_matches_chunk=quote_matches_chunk,
            page_plausible=page_plausible,
            claim_support=claim_support,
            multi_document_synthesis_valid=multi_document_synthesis_valid,
            multi_document_semantic_support=multi_document_semantic_support,
            unsupported_claims=unsupported_claims,
            missing_evidence=missing_evidence,
        )


@dataclass(frozen=True)
class RequirementMatchResult:
    requirement_applicable: bool
    auto_close_allowed_considered: bool
    missing_evidence: list[str]
    applicable_requirement_texts: list[str]


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
                applicable_requirement_texts=[],
            )

        requirement_set = self.repository.get_requirement_set(document_set.requirement_set_id)
        if requirement_set is None:
            return RequirementMatchResult(
                requirement_applicable=False,
                auto_close_allowed_considered=False,
                missing_evidence=[
                    f"requirement_set_id does not exist: {document_set.requirement_set_id}"
                ],
                applicable_requirement_texts=[],
            )

        if not finding.requirement_references:
            return RequirementMatchResult(
                requirement_applicable=False,
                auto_close_allowed_considered=not finding.auto_close_allowed,
                missing_evidence=["finding has no requirement references"],
                applicable_requirement_texts=[],
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
            applicable_requirement_texts=[
                requirement.requirement_text for requirement in applicable_requirements
            ],
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
        requirement_result = self.requirement_checker.check(
            document_set_id=document_set_id,
            finding=finding,
        )
        citation_result = self.citation_checker.check(
            finding,
            requirement_texts=requirement_result.applicable_requirement_texts,
        )
        missing_evidence = [
            *citation_result.missing_evidence,
            *requirement_result.missing_evidence,
            *finding.missing_information,
        ]
        claim_support_is_sufficient = citation_result.claim_support == EvidenceSupport.STRONG or (
            len(finding.evidence_items) >= 2
            and citation_result.multi_document_synthesis_valid
            and citation_result.multi_document_semantic_support
        )
        deterministic_checks_passed = (
            citation_result.quote_exists
            and citation_result.quote_matches_chunk
            and citation_result.page_plausible
            and claim_support_is_sufficient
            and citation_result.multi_document_synthesis_valid
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


def _strict_quote_matches_chunk(quote: str, chunk_text: str) -> bool:
    return _normalize_strict_quote(quote) in _normalize_strict_quote(chunk_text)


def _normalize_strict_quote(value: str) -> str:
    """Ignore presentation-only Markdown markers without altering quote content."""
    return _normalize(value.replace("**", "").replace("__", "").replace("`", ""))


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


def _multi_document_synthesis_is_valid(
    *,
    finding: RiskFinding,
    exact_quote_document_ids: set[str],
    evidence_quotes: Sequence[str],
    unsupported_claims: list[str],
    missing_evidence: list[str],
) -> bool:
    """Validate claims deliberately synthesized from more than one citation.

    Single-citation findings retain the established lexical verifier behavior.  A
    finding that supplies multiple citations, however, is asserting a synthesis
    across them and must meet stricter, deterministic provenance constraints.
    """
    if len(finding.evidence_items) < 2:
        return True

    valid = True
    if len(exact_quote_document_ids) < 2:
        missing_evidence.append(
            "multi-document synthesis requires at least two distinct source documents"
        )
        valid = False

    normalized_quotes = [_normalize_strict_quote(quote) for quote in evidence_quotes]
    if len(set(normalized_quotes)) != len(normalized_quotes):
        missing_evidence.append(
            "multi-document synthesis requires non-duplicate exact evidence quotes"
        )
        valid = False

    non_supporting_evidence = [
        evidence_item
        for evidence_item in finding.evidence_items
        if evidence_item.support_type.value != "supports"
    ]
    if non_supporting_evidence:
        unsupported_claims.append(
            "multi-document synthesis requires every evidence item to have support_type=supports"
        )
        valid = False

    exact_quote_text = _normalize(" ".join(evidence_quotes))
    uncovered_anchors = [
        anchor
        for anchor in _factual_anchors(finding.risk_statement)
        if _normalize(anchor) not in exact_quote_text
    ]
    if uncovered_anchors:
        unsupported_claims.extend(
            f"factual anchor is not covered by exact evidence quotes: {anchor}"
            for anchor in uncovered_anchors
        )
        valid = False
    return valid


def _multi_document_claim_is_semantically_supported(
    *,
    finding: RiskFinding,
    exact_quotes_by_document: dict[str, list[str]],
    requirement_texts: Sequence[str],
) -> bool:
    """Require multi-source concept coverage before promoting a synthesis.

    This is intentionally a small deterministic guard, not an inference engine:
    the risk must share at least two normalized concepts with the exact quote
    corpus, the support must span source documents, and explicit anchors are
    counted only after their exact-quote check elsewhere has succeeded.
    """
    if len(finding.evidence_items) < 2:
        return True

    claim_concepts = _synthesis_concepts(finding.risk_statement)
    if not claim_concepts:
        return False

    requirement_concepts = _synthesis_concepts(" ".join(requirement_texts))
    quote_concepts_by_document = {
        document_id: _synthesis_concepts(" ".join(quotes))
        for document_id, quotes in exact_quotes_by_document.items()
    }
    quote_corpus_concepts = set().union(*quote_concepts_by_document.values())
    if _unsupported_material_clauses(
        risk_statement=finding.risk_statement,
        quote_concepts=quote_corpus_concepts,
        requirement_concepts=requirement_concepts,
    ):
        return False

    concept_sources: dict[str, set[str]] = {}
    for document_id, quote_concepts in quote_concepts_by_document.items():
        for concept in claim_concepts.intersection(quote_concepts):
            concept_sources.setdefault(concept, set()).add(document_id)

    quote_concepts = set(concept_sources)
    required_concepts = claim_concepts.intersection(requirement_concepts)
    covered_concepts = quote_concepts.union(required_concepts)
    anchors = _factual_anchors(finding.risk_statement)
    anchor_sources = {
        document_id
        for document_id, quotes in exact_quotes_by_document.items()
        if any(_normalize(anchor) in _normalize(" ".join(quotes)) for anchor in anchors)
    }
    supporting_documents = {
        document_id
        for document_id, quote_concepts in quote_concepts_by_document.items()
        if quote_concepts.intersection(claim_concepts)
    }.union(anchor_sources)

    return (
        len(quote_concepts) >= 2
        and len(covered_concepts) + len(anchors) >= 3
        and len(supporting_documents) >= 2
    )


def _synthesis_clauses(risk_statement: str) -> list[str]:
    import re

    return [
        clause.strip()
        for clause in re.split(r";|(?<!\d)\.(?!\d)", risk_statement)
        if _synthesis_concepts(clause)
    ]


def _material_clause_is_supported(
    *,
    clause: str,
    quote_concepts: set[str],
    requirement_concepts: set[str],
) -> bool:
    clause_concepts = _synthesis_concepts(clause)
    covered_concepts = clause_concepts.intersection(
        quote_concepts.union(requirement_concepts)
    )
    return len(covered_concepts) >= 2 and covered_concepts == clause_concepts


def _unsupported_material_clauses(
    *,
    risk_statement: str,
    quote_concepts: set[str],
    requirement_concepts: set[str],
) -> list[str]:
    return [
        clause
        for clause in _synthesis_clauses(risk_statement)
        if not _material_clause_is_supported(
            clause=clause,
            quote_concepts=quote_concepts,
            requirement_concepts=requirement_concepts,
        )
    ]


def _synthesis_concepts(value: str) -> set[str]:
    import re

    value = value.replace("N/A", " optional ").replace("n/a", " optional ")
    tokens = {
        token
        for token in re.findall(r"[^\W_]+", value.lower(), flags=re.UNICODE)
        if len(token) >= 3 and token not in _SYNTHESIS_STOPWORDS
    }
    return {
        _SYNTHESIS_SYNONYMS.get(
            _TOKEN_SYNONYMS.get(token, token),
            _TOKEN_SYNONYMS.get(token, token),
        )
        for token in tokens
    }


def _factual_anchors(risk_statement: str) -> set[str]:
    """Return explicit identifiers, versions, and numerical limit expressions.

    These are intentionally narrow: they are checkable facts, rather than a
    semantic inference from the risk statement.
    """
    import re

    identifier_anchors = [
        *re.findall(r"\b[A-Za-z][A-Za-z0-9]*-\d+(?:[.,]\d+)?", risk_statement),
        *re.findall(r"\b[A-Z]{2,}-[A-Z]{2,}\b", risk_statement),
    ]
    numerical_anchors = re.findall(
        r"(?<![A-Za-z0-9])(?:v(?:ersion)?\.?\s*)?\d+(?:[.,]\d+)+(?:\s*%)?",
        risk_statement,
        flags=re.IGNORECASE,
    )
    return {anchor.strip() for anchor in [*identifier_anchors, *numerical_anchors]}


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
        for token in re.findall(r"[^\W_]+", value.lower(), flags=re.UNICODE)
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
    if citation_result.quote_matches_chunk and requirement_result.requirement_applicable:
        if (
            len(finding.evidence_items) >= 2
            and citation_result.multi_document_synthesis_valid
            and citation_result.multi_document_semantic_support
            and not missing_evidence
        ):
            return EvidenceSupport.STRONG
        if citation_result.claim_support == EvidenceSupport.NONE:
            return EvidenceSupport.NONE
        if not citation_result.multi_document_synthesis_valid:
            return EvidenceSupport.PARTIAL
        if citation_result.claim_support == EvidenceSupport.PARTIAL:
            return EvidenceSupport.PARTIAL
        if missing_evidence:
            return EvidenceSupport.PARTIAL
        return EvidenceSupport.STRONG
    if citation_result.claim_support == EvidenceSupport.NONE:
        return EvidenceSupport.NONE
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

_SYNTHESIS_STOPWORDS = {
    "aber",
    "alle",
    "als",
    "am",
    "an",
    "auch",
    "auf",
    "aus",
    "bei",
    "behandelt",
    "beziehungsweise",
    "dass",
    "das",
    "dem",
    "den",
    "der",
    "des",
    "die",
    "einem",
    "einen",
    "eine",
    "ein",
    "erste",
    "ersten",
    "für",
    "im",
    "in",
    "ist",
    "kein",
    "keine",
    "mit",
    "nicht",
    "noch",
    "nur",
    "obwohl",
    "oder",
    "sein",
    "sich",
    "sind",
    "und",
    "von",
    "vor",
    "werden",
    "wird",
    "wie",
    "zeigen",
    "zu",
    "zur",
}

_SYNTHESIS_SYNONYMS = {
    "abgedeckt": "coverage",
    "akzeptiert": "support",
    "aktuell": "equipment",
    "aktuelle": "equipment",
    "alten": "historical",
    "alte": "historical",
    "andere": "comparison",
    "anderen": "comparison",
    "anwendung": "release",
    "approval": "approval",
    "ausgeführt": "release",
    "ausreichend": "coverage",
    "auftaucht": "record",
    "batch": "batch",
    "bridging": "bridge",
    "chargen": "batch",
    "chargenfreigabe": "release",
    "change": "record",
    "comparison": "comparison",
    "comparator": "comparison",
    "coverage": "coverage",
    "deckt": "coverage",
    "decision": "decision",
    "dokumentiert": "documented",
    "dokumentierte": "documented",
    "documented": "documented",
    "entscheidung": "decision",
    "entwarnung": "support",
    "equipment": "equipment",
    "erforderlich": "required",
    "ergebnisreview": "review",
    "execution": "record",
    "freigabe": "approval",
    "freigaben": "approval",
    "freigabesignaturblock": "documented",
    "geräte": "equipment",
    "geräteäquivalenz": "bridge",
    "gerätebrücke": "bridge",
    "geplant": "pending",
    "geschult": "training",
    "grenzwert": "limit",
    "grenzwerts": "limit",
    "hplc": "equipment",
    "leer": "documented",
    "methode": "validation",
    "methodenfitness": "validation",
    "muss": "required",
    "müssen": "required",
    "nennt": "scope",
    "neue": "new",
    "neuem": "new",
    "neuen": "new",
    "original": "historical",
    "optional": "optional",
    "part": "coverage",
    "pending": "pending",
    "protokolls": "historical",
    "record": "record",
    "retest": "retest",
    "review": "review",
    "reduzierten": "limit",
    "routinegeräteplattform": "equipment",
    "routineplattform": "equipment",
    "rückstellmuster": "retest",
    "scope": "scope",
    "sheet": "limit",
    "standort": "site",
    "stützt": "support",
    "teil": "coverage",
    "training": "training",
    "transfer": "bridge",
    "uplc": "equipment",
    "ursprünglichen": "historical",
    "validation": "validation",
    "validated": "validation",
    "validierung": "validation",
    "validierungspaket": "validation",
    "vergleichslabordaten": "comparison",
    "verpflichtend": "required",
    "vorliegt": "documented",
    "änderung": "record",
}
