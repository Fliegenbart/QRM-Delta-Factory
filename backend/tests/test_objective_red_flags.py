from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

from app.audit.events import InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import Document, DocumentChunk, DocumentSet, RequirementSet
from app.services.objective_red_flags import ObjectiveRedFlagService


def test_objective_red_flags_detect_case01_hidden_errors_from_chunks() -> None:
    repository = InMemoryDocumentRepository()
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set())
    repository.add_document(
        document=_document("doc_case01_deviation", "deviation.md"),
        chunks=[_chunk("chunk_case01_deviation_p1", "doc_case01_deviation", DEVIATION_TEXT)],
    )
    repository.add_document(
        document=_document("doc_case01_batch", "batch.md"),
        chunks=[_chunk("chunk_case01_batch_p1", "doc_case01_batch", BATCH_TEXT)],
    )
    service = ObjectiveRedFlagService(repository=repository, audit_log=InMemoryAuditLog())

    findings = service.run_objective_red_flag_scan("ds_case01")

    statements = " ".join(finding.risk_statement for finding in findings).lower()
    assert "signaturdatum" in statements
    assert "zukunft" in statements
    assert "fehlklassifizierung" in statements
    assert "minor" in statements
    assert {finding.severity for finding in findings} >= {"medium", "high"}
    assert any(
        "Digitale Signatur am 14.12.2026" in item.quote
        for finding in findings
        for item in finding.evidence_items
    )
    assert any(
        "Die Abweichung wird als Minor eingestuft" in item.quote
        for finding in findings
        for item in finding.evidence_items
    )
    assert repository.list_risk_fusion_findings("ds_case01") == findings


DEVIATION_TEXT = (
    "Abweichungsbericht DEV-2026-891\n"
    "Datum der Erfassung: 12.03.2026.\n"
    "Die Abweichung wird als Minor eingestuft, da die Salbe visuell homogen blieb. "
    "Ein Einfluss auf die Produktqualitaet wird ausgeschlossen.\n"
    "Geprueft durch: Dr. Anna Klar (Qualitaetssicherung) - Digitale Signatur am 14.12.2026."
)

BATCH_TEXT = (
    "Die Manteltemperatur sank fuer einen Zeitraum von 45 Minuten auf 34,2°C ab. "
    "Die spezifizierte Solltemperatur laut Herstellanweisung betraegt 40°C bis 45°C. "
    "Viskositaet: 2400 mPa·s, 2850 mPa·s, 2900 mPa·s, 2910 mPa·s."
)


def _document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_case01",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_case01",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="deviation",
        declared_process_area="formulation_mixing",
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_case01",
        tenant_id="tenant_demo_pharma",
        name="Case 01 Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_data_integrity_signature",
                "source_type": "internal_sop",
                "source_name": "SOP-DI-001",
                "source_version": "1.0",
                "section": "6",
                "requirement_text": (
                    "Electronic signatures and dates must be accurate and contemporaneous."
                ),
                "applies_to_document_types": ["deviation"],
                "applies_to_process_areas": ["formulation_mixing"],
                "criticality": "high",
                "required_evidence": ["signature timestamp", "audit trail"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_deviation_classification",
                "source_type": "internal_sop",
                "source_name": "SOP-DEV-001",
                "source_version": "1.0",
                "section": "7",
                "requirement_text": (
                    "Deviation classification must reflect process parameter excursions "
                    "and product quality impact."
                ),
                "applies_to_document_types": ["deviation"],
                "applies_to_process_areas": ["formulation_mixing"],
                "criticality": "high",
                "required_evidence": ["process parameter excursion", "impact assessment"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
        ],
    )


def _document(document_id: str, filename: str) -> Document:
    return Document(
        document_id=document_id,
        document_set_id="ds_case01",
        filename=filename,
        file_hash_sha256=sha256(filename.encode()).hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri=f"local://case01/{filename}",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=0.95,
        language="de",
        metadata={},
    )


def _chunk(chunk_id: str, document_id: str, text: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )
