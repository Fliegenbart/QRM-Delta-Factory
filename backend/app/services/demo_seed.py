from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256

from app.audit.events import InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.demo import DemoSeedResponse
from app.schemas.domain import (
    Criticality,
    Document,
    DocumentChunk,
    DocumentSet,
    DocumentSetStatus,
    ParsingStatus,
    Requirement,
    RequirementSet,
    RequirementSourceType,
)
from app.services.pipeline import PipelineService
from app.services.review_pack import ReviewPackService

DEMO_DOCUMENT_SET_ID = "ds_demo_avi_threshold"
DEMO_REQUIREMENT_SET_ID = "rset_demo_avi_threshold_2026"
DEMO_DOCUMENT_ID = "doc_demo_avi_change_control"


class DemoSeedTenantMismatchError(Exception):
    pass


@dataclass(frozen=True)
class DemoSeedService:
    repository: InMemoryDocumentRepository
    audit_log: InMemoryAuditLog

    def seed(self, *, tenant_id: str = "tenant_demo_pharma") -> DemoSeedResponse:
        created = self._ensure_demo_dataset(tenant_id=tenant_id)
        pipeline_run = PipelineService(
            repository=self.repository,
            audit_log=self.audit_log,
        ).run_pipeline(DEMO_DOCUMENT_SET_ID)
        review_pack = ReviewPackService(
            repository=self.repository,
            audit_log=self.audit_log,
        ).get_review_pack(DEMO_DOCUMENT_SET_ID)
        document_set = self.repository.get_document_set(DEMO_DOCUMENT_SET_ID)
        if document_set is None:
            raise RuntimeError("Demo DocumentSet was not created")
        return DemoSeedResponse(
            created=created,
            document_set=document_set,
            pipeline_run=pipeline_run,
            review_pack=review_pack,
        )

    def _ensure_demo_dataset(self, *, tenant_id: str) -> bool:
        existing = self.repository.get_document_set(DEMO_DOCUMENT_SET_ID)
        if existing is not None:
            if existing.tenant_id != tenant_id:
                raise DemoSeedTenantMismatchError(
                    "Demo dataset already exists for a different tenant"
                )
            return False

        requirement_set = _demo_requirement_set(tenant_id=tenant_id)
        self.repository.create_requirement_set(requirement_set)
        document_set = _demo_document_set(tenant_id=tenant_id)
        self.repository.create_document_set(document_set)
        self.repository.add_document(
            document=_demo_document(),
            chunks=_demo_chunks(),
        )
        self.audit_log.append(
            event_type="demo_dataset_seeded",
            actor_id="service_demo_seed",
            actor_type="service",
            entity_type="DocumentSet",
            entity_id=DEMO_DOCUMENT_SET_ID,
            tenant_id=tenant_id,
            payload={
                "document_set_id": DEMO_DOCUMENT_SET_ID,
                "requirement_set_id": DEMO_REQUIREMENT_SET_ID,
                "document_ids": [DEMO_DOCUMENT_ID],
                "synthetic": True,
            },
        )
        return True


def _demo_document_set(*, tenant_id: str) -> DocumentSet:
    return DocumentSet(
        document_set_id=DEMO_DOCUMENT_SET_ID,
        tenant_id=tenant_id,
        requirement_set_id=DEMO_REQUIREMENT_SET_ID,
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="change_control",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status=DocumentSetStatus.READY_FOR_ORCHESTRATION,
    )


def _demo_document() -> Document:
    full_text = "\n\n".join(chunk.text for chunk in _demo_chunks())
    return Document(
        document_id=DEMO_DOCUMENT_ID,
        document_set_id=DEMO_DOCUMENT_SET_ID,
        filename="synthetic-cc-2026-014-avi-threshold-change.txt",
        file_hash_sha256=sha256(full_text.encode()).hexdigest(),
        mime_type="text/plain",
        page_count=3,
        storage_uri="local://demo/synthetic-cc-2026-014-avi-threshold-change.txt",
        parser_version="demo-seed-parser-v1",
        parsing_status=ParsingStatus.PARSED,
        parsing_quality_score=0.93,
        language="en",
        metadata={
            "synthetic": True,
            "document_type": "change_control",
            "process_area": "aseptic_filling",
            "missing_required_documents": [
                "training record for revised AVI SOP",
                "validation addendum for new rejection threshold",
            ],
        },
    )


