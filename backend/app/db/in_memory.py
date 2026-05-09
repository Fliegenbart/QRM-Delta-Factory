from __future__ import annotations

from app.schemas.domain import (
    AdversarialChallenge,
    Claim,
    Criticality,
    Document,
    DocumentChunk,
    DocumentSet,
    FindingVerificationResult,
    ModelRun,
    RawModelOutputRecord,
    Requirement,
    RequirementSet,
    ReviewDecision,
    RiskFinding,
)
from app.schemas.pipeline import PipelineRun
from app.schemas.review import CoverageSummary
from app.schemas.risk import RiskDecision


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self.document_sets: dict[str, DocumentSet] = {}
        self.documents: dict[str, Document] = {}
        self.chunks_by_document: dict[str, list[DocumentChunk]] = {}
        self.claims_by_document_set: dict[str, list[Claim]] = {}
        self.risk_findings_by_document_set: dict[str, list[RiskFinding]] = {}
        self.risk_fusion_findings_by_document_set: dict[str, list[RiskFinding]] = {}
        self.adversarial_challenges_by_document_set: dict[str, list[AdversarialChallenge]] = {}
        self.coverage_summaries_by_document_set: dict[str, list[CoverageSummary]] = {}
        self.risk_decisions_by_document_set: dict[str, list[RiskDecision]] = {}
        self.pipeline_runs: dict[str, PipelineRun] = {}
        self.review_decisions_by_finding: dict[str, list[ReviewDecision]] = {}
        self.verification_results_by_document_set: dict[str, list[FindingVerificationResult]] = {}
        self.model_runs_by_document_set: dict[str, list[ModelRun]] = {}
        self.raw_model_outputs: dict[str, RawModelOutputRecord] = {}
        self.requirement_sets: dict[str, RequirementSet] = {}

    def reset(self) -> None:
        self.document_sets.clear()
        self.documents.clear()
        self.chunks_by_document.clear()
        self.claims_by_document_set.clear()
        self.risk_findings_by_document_set.clear()
        self.risk_fusion_findings_by_document_set.clear()
        self.adversarial_challenges_by_document_set.clear()
        self.coverage_summaries_by_document_set.clear()
        self.risk_decisions_by_document_set.clear()
        self.pipeline_runs.clear()
        self.review_decisions_by_finding.clear()
        self.verification_results_by_document_set.clear()
        self.model_runs_by_document_set.clear()
        self.raw_model_outputs.clear()
        self.requirement_sets.clear()

    def create_document_set(self, document_set: DocumentSet) -> DocumentSet:
        self.document_sets[document_set.document_set_id] = document_set
        return document_set

    def get_document_set(self, document_set_id: str) -> DocumentSet | None:
        return self.document_sets.get(document_set_id)

    def list_document_sets(self, *, tenant_id: str | None = None) -> list[DocumentSet]:
        document_sets = list(self.document_sets.values())
        if tenant_id is not None:
            document_sets = [
                document_set
                for document_set in document_sets
                if document_set.tenant_id == tenant_id
            ]
        return sorted(document_sets, key=lambda item: item.upload_timestamp, reverse=True)

    def update_document_set(self, document_set: DocumentSet) -> DocumentSet:
        self.document_sets[document_set.document_set_id] = document_set
        return document_set

    def add_document(
        self,
        *,
        document: Document,
        chunks: list[DocumentChunk],
    ) -> Document:
        self.documents[document.document_id] = document
        self.chunks_by_document[document.document_id] = chunks
        document_set = self.document_sets[document.document_set_id]
        if document.document_id not in document_set.document_ids:
            self.document_sets[document.document_set_id] = document_set.model_copy(
                update={"document_ids": [*document_set.document_ids, document.document_id]}
            )
        return document

    def list_chunks(self, document_id: str) -> list[DocumentChunk]:
        return list(self.chunks_by_document.get(document_id, []))

    def get_document(self, document_id: str) -> Document | None:
        return self.documents.get(document_id)

    def get_chunk(self, *, document_id: str, chunk_id: str) -> DocumentChunk | None:
        return next(
            (
                chunk
                for chunk in self.chunks_by_document.get(document_id, [])
                if chunk.chunk_id == chunk_id
            ),
            None,
        )

    def list_chunks_for_document_set(self, document_set_id: str) -> list[DocumentChunk]:
        document_set = self.document_sets.get(document_set_id)
        if document_set is None:
            return []
        chunks: list[DocumentChunk] = []
        for document_id in document_set.document_ids:
            chunks.extend(self.list_chunks(document_id))
        return chunks

    def replace_claim_ledger(self, *, document_set_id: str, claims: list[Claim]) -> list[Claim]:
        self.claims_by_document_set[document_set_id] = claims
        return claims

    def list_claims(self, document_set_id: str) -> list[Claim]:
        return list(self.claims_by_document_set.get(document_set_id, []))

    def replace_risk_findings(
        self,
        *,
        document_set_id: str,
        findings: list[RiskFinding],
    ) -> list[RiskFinding]:
        self.risk_findings_by_document_set[document_set_id] = findings
        return findings

    def list_risk_findings(self, document_set_id: str) -> list[RiskFinding]:
        return list(self.risk_findings_by_document_set.get(document_set_id, []))

    def replace_risk_fusion_findings(
        self,
        *,
        document_set_id: str,
        findings: list[RiskFinding],
    ) -> list[RiskFinding]:
        deduplicated: dict[str, RiskFinding] = {}
        for finding in findings:
            deduplicated[finding.finding_id] = finding
        self.risk_fusion_findings_by_document_set[document_set_id] = list(
            deduplicated.values()
        )
        return self.risk_fusion_findings_by_document_set[document_set_id]

    def list_risk_fusion_findings(self, document_set_id: str) -> list[RiskFinding]:
        return list(self.risk_fusion_findings_by_document_set.get(document_set_id, []))

    def append_adversarial_challenges(
        self,
        *,
        document_set_id: str,
        challenges: list[AdversarialChallenge],
    ) -> list[AdversarialChallenge]:
        existing = self.adversarial_challenges_by_document_set.setdefault(
            document_set_id,
            [],
        )
        existing_by_id = {challenge.challenge_id: challenge for challenge in existing}
        for challenge in challenges:
            existing_by_id[challenge.challenge_id] = challenge
        self.adversarial_challenges_by_document_set[document_set_id] = list(
            existing_by_id.values()
        )
        return list(self.adversarial_challenges_by_document_set[document_set_id])

    def list_adversarial_challenges(
        self,
        document_set_id: str,
    ) -> list[AdversarialChallenge]:
        return list(self.adversarial_challenges_by_document_set.get(document_set_id, []))

    def replace_coverage_summaries(
        self,
        *,
        document_set_id: str,
        coverage_summaries: list[CoverageSummary],
    ) -> list[CoverageSummary]:
        self.coverage_summaries_by_document_set[document_set_id] = coverage_summaries
        return coverage_summaries

    def list_coverage_summaries(self, document_set_id: str) -> list[CoverageSummary]:
        return list(self.coverage_summaries_by_document_set.get(document_set_id, []))

    def add_risk_decision(
        self,
        *,
        document_set_id: str,
        risk_decision: RiskDecision,
    ) -> RiskDecision:
        self.risk_decisions_by_document_set.setdefault(document_set_id, []).append(
            risk_decision
        )
        return risk_decision

    def get_latest_risk_decision(self, document_set_id: str) -> RiskDecision | None:
        decisions = self.risk_decisions_by_document_set.get(document_set_id, [])
        return decisions[-1] if decisions else None

    def add_pipeline_run(self, pipeline_run: PipelineRun) -> PipelineRun:
        self.pipeline_runs[pipeline_run.pipeline_run_id] = pipeline_run
        return pipeline_run

    def update_pipeline_run(self, pipeline_run: PipelineRun) -> PipelineRun:
        self.pipeline_runs[pipeline_run.pipeline_run_id] = pipeline_run
        return pipeline_run

    def get_pipeline_run(self, pipeline_run_id: str) -> PipelineRun | None:
        return self.pipeline_runs.get(pipeline_run_id)

    def add_review_decision(self, review_decision: ReviewDecision) -> ReviewDecision:
        self.review_decisions_by_finding.setdefault(
            review_decision.finding_id,
            [],
        ).append(review_decision)
        return review_decision

    def list_review_decisions(self, finding_id: str) -> list[ReviewDecision]:
        return list(self.review_decisions_by_finding.get(finding_id, []))

    def list_review_decisions_all(self) -> list[ReviewDecision]:
        decisions: list[ReviewDecision] = []
        for finding_decisions in self.review_decisions_by_finding.values():
            decisions.extend(finding_decisions)
        return sorted(decisions, key=lambda decision: decision.created_at)

    def find_risk_finding(self, finding_id: str) -> RiskFinding | None:
        for findings in [
            *self.risk_findings_by_document_set.values(),
            *self.risk_fusion_findings_by_document_set.values(),
        ]:
            for finding in findings:
                if finding.finding_id == finding_id:
                    return finding
        return None

    def replace_verification_results(
        self,
        *,
        document_set_id: str,
        results: list[FindingVerificationResult],
    ) -> list[FindingVerificationResult]:
        self.verification_results_by_document_set[document_set_id] = results
        return results

    def list_verification_results(self, document_set_id: str) -> list[FindingVerificationResult]:
        return list(self.verification_results_by_document_set.get(document_set_id, []))

    def add_model_run(self, *, document_set_id: str, model_run: ModelRun) -> ModelRun:
        self.model_runs_by_document_set.setdefault(document_set_id, []).append(model_run)
        return model_run

    def list_model_runs(self, document_set_id: str) -> list[ModelRun]:
        return list(self.model_runs_by_document_set.get(document_set_id, []))

    def store_raw_model_output(self, record: RawModelOutputRecord) -> RawModelOutputRecord:
        self.raw_model_outputs[record.output_hash] = record
        return record

    def list_raw_model_outputs(self) -> list[RawModelOutputRecord]:
        return list(self.raw_model_outputs.values())

    def create_requirement_set(self, requirement_set: RequirementSet) -> RequirementSet:
        self.requirement_sets[requirement_set.requirement_set_id] = requirement_set
        return requirement_set

    def get_requirement_set(self, requirement_set_id: str) -> RequirementSet | None:
        return self.requirement_sets.get(requirement_set_id)

    def update_requirement_set(self, requirement_set: RequirementSet) -> RequirementSet:
        self.requirement_sets[requirement_set.requirement_set_id] = requirement_set
        return requirement_set

    def is_active_requirement_set(self, requirement_set_id: str) -> bool:
        requirement_set = self.get_requirement_set(requirement_set_id)
        return requirement_set is not None and requirement_set.active

    def search_requirements(
        self,
        *,
        tenant_id: str | None = None,
        document_type: str | None = None,
        process_area: str | None = None,
        criticality: Criticality | None = None,
    ) -> list[Requirement]:
        matches: list[Requirement] = []
        for requirement_set in self.requirement_sets.values():
            if not requirement_set.active:
                continue
            if tenant_id is not None and requirement_set.tenant_id != tenant_id:
                continue
            matches.extend(
                requirement
                for requirement in requirement_set.requirements
                if _requirement_matches(
                    requirement=requirement,
                    document_type=document_type,
                    process_area=process_area,
                    criticality=criticality,
                )
            )
        return matches


def _requirement_matches(
    *,
    requirement: Requirement,
    document_type: str | None,
    process_area: str | None,
    criticality: Criticality | None,
) -> bool:
    if document_type and document_type not in requirement.applies_to_document_types:
        return False
    if process_area and process_area not in requirement.applies_to_process_areas:
        return False
    return not (criticality and criticality != requirement.criticality)


repository = InMemoryDocumentRepository()
