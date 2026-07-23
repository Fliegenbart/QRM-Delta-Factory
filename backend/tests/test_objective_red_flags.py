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


def test_objective_red_flags_detect_yield_below_spec_marked_pass() -> None:
    repository = InMemoryDocumentRepository()
    repository.create_requirement_set(
        _requirement_set(
            requirement_set_id="rset_yield",
            name="Yield Requirements",
            process_area="batch_record_review",
            requirement_text=(
                "Batch records must identify out-of-specification yield results and "
                "must not classify them as pass without deviation and impact assessment."
            ),
            required_evidence=["yield range", "actual yield", "batch disposition"],
        )
    )
    repository.create_document_set(
        _document_set(
            document_set_id="ds_yield",
            requirement_set_id="rset_yield",
            declared_process_area="batch_record_review",
        )
    )
    repository.add_document(
        document=_document("doc_yield_batch", "yield-batch.md", document_set_id="ds_yield"),
        chunks=[_chunk("chunk_yield_batch_p1", "doc_yield_batch", YIELD_SPEC_TEXT)],
    )
    service = ObjectiveRedFlagService(repository=repository, audit_log=InMemoryAuditLog())

    findings = service.run_objective_red_flag_scan("ds_yield")

    statements = " ".join(finding.risk_statement for finding in findings).lower()
    assert "spezifikationsverletzung" in statements
    assert "ausbeute" in statements
    assert "pass" in statements
    assert any(finding.severity == "high" for finding in findings)
    assert any(
        "Reale Netto-Ausbeute" in item.quote
        for finding in findings
        for item in finding.evidence_items
    )
    assert any(
        'Status: "Pass"' in item.quote
        for finding in findings
        for item in finding.evidence_items
    )


def test_objective_red_flags_detect_water_content_outside_range_with_release() -> None:
    repository = InMemoryDocumentRepository()
    repository.create_requirement_set(
        _requirement_set(
            requirement_set_id="rset_water",
            name="Raw Material Requirements",
            process_area="incoming_material_release",
            requirement_text=(
                "Material release must compare measured analytical values against the "
                "internal specification and block release when a result is outside range."
            ),
            required_evidence=["analytical result", "internal specification", "release status"],
        )
    )
    repository.create_document_set(
        _document_set(
            document_set_id="ds_water",
            requirement_set_id="rset_water",
            declared_process_area="incoming_material_release",
        )
    )
    repository.add_document(
        document=_document("doc_water_lab", "water-lab.md", document_set_id="ds_water"),
        chunks=[_chunk("chunk_water_lab_p1", "doc_water_lab", WATER_SPEC_TEXT)],
    )
    service = ObjectiveRedFlagService(repository=repository, audit_log=InMemoryAuditLog())

    findings = service.run_objective_red_flag_scan("ds_water")

    statements = " ".join(finding.risk_statement for finding in findings).lower()
    assert "spezifikationsverletzung" in statements
    assert "wassergehalt" in statements
    assert "konform" in statements or "freigabe" in statements
    assert any(
        "Wassergehalt (Karl Fischer): 13,2%" in item.quote
        for finding in findings
        for item in finding.evidence_items
    )
    assert any(
        "Akzeptanzkriterium von 11.5% bis 12.8%" in item.quote
        for finding in findings
        for item in finding.evidence_items
    )


