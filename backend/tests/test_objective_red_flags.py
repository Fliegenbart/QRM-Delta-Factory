from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from app.audit.events import InMemoryAuditLog
from app.db.in_memory import InMemoryDocumentRepository
from app.evals.run_goldstandard import (
    _load_post_run_oracle,
    _review_pack_risks_as_findings,
    _score_visible_review_pack_errors,
)
from app.schemas.domain import Document, DocumentChunk, DocumentSet, RequirementSet
from app.services.objective_red_flags import ObjectiveRedFlagService
from app.services.review_pack import ReviewPackService
from app.services.risk_fusion import RiskFusionService
from app.verifiers.evidence import EvidenceVerifierService


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
        'Status: "Pass"' in item.quote for finding in findings for item in finding.evidence_items
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
        "maximal 0,20%" in item.quote for finding in findings for item in finding.evidence_items
    )


def test_objective_red_flags_detect_general_qc_change_control_cross_document_gaps() -> None:
    repository = InMemoryDocumentRepository()
    repository.create_requirement_set(_qc_change_requirement_set())
    repository.create_document_set(
        _document_set(
            document_set_id="ds_qc_west_2026",
            requirement_set_id="rset_qc_west_2026",
            declared_document_type="change_control_package",
            declared_process_area="qc_lab",
        )
    )
    _add_qc_change_documents(repository, document_set_id="ds_qc_west_2026")
    audit_log = InMemoryAuditLog()
    service = ObjectiveRedFlagService(repository=repository, audit_log=audit_log)

    findings = service.run_objective_red_flag_scan("ds_qc_west_2026")

    by_requirement = {
        finding.requirement_references[0]: finding
        for finding in findings
        if finding.requirement_references
    }
    expected_requirement_ids = {
        "req_qc_limit_fitness_at_tightened_limit",
        "req_qc_equipment_site_bridge_for_comparator_evidence",
        "req_qc_qa_approval_before_first_gmp_use",
        "req_qc_training_before_effective_sop_use",
        "req_qc_affected_batch_scope_includes_retests",
    }
    assert expected_requirement_ids <= set(by_requirement)
    assert all(
        finding.missing_information == []
        and all(item.support_type == "supports" for item in finding.evidence_items)
        for finding in by_requirement.values()
    )
    assert "NMT 0.20%" in by_requirement["req_qc_limit_fitness_at_tightened_limit"].risk_statement
    assert any(
        "Site East" in item.quote
        for item in by_requirement[
            "req_qc_equipment_site_bridge_for_comparator_evidence"
        ].evidence_items
    )
    assert any(
        "QA approval: pending" in item.quote
        for item in by_requirement["req_qc_qa_approval_before_first_gmp_use"].evidence_items
    )
    assert any(
        "optional / N/A" in item.quote
        for item in by_requirement["req_qc_training_before_effective_sop_use"].evidence_items
    )
    assert any(
        "A17-26045" in item.quote
        for item in by_requirement["req_qc_affected_batch_scope_includes_retests"].evidence_items
    )

    verified = EvidenceVerifierService(
        repository=repository,
        audit_log=audit_log,
    ).verify_findings("ds_qc_west_2026", list(by_requirement.values()))
    assert all(
        finding.verification_result is not None
        and finding.verification_result.quote_matches_chunk
        and finding.verification_result.requirement_applicable
        and finding.verification_result.evidence_support == "strong"
        and finding.verification_result.deterministic_checks_passed
        for finding in verified
    ), [
        (
            finding.requirement_references,
            finding.verification_result.evidence_support if finding.verification_result else None,
            finding.verification_result.deterministic_checks_passed
            if finding.verification_result
            else None,
            finding.verification_result.unsupported_claims if finding.verification_result else [],
        )
        for finding in verified
    ]
    repository.replace_risk_fusion_findings(
        document_set_id="ds_qc_west_2026",
        findings=verified,
    )
    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_qc_west_2026"
    )
    assert set(decision.published_finding_ids) == {finding.finding_id for finding in verified}


def test_objective_red_flags_do_not_report_qc_change_gaps_when_controls_are_documented() -> None:
    repository = InMemoryDocumentRepository()
    repository.create_requirement_set(_qc_change_requirement_set("rset_qc_controls"))
    repository.create_document_set(
        _document_set(
            document_set_id="ds_qc_controls",
            requirement_set_id="rset_qc_controls",
            declared_document_type="change_control_package",
            declared_process_area="qc_lab",
        )
    )
    _add_qc_change_documents(
        repository,
        document_set_id="ds_qc_controls",
        controls_documented=True,
    )

    findings = ObjectiveRedFlagService(
        repository=repository,
        audit_log=InMemoryAuditLog(),
    ).run_objective_red_flag_scan("ds_qc_controls")

    assert not {
        reference
        for finding in findings
        for reference in finding.requirement_references
        if reference.startswith("req_qc_")
    }


def test_objective_red_flags_do_not_infer_training_gap_from_missing_record_alone() -> None:
    repository = InMemoryDocumentRepository()
    repository.create_requirement_set(_qc_change_requirement_set("rset_qc_training_missing"))
    repository.create_document_set(
        _document_set(
            document_set_id="ds_qc_training_missing",
            requirement_set_id="rset_qc_training_missing",
            declared_document_type="change_control_package",
            declared_process_area="qc_lab",
        )
    )
    repository.add_document(
        document=_document(
            "doc_sop_south_8",
            "sop-south-8.md",
            document_set_id="ds_qc_training_missing",
        ),
        chunks=[
            _chunk(
                "chunk_sop_south_8",
                "doc_sop_south_8",
                "SOP AX-77 v3 is effective and requires training before use or review.",
            )
        ],
    )
    repository.add_document(
        document=_document(
            "doc_execution_south_8",
            "execution-south-8.md",
            document_set_id="ds_qc_training_missing",
        ),
        chunks=[
            _chunk(
                "chunk_execution_south_8",
                "doc_execution_south_8",
                "Analyst used SOP AX-77 v3 during routine GMP execution for batch S8-440.",
            )
        ],
    )

    findings = ObjectiveRedFlagService(
        repository=repository,
        audit_log=InMemoryAuditLog(),
    ).run_objective_red_flag_scan("ds_qc_training_missing")

    training_findings = [
        finding
        for finding in findings
        if finding.requirement_references == ["req_qc_training_before_effective_sop_use"]
    ]
    assert training_findings == []


def test_objective_red_flags_match_all_real_pkg001_qc_findings_in_visible_review_pack() -> None:
    fixture_dir = Path(__file__).parent / "fixtures" / "pkg001"
    repository = InMemoryDocumentRepository()
    repository.create_requirement_set(_real_qc_requirement_set())
    repository.create_document_set(
        _document_set(
            document_set_id="ds_real_qc_fixture",
            requirement_set_id="rset_real_qc_fixture",
            declared_document_type="change_control_package",
            declared_process_area="qc_lab",
        )
    )
    for source_path in sorted(fixture_dir.glob("*.md")):
        document_id = f"doc_real_{source_path.stem}"
        source_text = source_path.read_text(encoding="utf-8")
        repository.add_document(
            document=_document(
                document_id,
                source_path.name,
                document_set_id="ds_real_qc_fixture",
            ),
            chunks=[
                _chunk(
                    f"chunk_real_{source_path.stem}",
                    document_id,
                    source_text,
                )
            ],
        )

    audit_log = InMemoryAuditLog()
    raw_findings = ObjectiveRedFlagService(
        repository=repository,
        audit_log=audit_log,
    ).run_objective_red_flag_scan("ds_real_qc_fixture")
    verified_findings = EvidenceVerifierService(
        repository=repository,
        audit_log=audit_log,
    ).verify_findings("ds_real_qc_fixture", raw_findings)
    repository.replace_risk_fusion_findings(
        document_set_id="ds_real_qc_fixture",
        findings=verified_findings,
    )
    decision = RiskFusionService(repository=repository, audit_log=audit_log).run_risk_fusion(
        "ds_real_qc_fixture"
    )
    review_pack = ReviewPackService(repository=repository, audit_log=audit_log).get_review_pack(
        "ds_real_qc_fixture"
    )

    expected_requirement_ids = {
        "req_qc_limit_fitness_at_tightened_limit",
        "req_qc_equipment_site_bridge_for_comparator_evidence",
        "req_qc_qa_approval_before_first_gmp_use",
        "req_qc_training_before_effective_sop_use",
        "req_qc_affected_batch_scope_includes_retests",
    }
    published_qc_requirements = {
        reference
        for finding in verified_findings
        if finding.finding_id in decision.published_finding_ids
        for reference in finding.requirement_references
        if reference.startswith("req_qc_")
    }
    assert published_qc_requirements == expected_requirement_ids, [
        (
            finding.requirement_references,
            finding.evidence_support,
            finding.verification_result.evidence_support
            if finding.verification_result is not None
            else None,
            finding.verification_result.deterministic_checks_passed
            if finding.verification_result is not None
            else None,
            finding.verification_result.unsupported_claims
            if finding.verification_result is not None
            else [],
            finding.risk_statement,
        )
        for finding in verified_findings
    ]

    oracle = _load_post_run_oracle(fixture_dir / "GOLD_STANDARD.json")
    matched, missed = _score_visible_review_pack_errors(
        oracle,
        _review_pack_risks_as_findings(
            [risk.model_dump(mode="json") for risk in review_pack.top_risks]
        ),
    )
    assert len(matched) == 5, missed
    assert missed == []


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


def _real_qc_requirement_set() -> RequirementSet:
    library_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "data"
        / "gmp-general-requirement-library.json"
    )
    payload = json.loads(library_path.read_text(encoding="utf-8"))
    payload.update(
        {
            "requirement_set_id": "rset_real_qc_fixture",
            "tenant_id": "tenant_demo_pharma",
            "imported_at": datetime.now(UTC).isoformat(),
            "imported_by": "user_quality_admin",
            "active": True,
        }
    )
    return RequirementSet.model_validate(payload)


def _qc_change_requirement_set(
    requirement_set_id: str = "rset_qc_west_2026",
) -> RequirementSet:
    requirements = [
        (
            "req_qc_limit_fitness_at_tightened_limit",
            "A tightened quantitative QC limit requires demonstrated method fitness at "
            "the new limit and on the current routine platform.",
        ),
        (
            "req_qc_equipment_site_bridge_for_comparator_evidence",
            "Comparator evidence from another site or equipment requires a formal "
            "bridge, transfer, or documented equivalence.",
        ),
        (
            "req_qc_qa_approval_before_first_gmp_use",
            "QA approval must be documented before first GMP use or routine execution.",
        ),
        (
            "req_qc_training_before_effective_sop_use",
            "An effective SOP requires training before personnel use or review it.",
        ),
        (
            "req_qc_affected_batch_scope_includes_retests",
            "Affected batch scope must include retests and retained-sample batches "
            "found in execution.",
        ),
    ]
    return RequirementSet(
        requirement_set_id=requirement_set_id,
        tenant_id="tenant_demo_pharma",
        name="West QC Change Requirements",
        version="2026.4",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": requirement_id,
                "source_type": "internal_sop",
                "source_name": "SOP-QC-CROSSDOC",
                "source_version": "6.4",
                "section": "5",
                "requirement_text": requirement_text,
                "applies_to_document_types": ["change_control_package"],
                "applies_to_process_areas": ["qc_lab"],
                "criticality": "high",
                "required_evidence": ["source excerpts"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
            for requirement_id, requirement_text in requirements
        ],
    )


def _add_qc_change_documents(
    repository: InMemoryDocumentRepository,
    *,
    document_set_id: str,
    controls_documented: bool = False,
) -> None:
    change_text = (
        "Change CHG-WEST-41 tightens assay Q from NMT 0.45% to NMT 0.20%.\n"
        "Affected batch scope: LOT-A11, LOT-B12, LOT-R77, and A17-26045 retest retained sample.\n"
        "SOP QS-44 v6 is effective and requires training before use or review.\n"
        if controls_documented
        else "Change CHG-WEST-41 tightens assay Q from NMT 0.45% to NMT 0.20%.\n"
        "Affected batch scope: LOT-A11, LOT-B12, and A17-26044 only.\n"
        "SOP QS-44 v6 is effective and requires training before use or review.\n"
    )
    validation_text = (
        "Accuracy and precision at NMT 0.20% were demonstrated on current routine "
        "platform UPLC-Analytix-9.\n"
        "Comparator evidence from Site East on UPLC-7 has an approved formal method "
        "transfer bridge and equipment equivalence.\n"
        if controls_documented
        else "Legacy validation covered NMT 0.45% on UPLC-7; current routine platform "
        "UPLC-Analytix-9 was not covered at NMT 0.20%.\n"
        "Comparator evidence was generated at Site East on UPLC-7. No formal "
        "bridge, transfer, or equipment equivalence is documented.\n"
    )
    execution_text = (
        "First GMP routine execution used the new NMT 0.20% limit for LOT-C13 after "
        "QA approval: approved.\n"
        "Training for SOP QS-44 v6 is complete before analyst review.\n"
        "Execution record processed retest retained-sample batch A17-26045 using the "
        "changed specification on 2026-07-24.\n"
        if controls_documented
        else "First GMP routine execution used the new NMT 0.20% limit for LOT-C13; "
        "QA approval: pending.\n"
        "Training matrix marks SOP QS-44 v6 as optional / N/A for analyst review.\n"
        "Execution record processed retest retained-sample batch A17-26045 using the "
        "changed specification on 2026-07-24.\n"
    )
    repository.add_document(
        document=_document(
            "doc_change_west_41",
            "change-west-41.md",
            document_set_id=document_set_id,
        ),
        chunks=[
            _chunk(
                "chunk_change_west_41",
                "doc_change_west_41",
                change_text,
            )
        ],
    )
    repository.add_document(
        document=_document(
            "doc_validation_east_41",
            "validation-east-41.md",
            document_set_id=document_set_id,
        ),
        chunks=[
            _chunk(
                "chunk_validation_east_41",
                "doc_validation_east_41",
                validation_text,
            )
        ],
    )
    repository.add_document(
        document=_document(
            "doc_execution_west_41",
            "execution-west-41.md",
            document_set_id=document_set_id,
        ),
        chunks=[
            _chunk(
                "chunk_execution_west_41",
                "doc_execution_west_41",
                execution_text,
            )
        ],
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
        requirement_text = "Electronic signatures and dates must be accurate and contemporaneous."
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
