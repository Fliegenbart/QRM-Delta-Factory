from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from threading import RLock
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import get_settings
from app.schemas.calibration import CalibrationExample, CalibrationExampleStatus
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

OperationT = TypeVar("OperationT")

LEGACY_DEMO_DOCUMENT_SET_IDS = {"ds_demo_avi_threshold"}


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
        self.calibration_examples: dict[str, CalibrationExample] = {}

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
        self.calibration_examples.clear()

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

    def delete_document_set(self, document_set_id: str) -> bool:
        document_set = self.document_sets.pop(document_set_id, None)
        if document_set is None:
            return False

        for document_id in document_set.document_ids:
            self.documents.pop(document_id, None)
            self.chunks_by_document.pop(document_id, None)

        finding_ids = {
            finding.finding_id
            for finding in [
                *self.risk_findings_by_document_set.get(document_set_id, []),
                *self.risk_fusion_findings_by_document_set.get(document_set_id, []),
            ]
        }
        for finding_id in finding_ids:
            self.review_decisions_by_finding.pop(finding_id, None)

        model_run_ids = {
            model_run.model_run_id
            for model_run in self.model_runs_by_document_set.get(document_set_id, [])
        }
        self.raw_model_outputs = {
            output_hash: output
            for output_hash, output in self.raw_model_outputs.items()
            if output.model_run_id not in model_run_ids
        }
        self.calibration_examples = {
            example_id: example
            for example_id, example in self.calibration_examples.items()
            if example.document_set_id != document_set_id
        }

        self.claims_by_document_set.pop(document_set_id, None)
        self.risk_findings_by_document_set.pop(document_set_id, None)
        self.risk_fusion_findings_by_document_set.pop(document_set_id, None)
        self.adversarial_challenges_by_document_set.pop(document_set_id, None)
        self.coverage_summaries_by_document_set.pop(document_set_id, None)
        self.risk_decisions_by_document_set.pop(document_set_id, None)
        self.verification_results_by_document_set.pop(document_set_id, None)
        self.model_runs_by_document_set.pop(document_set_id, None)
        self.pipeline_runs = {
            pipeline_run_id: pipeline_run
            for pipeline_run_id, pipeline_run in self.pipeline_runs.items()
            if pipeline_run.document_set_id != document_set_id
        }
        return True

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

    def add_calibration_example(
        self,
        calibration_example: CalibrationExample,
    ) -> CalibrationExample:
        self.calibration_examples[
            calibration_example.calibration_example_id
        ] = calibration_example
        return calibration_example

    def update_calibration_example(
        self,
        calibration_example: CalibrationExample,
    ) -> CalibrationExample:
        self.calibration_examples[
            calibration_example.calibration_example_id
        ] = calibration_example
        return calibration_example

    def get_calibration_example(
        self,
        calibration_example_id: str,
    ) -> CalibrationExample | None:
        return self.calibration_examples.get(calibration_example_id)

    def list_calibration_examples(
        self,
        *,
        tenant_id: str | None = None,
        status: CalibrationExampleStatus | None = None,
        agent_role: str | None = None,
    ) -> list[CalibrationExample]:
        examples = list(self.calibration_examples.values())
        if tenant_id is not None:
            examples = [example for example in examples if example.tenant_id == tenant_id]
        if status is not None:
            examples = [example for example in examples if example.status == status]
        if agent_role is not None:
            examples = [example for example in examples if example.agent_role == agent_role]
        return sorted(examples, key=lambda example: example.created_at, reverse=True)

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