def _demo_chunks() -> list[DocumentChunk]:
    texts = [
        (
            "Change control CC-2026-014 modifies the automated visual inspection "
            "rejection threshold on aseptic filling Line 2 for sterile injectable "
            "drug product. DEV-2026-014 documents historical false accept concerns "
            "for cracked or particulate-defective containers. Batch AVI-2026-001 is "
            "listed as the first batch potentially exposed to the revised threshold. "
            "Impact assessment: the threshold change may affect false accept of "
            "defective containers, particulate contamination detection, and container "
            "closure defect detection. Root cause: inspection threshold sensitivity "
            "was adjusted during recipe optimization."
        ),
        (
            "SOP-AVI-012 revision 7 describes operator verification of automated "
            "visual inspection alarms, audit trail review, and batch record "
            "reconciliation after inspection. QA approval: pending until validation "
            "addendum and training completion are documented. CAPA-2026-014 assigns "
            "validation and operations to verify the revised threshold before routine "
            "release. Effectiveness check is not documented for the new threshold. "
            "Training record is not available for operators using SOP-AVI-012 revision 7."
        ),
        (
            "Validation report VR-AVI-2025-008 covers the previous automated visual "
            "inspection rejection threshold only. Test result: old-threshold challenge "
            "set met acceptance criteria for cracked vial detection and visible "
            "particulate rejection. Acceptance criterion: revised threshold must "
            "demonstrate no increased false accept rate for critical visual defects "
            "and no unexplained batch reconciliation discrepancy by 2026-04-30. "
            "Batch record reconciliation procedure is unclear for manual reinspection "
            "after threshold-related alarms."
        ),
    ]
    return [
        DocumentChunk(
            chunk_id=f"chunk_demo_avi_{index}",
            document_id=DEMO_DOCUMENT_ID,
            page_start=index,
            page_end=index,
            text=text,
            token_count=len(text.split()),
            extraction_confidence=0.95,
            bbox=None,
            source_hash=sha256(text.encode()).hexdigest(),
        )
        for index, text in enumerate(texts, start=1)
    ]


def _demo_requirement_set(*, tenant_id: str) -> RequirementSet:
    now = datetime.now(UTC)
    return RequirementSet(
        requirement_set_id=DEMO_REQUIREMENT_SET_ID,
        tenant_id=tenant_id,
        name="Synthetic AVI Threshold Change Requirements",
        version="2026.1-demo",
        imported_at=now,
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            _requirement(
                requirement_id="req_demo_change_impact",
                section="CC-1",
                requirement_text=(
                    "Change controls for aseptic inspection parameters must include "
                    "documented impact assessment for product quality, patient safety, "
                    "batch disposition, and process controls."
                ),
                criticality=Criticality.HIGH,
                required_evidence=[
                    "approved change impact assessment",
                    "batch impact assessment",
                    "QA disposition rationale",
                ],
            ),
            _requirement(
                requirement_id="req_demo_validation_addendum",
                section="VAL-1",
                requirement_text=(
                    "Modified automated inspection thresholds must be supported by "
                    "verification or validation evidence applicable to the changed "
                    "threshold."
                ),
                criticality=Criticality.HIGH,
                required_evidence=[
                    "validation addendum",
                    "challenge set results",
                    "threshold configuration record",
                ],
            ),
            _requirement(
                requirement_id="req_demo_training",
                section="TRN-1",
                requirement_text=(
                    "SOP changes affecting GMP execution must have documented "
                    "training completion before routine use."
                ),
                criticality=Criticality.MEDIUM,
                required_evidence=["training record", "effective SOP revision"],
            ),
            _requirement(
                requirement_id="req_demo_data_integrity",
                section="DI-1",
                requirement_text=(
                    "Automated inspection data, audit trail review, and batch record "
                    "reconciliation must remain attributable and reviewable."
                ),
                criticality=Criticality.HIGH,
                required_evidence=[
                    "audit trail review evidence",
                    "batch record reconciliation evidence",
                ],
            ),
            _requirement(
                requirement_id="req_demo_capa_effectiveness",
                section="CAPA-1",
                requirement_text=(
                    "CAPA linked to product quality risk must include documented "
                    "effectiveness evidence or a justified plan."
                ),
                criticality=Criticality.MEDIUM,
                required_evidence=["CAPA effectiveness check"],
            ),
        ],
    )


def _requirement(
    *,
    requirement_id: str,
    section: str,
    requirement_text: str,
    criticality: Criticality,
    required_evidence: list[str],
) -> Requirement:
    return Requirement(
        requirement_id=requirement_id,
        source_type=RequirementSourceType.INTERNAL_SOP,
        source_name="Synthetic QRM Demo Requirement Library",
        source_version="2026.1-demo",
        section=section,
        requirement_text=requirement_text,
        applies_to_document_types=["change_control"],
        applies_to_process_areas=["aseptic_filling"],
        criticality=criticality,
        required_evidence=required_evidence,
        auto_close_allowed=criticality not in {Criticality.HIGH, Criticality.CRITICAL},
        effective_from=datetime(2026, 1, 1, tzinfo=UTC),
        effective_to=None,
    )