def test_objective_red_flags_detect_impurity_above_max_with_stability_continuation() -> None:
    repository = InMemoryDocumentRepository()
    repository.create_requirement_set(
        _requirement_set(
            requirement_set_id="rset_impurity",
            name="Stability Requirements",
            process_area="stability_testing",
            requirement_text=(
                "Stability studies must treat unknown impurity results above registered "
                "limits as OOS and may not continue unchanged while considering all "
                "analytical requirements fulfilled."
            ),
            required_evidence=["impurity limit", "measured impurity", "study disposition"],
        )
    )
    repository.create_document_set(
        _document_set(
            document_set_id="ds_impurity",
            requirement_set_id="rset_impurity",
            declared_process_area="stability_testing",
        )
    )
    repository.add_document(
        document=_document("doc_impurity", "impurity.md", document_set_id="ds_impurity"),
        chunks=[_chunk("chunk_impurity_p1", "doc_impurity", IMPURITY_SPEC_TEXT)],
    )
    service = ObjectiveRedFlagService(repository=repository, audit_log=InMemoryAuditLog())

    findings = service.run_objective_red_flag_scan("ds_impurity")

    statements = " ".join(finding.risk_statement for finding in findings).lower()
    assert "spezifikationsverletzung" in statements
    assert "verunreinigung" in statements
    assert "fortgesetzt" in statements or "erfuellt" in statements
    assert any(
        "Verunreinigung" in item.quote and "0,32%" in item.quote
        for finding in findings
        for item in finding.evidence_items
    )
    assert any(
        "maximal 0,20%" in item.quote
        for finding in findings
        for item in finding.evidence_items
    )


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

YIELD_SPEC_TEXT = (
    "Spezifizierter Toleranzbereich laut Validierung: 95.0% bis 102.0%.\n"
    "Reale Netto-Ausbeute laut Batch Record Review = 92,4%.\n"
    'Status: "Pass". Keine weitere Abweichung erforderlich.'
)

WATER_SPEC_TEXT = (
    "Wassergehalt (Karl Fischer): 13,2%.\n"
    "Internes Akzeptanzkriterium von 11.5% bis 12.8% Wassergehalt.\n"
    "Das Analysenzertifikat des Lieferanten belegt die Konformitaet; "
    "die Charge ist final autorisiert und frei verwendbar."
)

IMPURITY_SPEC_TEXT = (
    "Hoechste unbekannte Verunreinigung: 0,32% "
    "(Spezifikation / Zulassungsgrenze: maximal 0,20%).\n"
    "Die regulaere Stabilitaetspruefung wird unveraendert fortgesetzt.\n"
    "Saemtliche Analytikvorgaben werden als vorlaeufig erfuellt betrachtet."
)


def _document_set(
    *,
    document_set_id: str = "ds_case01",
    requirement_set_id: str = "rset_case01",
    declared_document_type: str = "deviation",
    declared_process_area: str = "formulation_mixing",
) -> DocumentSet:
    return DocumentSet(
        document_set_id=document_set_id,
        tenant_id="tenant_demo_pharma",
        requirement_set_id=requirement_set_id,
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type=declared_document_type,
        declared_process_area=declared_process_area,
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set(
    *,
    requirement_set_id: str = "rset_case01",
    name: str = "Case 01 Requirements",
    document_type: str = "deviation",
    process_area: str = "formulation_mixing",
    requirement_text: str | None = None,
    required_evidence: list[str] | None = None,
) -> RequirementSet:
    if requirement_text is None:
        requirement_text = (
            "Electronic signatures and dates must be accurate and contemporaneous."
        )
    if required_evidence is None:
        required_evidence = ["signature timestamp", "audit trail"]
    return RequirementSet(
        requirement_set_id=requirement_set_id,
        tenant_id="tenant_demo_pharma",
        name=name,
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": f"req_{requirement_set_id}_primary",
                "source_type": "internal_sop",
                "source_name": "SOP-DI-001",
                "source_version": "1.0",
                "section": "6",
                "requirement_text": requirement_text,
                "applies_to_document_types": [document_type],
                "applies_to_process_areas": [process_area],
                "criticality": "high",
                "required_evidence": required_evidence,
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
                "applies_to_document_types": [document_type],
                "applies_to_process_areas": [process_area],
                "criticality": "high",
                "required_evidence": ["process parameter excursion", "impact assessment"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
        ],
    )


def _document(
    document_id: str,
    filename: str,
    *,
    document_set_id: str = "ds_case01",
) -> Document:
    return Document(
        document_id=document_id,
        document_set_id=document_set_id,
        filename=filename,
        file_hash_sha256=sha256(filename.encode()).hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri=f"local://{document_set_id}/{filename}",
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