class PersistentSnapshotRepository(InMemoryDocumentRepository):
    """Small durable repository for MVP deployments.

    The current backend mostly works with Pydantic domain objects. To avoid a large ORM
    migration before the product flow is proven, this repository stores a validated JSON
    snapshot in SQL. It is intentionally conservative and can later be replaced by table-
    per-entity SQLAlchemy models without changing service boundaries.
    """

    def __init__(self, *, database_url: str) -> None:
        normalized_database_url = _normalize_database_url(database_url)
        self._engine: Engine = create_engine(
            normalized_database_url,
            future=True,
            **_engine_options_for_database_url(normalized_database_url),
        )
        self._is_loading = False
        self._lock = RLock()
        super().__init__()
        self._create_table()
        self._load_snapshot()

    def reset(self) -> None:
        with self._lock:
            super().reset()
            if hasattr(self, "_engine"):
                self._save_snapshot()

    def create_document_set(self, document_set: DocumentSet) -> DocumentSet:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).create_document_set(document_set)
        )

    def update_document_set(self, document_set: DocumentSet) -> DocumentSet:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).update_document_set(document_set)
        )

    def delete_document_set(self, document_set_id: str) -> bool:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).delete_document_set(document_set_id)
        )

    def add_document(
        self,
        *,
        document: Document,
        chunks: list[DocumentChunk],
    ) -> Document:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).add_document(
                document=document,
                chunks=chunks,
            )
        )

    def replace_claim_ledger(self, *, document_set_id: str, claims: list[Claim]) -> list[Claim]:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).replace_claim_ledger(
                document_set_id=document_set_id,
                claims=claims,
            )
        )

    def replace_risk_findings(
        self,
        *,
        document_set_id: str,
        findings: list[RiskFinding],
    ) -> list[RiskFinding]:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).replace_risk_findings(
                document_set_id=document_set_id,
                findings=findings,
            )
        )

    def replace_risk_fusion_findings(
        self,
        *,
        document_set_id: str,
        findings: list[RiskFinding],
    ) -> list[RiskFinding]:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).replace_risk_fusion_findings(
                document_set_id=document_set_id,
                findings=findings,
            )
        )

    def append_adversarial_challenges(
        self,
        *,
        document_set_id: str,
        challenges: list[AdversarialChallenge],
    ) -> list[AdversarialChallenge]:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).append_adversarial_challenges(
                document_set_id=document_set_id,
                challenges=challenges,
            )
        )

    def replace_coverage_summaries(
        self,
        *,
        document_set_id: str,
        coverage_summaries: list[CoverageSummary],
    ) -> list[CoverageSummary]:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).replace_coverage_summaries(
                document_set_id=document_set_id,
                coverage_summaries=coverage_summaries,
            )
        )

    def add_risk_decision(
        self,
        *,
        document_set_id: str,
        risk_decision: RiskDecision,
    ) -> RiskDecision:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).add_risk_decision(
                document_set_id=document_set_id,
                risk_decision=risk_decision,
            )
        )

    def add_pipeline_run(self, pipeline_run: PipelineRun) -> PipelineRun:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).add_pipeline_run(pipeline_run)
        )

    def update_pipeline_run(self, pipeline_run: PipelineRun) -> PipelineRun:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).update_pipeline_run(pipeline_run)
        )

    def add_review_decision(self, review_decision: ReviewDecision) -> ReviewDecision:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).add_review_decision(review_decision)
        )

    def replace_verification_results(
        self,
        *,
        document_set_id: str,
        results: list[FindingVerificationResult],
    ) -> list[FindingVerificationResult]:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).replace_verification_results(
                document_set_id=document_set_id,
                results=results,
            )
        )

    def add_model_run(self, *, document_set_id: str, model_run: ModelRun) -> ModelRun:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).add_model_run(
                document_set_id=document_set_id,
                model_run=model_run,
            )
        )

    def store_raw_model_output(self, record: RawModelOutputRecord) -> RawModelOutputRecord:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).store_raw_model_output(record)
        )

    def create_requirement_set(self, requirement_set: RequirementSet) -> RequirementSet:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).create_requirement_set(
                requirement_set
            )
        )

    def update_requirement_set(self, requirement_set: RequirementSet) -> RequirementSet:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).update_requirement_set(
                requirement_set
            )
        )

    def add_calibration_example(
        self,
        calibration_example: CalibrationExample,
    ) -> CalibrationExample:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).add_calibration_example(
                calibration_example
            )
        )

    def update_calibration_example(
        self,
        calibration_example: CalibrationExample,
    ) -> CalibrationExample:
        return self._persist_after(
            lambda: super(PersistentSnapshotRepository, self).update_calibration_example(
                calibration_example
            )
        )

    def _persist_after(self, operation: Callable[[], OperationT]) -> OperationT:
        with self._lock:
            result = operation()
            if not self._is_loading:
                self._save_snapshot()
            return result

    def _create_table(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS qrm_repository_snapshots (
                        snapshot_id VARCHAR(64) PRIMARY KEY,
                        payload TEXT NOT NULL,
                        updated_at VARCHAR(64) NOT NULL
                    )
                    """
                )
            )

    def _load_snapshot(self) -> None:
        with self._engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT payload FROM qrm_repository_snapshots
                    WHERE snapshot_id = :snapshot_id
                    """
                ),
                {"snapshot_id": "default"},
            ).first()
        if row is None:
            return

        payload = json.loads(str(row.payload))
        self._is_loading = True
        try:
            self.document_sets = _model_dict(payload, "document_sets", DocumentSet)
            self.documents = _model_dict(payload, "documents", Document)
            self.chunks_by_document = _model_list_dict(
                payload,
                "chunks_by_document",
                DocumentChunk,
            )
            self.claims_by_document_set = _model_list_dict(
                payload,
                "claims_by_document_set",
                Claim,
            )
            self.risk_findings_by_document_set = _model_list_dict(
                payload,
                "risk_findings_by_document_set",
                RiskFinding,
            )
            self.risk_fusion_findings_by_document_set = _model_list_dict(
                payload,
                "risk_fusion_findings_by_document_set",
                RiskFinding,
            )
            self.adversarial_challenges_by_document_set = _model_list_dict(
                payload,
                "adversarial_challenges_by_document_set",
                AdversarialChallenge,
            )
            self.coverage_summaries_by_document_set = _model_list_dict(
                payload,
                "coverage_summaries_by_document_set",
                CoverageSummary,
            )
            self.risk_decisions_by_document_set = _model_list_dict(
                payload,
                "risk_decisions_by_document_set",
                RiskDecision,
            )
            self.pipeline_runs = _model_dict(payload, "pipeline_runs", PipelineRun)
            self.review_decisions_by_finding = _model_list_dict(
                payload,
                "review_decisions_by_finding",
                ReviewDecision,
            )
            self.verification_results_by_document_set = _model_list_dict(
                payload,
                "verification_results_by_document_set",
                FindingVerificationResult,
            )
            self.model_runs_by_document_set = _model_list_dict(
                payload,
                "model_runs_by_document_set",
                ModelRun,
            )
            self.raw_model_outputs = _model_dict(
                payload,
                "raw_model_outputs",
                RawModelOutputRecord,
            )
            self.requirement_sets = _model_dict(payload, "requirement_sets", RequirementSet)
            self.calibration_examples = _model_dict(
                payload,
                "calibration_examples",
                CalibrationExample,
            )
        finally:
            self._is_loading = False

        for document_set_id in LEGACY_DEMO_DOCUMENT_SET_IDS:
            self.delete_document_set(document_set_id)

    def _save_snapshot(self) -> None:
        with self._lock:
            payload = json.dumps(self._snapshot(), sort_keys=True)
            updated_at = datetime.now(UTC).isoformat()
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO qrm_repository_snapshots
                    (snapshot_id, payload, updated_at)
                    VALUES (:snapshot_id, :payload, :updated_at)
                    ON CONFLICT (snapshot_id) DO UPDATE SET
                        payload = EXCLUDED.payload,
                        updated_at = EXCLUDED.updated_at
                    """
                ),
                {
                    "snapshot_id": "default",
                    "payload": payload,
                    "updated_at": updated_at,
                },
            )

    def _snapshot(self) -> dict[str, object]:
        return {
            "document_sets": _dump_model_dict(self.document_sets),
            "documents": _dump_model_dict(self.documents),
            "chunks_by_document": _dump_model_list_dict(self.chunks_by_document),
            "claims_by_document_set": _dump_model_list_dict(self.claims_by_document_set),
            "risk_findings_by_document_set": _dump_model_list_dict(
                self.risk_findings_by_document_set
            ),
            "risk_fusion_findings_by_document_set": _dump_model_list_dict(
                self.risk_fusion_findings_by_document_set
            ),
            "adversarial_challenges_by_document_set": _dump_model_list_dict(
                self.adversarial_challenges_by_document_set
            ),
            "coverage_summaries_by_document_set": _dump_model_list_dict(
                self.coverage_summaries_by_document_set
            ),
            "risk_decisions_by_document_set": _dump_model_list_dict(
                self.risk_decisions_by_document_set
            ),
            "pipeline_runs": _dump_model_dict(self.pipeline_runs),
            "review_decisions_by_finding": _dump_model_list_dict(
                self.review_decisions_by_finding
            ),
            "verification_results_by_document_set": _dump_model_list_dict(
                self.verification_results_by_document_set
            ),
            "model_runs_by_document_set": _dump_model_list_dict(self.model_runs_by_document_set),
            "raw_model_outputs": _dump_model_dict(self.raw_model_outputs),
            "requirement_sets": _dump_model_dict(self.requirement_sets),
            "calibration_examples": _dump_model_dict(self.calibration_examples),
        }


def _dump_model_dict[ModelT: BaseModel](items: Mapping[str, ModelT]) -> dict[str, object]:
    return {key: item.model_dump(mode="json") for key, item in items.items()}


def _dump_model_list_dict[ModelT: BaseModel](
    items: Mapping[str, Sequence[ModelT]],
) -> dict[str, list[object]]:
    return {
        key: [item.model_dump(mode="json") for item in values]
        for key, values in items.items()
    }


def _model_dict[ModelT: BaseModel](
    payload: dict[str, object],
    key: str,
    model: type[ModelT],
) -> dict[str, ModelT]:
    data = payload.get(key, {})
    if not isinstance(data, dict):
        return {}
    return {item_key: model.model_validate(value) for item_key, value in data.items()}


def _model_list_dict[ModelT: BaseModel](
    payload: dict[str, object],
    key: str,
    model: type[ModelT],
) -> dict[str, list[ModelT]]:
    data = payload.get(key, {})
    if not isinstance(data, dict):
        return {}
    return {
        item_key: [model.model_validate(value) for value in values]
        for item_key, values in data.items()
        if isinstance(values, list)
    }


def _normalize_database_url(database_url: str) -> str:
    """Use the psycopg SQLAlchemy driver when Supabase provides a plain URL."""

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def _engine_options_for_database_url(database_url: str) -> dict[str, object]:
    normalized_database_url = _normalize_database_url(database_url)
    if normalized_database_url.startswith("postgresql+psycopg://"):
        return {
            "connect_args": {"prepare_threshold": None},
            "pool_pre_ping": True,
        }
    return {}


def _build_repository() -> InMemoryDocumentRepository:
    settings = get_settings()
    if settings.persistence_enabled:
        return PersistentSnapshotRepository(database_url=settings.database_url)
    return InMemoryDocumentRepository()


repository = _build_repository()
