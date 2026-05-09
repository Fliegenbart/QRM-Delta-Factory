from __future__ import annotations

from collections.abc import Sequence

from app.audit.events import InMemoryAuditLog
from app.core.config import Settings, get_settings
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import (
    Claim,
    ClaimType,
    Criticality,
    Document,
    DocumentSet,
    Requirement,
    Severity,
)
from app.schemas.gates import CoverageGateResult, OODGateResult

BASE_REQUIRED_REVIEWER_ROLES = {
    "GMPDataIntegrityReviewer",
    "RegulatoryConsistencyReviewer",
    "ContradictionHunter",
}

DOCUMENT_TYPE_REVIEWER_ROLES: dict[str, set[str]] = {
    "deviation": {"DeviationReviewer", "BatchImpactReviewer"},
    "capa": {"CAPAReviewer"},
    "change_control": {"BatchImpactReviewer"},
    "batch_record": {"BatchImpactReviewer"},
    "batch_impact_assessment": {"BatchImpactReviewer"},
}

PROCESS_AREA_REVIEWER_ROLES: dict[str, set[str]] = {
    "aseptic_filling": {"BatchImpactReviewer"},
    "sterile_manufacturing": {"BatchImpactReviewer"},
    "data_integrity": {"GMPDataIntegrityReviewer"},
}


class OODDocumentSetNotFoundError(Exception):
    pass


class CoverageDocumentSetNotFoundError(Exception):
    pass


class OODService:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
        settings: Settings | None = None,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log
        self.settings = settings or get_settings()

    def evaluate(self, document_set_id: str) -> OODGateResult:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise OODDocumentSetNotFoundError(f"DocumentSet {document_set_id} not found")

        documents = _documents_for_set(self.repository, document_set)
        requirements = _requirements_for_set(self.repository, document_set)
        claims = self.repository.list_claims(document_set_id)
        required_roles = required_reviewer_roles_for_scope(
            document_type=document_set.declared_document_type,
            process_area=document_set.declared_process_area,
        )
        failed_roles = _failed_roles_for_document_set(
            audit_log=self.audit_log,
            document_set_id=document_set_id,
            required_roles=required_roles,
        )

        weighted_signals: list[tuple[str, str, float]] = []
        matching_requirements = _matching_requirements(document_set, requirements)
        if any(document.metadata.get("out_of_scope") is True for document in documents):
            weighted_signals.append(
                ("explicit_out_of_scope", "document metadata marks set as out of scope", 1.0)
            )
        if not _known_document_type(document_set, requirements):
            weighted_signals.append(
                (
                    "unknown_document_type",
                    f"unknown document type: {document_set.declared_document_type}",
                    0.25,
                )
            )
        if not _known_process_area(document_set, requirements):
            weighted_signals.append(
                (
                    "unknown_process_area",
                    f"unknown process area: {document_set.declared_process_area}",
                    0.25,
                )
            )
        unsupported_languages = _unsupported_languages(documents, self.settings)
        weighted_signals.extend(
            ("unsupported_language", f"unsupported language: {language}", 0.2)
            for language in unsupported_languages
        )
        if any(
            document.parsing_quality_score < self.settings.parsing_quality_threshold
            for document in documents
        ):
            weighted_signals.append(
                (
                    "low_parsing_quality",
                    "document parsing quality below threshold",
                    0.25,
                )
            )
        for missing_document in _missing_required_documents(documents):
            weighted_signals.append(
                (
                    "missing_required_document",
                    f"missing required document: {missing_document}",
                    0.25,
                )
            )
        if len(claims) < self.settings.minimum_claim_count:
            weighted_signals.append(
                ("unusually_few_claims", "unusually few claims", 0.15)
            )
        if _unclear_claim_ratio(claims) > self.settings.unclear_claim_ratio_threshold:
            weighted_signals.append(
                ("unclear_claim_ratio", "unusually many unclear claims", 0.2)
            )
        if not matching_requirements:
            weighted_signals.append(
                ("no_matching_requirements", "no matching requirements found", 1.0)
            )
        weighted_signals.extend(
            (
                "failed_relevant_reviewer_role",
                f"relevant reviewer role failed: {role}",
                0.25,
            )
            for role in failed_roles
        )

        score = min(sum(weight for _, _, weight in weighted_signals), 1.0)
        return OODGateResult(
            score=round(score, 3),
            threshold=self.settings.ood_score_threshold,
            signals=_dedupe_text([signal for signal, _, _ in weighted_signals]),
            reasons=_dedupe_text([reason for _, reason, _ in weighted_signals]),
            auto_clear_blocked=score >= self.settings.ood_score_threshold,
        )


class CoverageService:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log

    def evaluate(self, document_set_id: str) -> CoverageGateResult:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise CoverageDocumentSetNotFoundError(f"DocumentSet {document_set_id} not found")

        requirements = _requirements_for_set(self.repository, document_set)
        matching_requirements = _matching_requirements(document_set, requirements)
        required_roles = required_reviewer_roles_for_scope(
            document_type=document_set.declared_document_type,
            process_area=document_set.declared_process_area,
        )
        completed_roles = _completed_roles_for_document_set(
            repository=self.repository,
            audit_log=self.audit_log,
            document_set_id=document_set_id,
        )
        failed_roles = _failed_roles_for_document_set(
            audit_log=self.audit_log,
            document_set_id=document_set_id,
            required_roles=required_roles,
        )
        missing_roles = sorted(role for role in required_roles if role not in completed_roles)

        gap_reasons: list[str] = []
        for role in missing_roles:
            gap_reasons.append(f"missing required reviewer role: {role}")
        for role in failed_roles:
            gap_reasons.append(f"required reviewer role failed: {role}")
        if not matching_requirements:
            gap_reasons.append("no matching requirements found")

        findings = [
            *self.repository.list_risk_findings(document_set_id),
            *self.repository.list_risk_fusion_findings(document_set_id),
        ]
        for finding in findings:
            if not finding.requirement_references:
                gap_reasons.append(
                    f"finding lacks requirement reference: {finding.finding_id}"
                )

        high_or_critical_scope = any(
            requirement.criticality in {Criticality.HIGH, Criticality.CRITICAL}
            for requirement in matching_requirements
        )
        high_or_critical_finding_gap = any(
            finding.severity in {Severity.HIGH, Severity.CRITICAL}
            and not finding.requirement_references
            for finding in findings
        )
        high_or_critical_coverage_gap = bool(
            (high_or_critical_scope or high_or_critical_finding_gap) and gap_reasons
        )
        coverage_score = max(0.0, 1.0 - (0.2 * len(_dedupe_text(gap_reasons))))
        return CoverageGateResult(
            coverage_score=round(coverage_score, 3),
            required_roles=required_roles,
            completed_roles=completed_roles,
            missing_roles=missing_roles,
            failed_roles=failed_roles,
            requirement_coverage_sufficient=bool(matching_requirements),
            high_or_critical_coverage_gap=high_or_critical_coverage_gap,
            gap_reasons=_dedupe_text(gap_reasons),
        )


def required_reviewer_roles_for_scope(*, document_type: str, process_area: str) -> list[str]:
    roles = set(BASE_REQUIRED_REVIEWER_ROLES)
    roles.update(DOCUMENT_TYPE_REVIEWER_ROLES.get(document_type.lower(), set()))
    roles.update(PROCESS_AREA_REVIEWER_ROLES.get(process_area.lower(), set()))
    return sorted(roles)


def _documents_for_set(
    repository: InMemoryDocumentRepository,
    document_set: DocumentSet,
) -> list[Document]:
    documents: list[Document] = []
    for document_id in document_set.document_ids:
        document = repository.get_document(document_id)
        if document is not None:
            documents.append(document)
    return documents


def _requirements_for_set(
    repository: InMemoryDocumentRepository,
    document_set: DocumentSet,
) -> list[Requirement]:
    requirement_set = repository.get_requirement_set(document_set.requirement_set_id)
    if requirement_set is None:
        return []
    return requirement_set.requirements


def _matching_requirements(
    document_set: DocumentSet,
    requirements: Sequence[Requirement],
) -> list[Requirement]:
    return [
        requirement
        for requirement in requirements
        if document_set.declared_document_type in requirement.applies_to_document_types
        and document_set.declared_process_area in requirement.applies_to_process_areas
    ]


def _known_document_type(
    document_set: DocumentSet,
    requirements: Sequence[Requirement],
) -> bool:
    return any(
        document_set.declared_document_type in requirement.applies_to_document_types
        for requirement in requirements
    )


def _known_process_area(
    document_set: DocumentSet,
    requirements: Sequence[Requirement],
) -> bool:
    return any(
        document_set.declared_process_area in requirement.applies_to_process_areas
        for requirement in requirements
    )


def _unsupported_languages(documents: Sequence[Document], settings: Settings) -> list[str]:
    supported = {language.lower() for language in settings.supported_document_language_set()}
    if not supported:
        return []
    return _dedupe_text(
        [
            document.language
            for document in documents
            if document.language.lower() not in supported
        ]
    )


def _missing_required_documents(documents: Sequence[Document]) -> list[str]:
    missing: list[str] = []
    for document in documents:
        for key in ("missing_required_documents", "required_documents_missing"):
            value = document.metadata.get(key, [])
            if isinstance(value, list):
                missing.extend(str(item) for item in value)
            elif isinstance(value, str):
                missing.append(value)
    return _dedupe_text(missing)


def _unclear_claim_ratio(claims: Sequence[Claim]) -> float:
    if not claims:
        return 0.0
    unclear_count = sum(1 for claim in claims if claim.claim_type == ClaimType.MISSING_OR_UNCLEAR)
    return unclear_count / len(claims)


def _completed_roles_for_document_set(
    *,
    repository: InMemoryDocumentRepository,
    audit_log: InMemoryAuditLog,
    document_set_id: str,
) -> list[str]:
    roles = [summary.role for summary in repository.list_coverage_summaries(document_set_id)]
    for event in audit_log.list_events():
        if (
            event.event_type == "model_run_completed"
            and event.payload.get("document_set_id") == document_set_id
        ):
            role = event.payload.get("role")
            if isinstance(role, str):
                roles.append(role)
    return _dedupe_text(roles)


def _failed_roles_for_document_set(
    *,
    audit_log: InMemoryAuditLog,
    document_set_id: str,
    required_roles: Sequence[str],
) -> list[str]:
    failed_roles: list[str] = []
    required_role_set = set(required_roles)
    for event in audit_log.list_events():
        if (
            event.event_type in {"model_run_failed", "failed_model_run"}
            and event.payload.get("document_set_id") == document_set_id
        ):
            role = event.payload.get("role")
            if isinstance(role, str) and role in required_role_set:
                failed_roles.append(role)
    return _dedupe_text(failed_roles)


def _dedupe_text(items: Sequence[str]) -> list[str]:
    deduped: list[str] = []
    for item in items:
        if item and item not in deduped:
            deduped.append(item)
    return deduped
