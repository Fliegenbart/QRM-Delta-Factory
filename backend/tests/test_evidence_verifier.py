from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import pytest

from app.agents.providers.mock_provider import MockProvider
from app.audit.events import audit_log
from app.db.in_memory import repository
from app.schemas.domain import Document, DocumentChunk, DocumentSet, RequirementSet, RiskFinding
from app.schemas.review import ReviewerAgentOutput
from app.services.review_orchestrator import ReviewerAgent
from app.services.risk_fusion import RiskFusionService
from app.verifiers.evidence import (
    EvidenceVerifierService,
    _factual_anchors,
    _synthesis_concepts,
)

LIMIT_RISK_STATEMENT = (
    "MV-VAL-221: Für 0,10 % keine separate Genauigkeits- oder Präzisionsstufe; "
    "UPLC-12 nicht Teil des ursprünglichen Protokolls."
)
EQUIPMENT_QUOTE = (
    "Die Routinegeräteplattform UPLC-12 am Standort BRX-3 war nicht Teil "
    "des ursprünglichen Protokolls."
)
QA_RISK_STATEMENT = (
    "QA-QC Reviewer pending; QA-Freigabe vor erster Chargenfreigabe erforderlich; "
    "QA-Freigabesignaturblock im Execution Record leer."
)
TRAINING_RISK_STATEMENT = (
    "Training record attached N/A no procedural change; Read-and-Understand-Training "
    "zur gültigen SOP-Version erforderlich; Trainingsnachweis SOP v4.0 "
    "im Batch-Review-Paket nicht abgelegt."
)
EXECUTION_TRAINING_QUOTE = (
    "Ein Trainingsnachweis zu SOP v4.0 ist im Batch-Review-Paket nicht abgelegt."
)
QA_EXECUTION_QUOTE = "Ein QA-Freigabesignaturblock ist in diesem Execution Record leer."
TRAINING_CHANGE_QUOTE = (
    "Das Feld Training record attached ist mit N/A - no procedural change ausgefüllt."
)
SCOPE_CHANGE_QUOTE = "Für A17-26045 und A17-26046 soll der neue Grenzwert angewendet werden."
EQUIPMENT_RISK_STATEMENT = (
    "Vergleichslabordaten akzeptiert; keine separate Bridge; dokumentierte Geräteäquivalenz "
    "oder genehmigtes Bridging erforderlich; No formal transfer was executed."
)
SCOPE_RISK_STATEMENT = (
    "A17-26045 und A17-26046: neuer Grenzwert; Rückstellmuster A17-26044 erneut bewertet; "
    "A17-26044 Retest."
)
SOP_LIMIT_QUOTE = "muss die Methodenfitness am neuen Grenzwert dokumentiert werden"
VALIDATION_LIMIT_QUOTE = (
    "Für 0,10 % wurde keine separate Genauigkeits- oder Präzisionsstufe durchgeführt."
)
VALIDATION_PACKAGE_QUOTE = "Das Validierungspaket MV-VAL-221 wurde 2024"
SOP_EQUIPMENT_QUOTE = (
    "ist eine dokumentierte Geräteäquivalenz oder ein genehmigtes Bridging erforderlich"
)
VALIDATION_TRANSFER_QUOTE = "No formal transfer was executed; comparison is informational only."
SOP_QA_QUOTE = (
    "Die QA-Freigabe des Change Controls und der betroffenen Spezifikationsseite "
    "muss vor der ersten Chargenfreigabe vorliegen."
)
SOP_TRAINING_QUOTE = "müssen ein Read-and-Understand-Training zur gültigen SOP-Version"
EXECUTION_RETEST_QUOTE = (
    "ein Rückstellmuster von A17-26044 aufgrund einer internen Trendanfrage erneut bewertet"
)
PKG001_GOLD = json.loads(
    (Path(__file__).parent / "fixtures" / "pkg001" / "GOLD_STANDARD.json").read_text(
        encoding="utf-8"
    )
)["must_detect_findings"]
PKG001_REQUIREMENTS = {
    "PKG001-F01": "req_limit_method_fitness",
    "PKG001-F02": "req_equipment_bridge",
    "PKG001-F03": "req_qa_before_gmp_use",
    "PKG001-F04": "req_training_before_specification_use",
    "PKG001-F05": "req_complete_batch_scope",
}
PKG001_ADDITIONAL_EVIDENCE = {
    "PKG001-F03": [
        {
            "document_id": "CC-SYN-001",
            "quote": "Für A17-26045 und A17-26046 soll der neue Grenzwert angewendet werden",
        },
        {
            "document_id": "BR-SYN-001",
            "quote": "Die Routineprüfung wurde für A17-26045 am 2026-03-20 gestartet",
        },
    ],
    "PKG001-F05": [
        {
            "document_id": "BR-SYN-001",
            "quote": (
                "Dieses Execution Record fasst die Impurity-Q-Prüfungen für "
                "AUR-17 Stage-4 am Standort BRX-3 zusammen"
            ),
        }
    ],
}
PKG001_SOURCE_FILES = {
    "CC-SYN-001": "change_control.md",
    "SOP-QC-AN-014-EX": "sop_excerpt.md",
    "VE-SYN-001": "validation_or_test_evidence.md",
    "RA-SYN-001": "baseline_risk_assessment.md",
    "BR-SYN-001": "batch_record_or_execution_record.md",
}


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set())
    repository.add_document(document=_document(), chunks=[_chunk()])


def test_valid_quote_and_requirement_produce_strong_verification_result() -> None:
    finding = _finding()
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.finding_id == finding.finding_id
    assert result.evidence_support == "strong"
    assert result.quote_exists is True
    assert result.quote_matches_chunk is True
    assert result.requirement_applicable is True
    assert result.deterministic_checks_passed is True
    assert result.unsupported_claims == []
    assert result.missing_evidence == []


def test_wrong_quote_is_not_silently_accepted() -> None:
    finding = _finding(
        quote="Impact assessment: no product impact identified.",
        risk_statement="Unsupported claim should not be accepted.",
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.quote_exists is False
    assert result.quote_matches_chunk is False
    assert result.evidence_support == "none"
    assert result.deterministic_checks_passed is False
    assert result.unsupported_claims


def test_quote_that_does_not_support_the_risk_statement_is_evidence_support_none() -> None:
    finding = _finding(
        quote="Impact assessment: possible false accept of defective container.",
        risk_statement="QA approval is documented and batch release is closed.",
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.quote_exists is True
    assert result.quote_matches_chunk is True
    assert result.requirement_applicable is True
    assert result.evidence_support == "none"
    assert result.deterministic_checks_passed is False
    assert any("risk statement" in item.lower() for item in result.unsupported_claims)


def test_partial_evidence_that_only_supports_part_of_statement_is_partial() -> None:
    finding = _finding(
        quote="Impact assessment: possible false accept of defective container.",
        risk_statement=(
            "Impact assessment identifies possible false accept risk, but QA approval is "
            "documented."
        ),
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.quote_exists is True
    assert result.quote_matches_chunk is True
    assert result.evidence_support == "partial"
    assert result.deterministic_checks_passed is False
    assert any("risk statement" in item.lower() for item in result.unsupported_claims)


def test_wrong_requirement_is_marked_not_applicable() -> None:
    finding = _finding(requirement_references=["req_not_applicable_to_deviation"])
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.requirement_applicable is False
    assert result.deterministic_checks_passed is False
    assert result.evidence_support == "weak"
    assert "not applicable" in result.verifier_rationale.lower()


def test_wrong_page_fails_deterministic_checks() -> None:
    finding = _finding(page=5)
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.quote_matches_chunk is True
    assert result.deterministic_checks_passed is False
    assert any("page" in item.lower() for item in result.missing_evidence)


def test_verification_result_is_attached_and_audited() -> None:
    finding = _finding()
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    verified_findings = service.verify_findings("ds_verifier_demo", [finding])

    assert verified_findings[0].verification_result is not None
    assert verified_findings[0].verification_result.evidence_support == "strong"
    assert repository.list_risk_findings("ds_verifier_demo")[0].verification_result is not None
    event = audit_log.list_events()[-1]
    assert event.event_type == "evidence_verifier_run"
    assert event.payload["finding_count"] == 1
    assert event.payload["strong_count"] == 1


def test_missing_document_is_stored_as_unverified_not_deleted() -> None:
    finding = _finding(document_id="doc_missing")
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    verified_findings = service.verify_findings("ds_verifier_demo", [finding])

    assert len(verified_findings) == 1
    result = verified_findings[0].verification_result
    assert result is not None
    assert result.quote_exists is False
    assert result.evidence_support == "none"
    assert repository.list_risk_findings("ds_verifier_demo")[0].finding_id == finding.finding_id


@pytest.mark.parametrize("gold_finding", PKG001_GOLD, ids=lambda item: item["finding_id"])
def test_pkg001_gold_risk_statements_are_strong_only_with_exact_multi_document_support(
    gold_finding: dict[str, object],
) -> None:
    expected_evidence_refs = gold_finding["expected_evidence_refs"]
    assert isinstance(expected_evidence_refs, list)
    evidence_refs = [
        *expected_evidence_refs,
        *PKG001_ADDITIONAL_EVIDENCE.get(str(gold_finding["finding_id"]), []),
    ]
    _add_gold_fixture_documents(evidence_refs)
    finding = _multi_document_finding(
        risk_statement=str(gold_finding["risk_statement"]),
        evidence=[
            (_gold_document_id(str(reference["document_id"])), str(reference["quote"]))
            for reference in evidence_refs
        ],
        requirement_references=[PKG001_REQUIREMENTS[str(gold_finding["finding_id"])]],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support == "strong"
    assert result.deterministic_checks_passed is True
    assert result.unsupported_claims == []
    assert result.missing_evidence == []


def test_pkg001_live_shaped_candidates_normalize_verify_and_publish_all_five_themes() -> None:
    fixture_references: list[object] = []
    candidates: list[dict[str, object]] = []
    categories = [
        "method_validation",
        "equipment_bridge",
        "qa_approval",
        "training_control",
        "batch_scope",
    ]
    deliberately_wrong_hash = "0" * 64

    for index, gold_finding in enumerate(PKG001_GOLD, start=1):
        finding_id = str(gold_finding["finding_id"])
        expected_evidence_refs = gold_finding["expected_evidence_refs"]
        assert isinstance(expected_evidence_refs, list)
        evidence_refs = [
            *expected_evidence_refs,
            *PKG001_ADDITIONAL_EVIDENCE.get(finding_id, []),
        ]
        fixture_references.extend(evidence_refs)
        candidates.append(
            {
                "finding_id": f"finding_pkg001_live_{index}",
                "document_set_id": "ds_verifier_demo",
                "risk_category": categories[index - 1],
                "severity": gold_finding["severity"],
                "likelihood": 3,
                "detectability": 3,
                "risk_statement": gold_finding["risk_statement"],
                "evidence_items": [
                    {
                        "document_id": _gold_document_id(str(reference["document_id"])),
                        "chunk_id": (
                            "chunk_"
                            f"{_gold_document_id(str(reference['document_id'])).removeprefix('doc_')}"
                            "_p1"
                        ),
                        "page": 1,
                        "quote": str(reference["quote"]),
                        "quote_hash": deliberately_wrong_hash,
                        "support_type": "supports",
                        "verifier_score": 0.95,
                    }
                    for reference in evidence_refs
                ],
                "requirement_references": [PKG001_REQUIREMENTS[finding_id]],
                "missing_information": [],
                "model_provider": "mock",
                "model_name": "mock-live-shaped-reviewer",
                "model_version": "0.1.0",
                "prompt_version": "pkg001-live-shaped-v1",
                "evidence_support": "partial",
                "recommended_action": "Route to QA/SME for review.",
                "auto_close_allowed": False,
                "status": "needs_human_review",
            }
        )

    _add_gold_fixture_documents(fixture_references)
    provider = MockProvider(
        model_name="mock-live-shaped-reviewer",
        model_version="0.1.0",
        configured_model_id="mock-live-shaped-pkg001",
        prompt_version="pkg001-live-shaped-v1",
        structured_output={
            "coverage_summary": "Five live-shaped candidates from PKG001.",
            "findings": candidates,
        },
    )
    raw_provider_output = provider.run_structured(
        prompt="Return live-shaped reviewer output.",
        input_schema={"document_set_id": "ds_verifier_demo"},
        output_schema=ReviewerAgentOutput,
    )
    raw_candidates = ReviewerAgentOutput.model_validate(raw_provider_output)
    assert {
        evidence.quote_hash
        for finding in raw_candidates.findings
        for evidence in finding.evidence_items
    } == {deliberately_wrong_hash}

    requirement_set = repository.get_requirement_set("rset_verifier_demo_2026")
    assert requirement_set is not None
    relevant_requirements = [
        requirement
        for requirement in requirement_set.requirements
        if requirement.requirement_id in set(PKG001_REQUIREMENTS.values())
    ]
    agent = ReviewerAgent(
        agent_id="reviewer_pkg001_live_shape",
        role="live-shaped regression reviewer",
        prompt_version="pkg001-live-shaped-v1",
        applicable_risk_categories=categories,
        provider=provider,
    )

    normalized_candidates = agent.run(
        claims=[],
        requirements=relevant_requirements,
        evidence_context=[],
        document_set_id="ds_verifier_demo",
        case_signals=[],
        knowledge_pack_ids=[],
        missing_knowledge_pack_ids=[],
        requirement_package_hash=sha256(b"pkg001-live-shaped").hexdigest(),
        calibration_examples=[],
        calibration_prompt_block="",
        calibration_pack_hash=None,
    ).findings

    assert all(
        evidence.quote_hash == sha256(evidence.quote.encode()).hexdigest()
        for finding in normalized_candidates
        for evidence in finding.evidence_items
    )
    verified_findings = EvidenceVerifierService(
        repository=repository,
        audit_log=audit_log,
    ).verify_findings("ds_verifier_demo", normalized_candidates)
    persisted_findings = repository.list_risk_findings("ds_verifier_demo")
    decision = RiskFusionService(
        repository=repository,
        audit_log=audit_log,
    ).run_risk_fusion("ds_verifier_demo")

    assert len(verified_findings) == len(PKG001_GOLD) == len(persisted_findings)
    assert all(
        finding.verification_result is not None
        and finding.verification_result.deterministic_checks_passed
        for finding in persisted_findings
    )
    assert {
        (finding.risk_category, finding.requirement_references[0])
        for finding in persisted_findings
    } == set(zip(categories, PKG001_REQUIREMENTS.values(), strict=True))
    assert {cluster.root_finding_id for cluster in decision.finding_clusters} == {
        finding.finding_id for finding in persisted_findings
    }
    assert set(decision.published_finding_ids) == {
        finding.finding_id for finding in persisted_findings
    }


def test_multi_document_synthesis_rejects_fuzzy_quote_substitution() -> None:
    _add_multi_document_sources()
    altered_quote = (
        "Ein QA-Genehmigungssignaturblock ist in diesem Execution Record leer."
    )
    finding = _multi_document_finding(
        risk_statement=QA_RISK_STATEMENT,
        evidence=[
            ("doc_change_qa", "QA-QC Reviewer: pending"),
            ("doc_execution_qa", altered_quote),
        ],
        requirement_references=["req_qa_before_gmp_use"],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert result.quote_matches_chunk is False


def test_multi_document_synthesis_rejects_incorrect_quote_hash() -> None:
    _add_multi_document_sources()
    finding = _multi_document_finding(
        risk_statement=QA_RISK_STATEMENT,
        evidence=[
            ("doc_change_qa", "QA-QC Reviewer: pending"),
            ("doc_execution_qa", QA_EXECUTION_QUOTE),
        ],
        requirement_references=["req_qa_before_gmp_use"],
    )
    finding = finding.model_copy(
        update={
            "evidence_items": [
                finding.evidence_items[0].model_copy(
                    update={"quote_hash": sha256(b"incorrect quote hash").hexdigest()}
                ),
                finding.evidence_items[1],
            ]
        }
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert any("quote_hash" in item for item in result.missing_evidence)


def test_multi_document_synthesis_rejects_fabricated_anchorless_clause() -> None:
    gold_finding = PKG001_GOLD[1]
    evidence_refs = gold_finding["expected_evidence_refs"]
    assert isinstance(evidence_refs, list)
    _add_gold_evidence_documents(evidence_refs)
    finding = _multi_document_finding(
        risk_statement=(
            f"{gold_finding['risk_statement']}; "
            "Autonomous budget allocation is approved for immediate use."
        ),
        evidence=[
            (_gold_document_id(str(reference["document_id"])), str(reference["quote"]))
            for reference in evidence_refs
        ],
        requirement_references=["req_equipment_bridge"],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert any("autonomous budget" in item.lower() for item in result.unsupported_claims)


@pytest.mark.parametrize(
    "fabricated_suffix",
    [
        "Documented equipment bridge authorizes autonomous budget allocation.",
        "Documented equipment authorizes autonomous budget allocation.",
    ],
)
def test_multi_document_synthesis_rejects_same_clause_concept_padding(
    fabricated_suffix: str,
) -> None:
    gold_finding = PKG001_GOLD[1]
    evidence_refs = gold_finding["expected_evidence_refs"]
    assert isinstance(evidence_refs, list)
    _add_gold_evidence_documents(evidence_refs)
    finding = _multi_document_finding(
        risk_statement=(
            f"{str(gold_finding['risk_statement']).rstrip('.')} and "
            f"{fabricated_suffix}"
        ),
        evidence=[
            (_gold_document_id(str(reference["document_id"])), str(reference["quote"]))
            for reference in evidence_refs
        ],
        requirement_references=["req_equipment_bridge"],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert result.unsupported_claims


def test_multi_document_synthesis_rejects_ten_of_thirteen_concept_padding() -> None:
    gold_finding = PKG001_GOLD[0]
    evidence_refs = gold_finding["expected_evidence_refs"]
    assert isinstance(evidence_refs, list)
    _add_gold_evidence_documents(evidence_refs)
    finding = _multi_document_finding(
        risk_statement=(
            "Validation coverage decision limit equipment historical new NMT "
            "Genauigkeits Präzisionsstufe authorizes autonomous budget."
        ),
        evidence=[
            (_gold_document_id(str(reference["document_id"])), str(reference["quote"]))
            for reference in evidence_refs
        ],
        requirement_references=["req_limit_method_fitness"],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert result.unsupported_claims


def test_multi_document_synthesis_with_duplicate_quotes_is_not_strong() -> None:
    _add_multi_document_sources()
    finding = _multi_document_finding(
        risk_statement="NMT 0,10 %",
        evidence=[
            (
                "doc_change_limit",
                "von NMT 0,20 % auf NMT 0,10 % abgesenkt",
            ),
            (
                "doc_change_limit_duplicate",
                "von NMT 0,20 % auf NMT 0,10 % abgesenkt",
            ),
        ],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert any("non-duplicate" in item for item in result.missing_evidence)


def test_multi_document_synthesis_rejects_markdown_only_duplicate_quotes() -> None:
    plain_quote = "QA approval required before release"
    emphasized_quote = "**QA approval required before release**"
    _add_document_with_chunk(document_id="doc_qa_plain", text=plain_quote)
    _add_document_with_chunk(document_id="doc_qa_emphasized", text=emphasized_quote)
    finding = _multi_document_finding(
        risk_statement=plain_quote,
        evidence=[
            ("doc_qa_plain", plain_quote),
            ("doc_qa_emphasized", emphasized_quote),
        ],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.quote_matches_chunk is True
    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert any("non-duplicate" in item for item in result.missing_evidence)


def test_multi_document_synthesis_covers_anchor_inside_markdown_presentation_markers() -> None:
    emphasized_quote = "**A17-26045** QA-Freigabe pending"
    _add_document_with_chunk(document_id="doc_markdown_anchor", text=emphasized_quote)
    _add_document_with_chunk(
        document_id="doc_markdown_requirement",
        text="QA-Freigabe erforderlich",
    )
    finding = _multi_document_finding(
        risk_statement="A17-26045 QA-Freigabe pending.",
        evidence=[
            ("doc_markdown_anchor", emphasized_quote),
            ("doc_markdown_requirement", "QA-Freigabe erforderlich"),
        ],
        requirement_references=["req_qa_before_gmp_use"],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support == "strong"
    assert result.deterministic_checks_passed is True
    assert not any("factual anchor" in item for item in result.unsupported_claims)


def test_synthesis_concepts_equates_ascii_german_transliterations_with_umlauts() -> None:
    source_concepts = _synthesis_concepts("Rückstellmuster geändert")
    model_concepts = _synthesis_concepts("Rueckstellmuster geaendert")

    assert model_concepts == source_concepts


def test_synthesis_concepts_does_not_accept_unrelated_terms() -> None:
    source_concepts = _synthesis_concepts("Rückstellmuster wurde erneut bewertet")
    unrelated_concepts = _synthesis_concepts("Fremdwort wurde erneut bewertet")

    assert "fremdwort" not in source_concepts
    assert source_concepts != unrelated_concepts


def test_factual_anchors_capture_complete_hyphenated_identifiers_without_fragments() -> None:
    anchors = _factual_anchors(
        "CC-SYN-001 follows SOP-QC-AN-014 for A17-26045 at v4.0 and 0,10 %."
    )

    assert {"CC-SYN-001", "SOP-QC-AN-014", "A17-26045", "v4.0", "0,10 %"} <= anchors
    assert {"CC-SYN", "SYN-001", "SOP-QC", "QC-AN", "AN-014"}.isdisjoint(anchors)


def test_multi_document_synthesis_with_only_one_source_is_not_strong() -> None:
    _add_multi_document_sources()
    finding = _multi_document_finding(
        risk_statement="NMT 0,10 %",
        evidence=[
            ("doc_single_source", "NMT 0,10 %"),
            ("doc_single_source", "supporting source detail"),
        ],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert any("distinct source" in item for item in result.missing_evidence)


def test_multi_document_synthesis_with_unrelated_quotes_is_not_strong() -> None:
    _add_multi_document_sources()
    finding = _multi_document_finding(
        risk_statement=LIMIT_RISK_STATEMENT,
        evidence=[
            ("doc_change_qa", "QA-QC Reviewer: pending"),
            ("doc_execution_qa", QA_EXECUTION_QUOTE),
        ],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False


def test_multi_document_synthesis_with_an_uncovered_factual_anchor_is_not_strong() -> None:
    _add_multi_document_sources()
    finding = _multi_document_finding(
        risk_statement="UPLC-99 BRX-3 no equipment bridge from HPLC-02 BRX-North.",
        evidence=[
            ("doc_risk_assessment", "Vergleichslabordaten akzeptiert; keine separate Bridge"),
            (
                "doc_validation",
                EQUIPMENT_QUOTE,
            ),
        ],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert any("factual anchor" in item for item in result.unsupported_claims)


@pytest.mark.parametrize("support_type", ["contextual", "contradicts"])
def test_multi_document_synthesis_with_non_supporting_evidence_is_not_strong(
    support_type: str,
) -> None:
    _add_multi_document_sources()
    finding = _multi_document_finding(
        risk_statement=QA_RISK_STATEMENT,
        evidence=[
            ("doc_change_qa", "QA-QC Reviewer: pending"),
            ("doc_execution_qa", QA_EXECUTION_QUOTE),
        ],
        support_types=["supports", support_type],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert any("supports" in item for item in result.unsupported_claims)


def test_multi_document_synthesis_with_inapplicable_requirement_is_not_strong() -> None:
    _add_multi_document_sources()
    finding = _multi_document_finding(
        risk_statement="A17-26044 Retest occurs outside A17-26045 and A17-26046 scope.",
        evidence=[
            ("doc_change_scope", SCOPE_CHANGE_QUOTE),
            ("doc_execution_scope", "A17-26044 Retest"),
        ],
        requirement_references=["req_not_applicable_to_deviation"],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert result.requirement_applicable is False


def test_multi_document_synthesis_with_missing_information_is_not_strong() -> None:
    _add_multi_document_sources()
    finding = _multi_document_finding(
        risk_statement="A17-26044 Retest occurs outside A17-26045 and A17-26046 scope.",
        evidence=[
            ("doc_change_scope", SCOPE_CHANGE_QUOTE),
            ("doc_execution_scope", "A17-26044 Retest"),
        ],
        missing_information=["Confirm whether the retest was included in change scope."],
    )
    service = EvidenceVerifierService(repository=repository, audit_log=audit_log)

    result = service.verify_finding("ds_verifier_demo", finding)

    assert result.evidence_support != "strong"
    assert result.deterministic_checks_passed is False
    assert result.missing_evidence[-1] == "Confirm whether the retest was included in change scope."


def _document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_verifier_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_verifier_demo_2026",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="change_control",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_verifier_demo_2026",
        tenant_id="tenant_demo_pharma",
        name="Verifier Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_deviation_documented_impact_assessment",
                "source_type": "internal_sop",
                "source_name": "SOP-DEV-001",
                "source_version": "4.2",
                "section": "6.3",
                "requirement_text": "Deviation records need documented product impact assessment.",
                "applies_to_document_types": ["change_control", "deviation"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["deviation record", "impact assessment"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_limit_method_fitness",
                "source_type": "internal_sop",
                "source_name": "SOP-QC-AN-014",
                "source_version": "4.0",
                "section": "5.2",
                "requirement_text": (
                    "Tightened quantitative limits require documented method fitness "
                    "at the new decision limit."
                ),
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["method fitness review"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_equipment_bridge",
                "source_type": "internal_sop",
                "source_name": "SOP-QC-AN-014",
                "source_version": "4.0",
                "section": "5.3",
                "requirement_text": (
                    "A site or equipment change requires a documented equipment "
                    "equivalence bridge before routine use."
                ),
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["equipment equivalence checklist"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_qa_before_gmp_use",
                "source_type": "internal_sop",
                "source_name": "SOP-QC-AN-014",
                "source_version": "4.0",
                "section": "5.5",
                "requirement_text": "QA approval is required before first batch release.",
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["QA approval record"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_training_before_specification_use",
                "source_type": "internal_sop",
                "source_name": "SOP-QC-AN-014",
                "source_version": "4.0",
                "section": "5.4",
                "requirement_text": (
                    "Required training on the active SOP and changed specification "
                    "must be completed before result review."
                ),
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["training matrix"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_complete_batch_scope",
                "source_type": "internal_sop",
                "source_name": "SOP-QC-AN-014",
                "source_version": "4.0",
                "section": "5.6",
                "requirement_text": (
                    "Affected-batch assessment must include retests and retained "
                    "samples within the declared change scope."
                ),
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "high",
                "required_evidence": ["batch impact assessment"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
            {
                "requirement_id": "req_not_applicable_to_deviation",
                "source_type": "internal_sop",
                "source_name": "SOP-CAPA-001",
                "source_version": "1.0",
                "section": "2.0",
                "requirement_text": "CAPA-only requirement.",
                "applies_to_document_types": ["capa"],
                "applies_to_process_areas": ["packaging"],
                "criticality": "medium",
                "required_evidence": ["CAPA record"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            },
        ],
    )


def _document() -> Document:
    return Document(
        document_id="doc_verifier_deviation",
        document_set_id="ds_verifier_demo",
        filename="deviation.txt",
        file_hash_sha256=sha256(b"deviation.txt").hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri="local://verifier/deviation.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=0.95,
        language="en",
        metadata={},
    )


def _chunk() -> DocumentChunk:
    text = (
        "Deviation DEV-2026-014 for Batch BATCH-001. "
        "Impact assessment: possible false accept of defective container."
    )
    return DocumentChunk(
        chunk_id="chunk_verifier_deviation_p1",
        document_id="doc_verifier_deviation",
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )


def _finding(
    *,
    quote: str = "Impact assessment: possible false accept of defective container.",
    risk_statement: str = "Deviation impact assessment indicates possible false accept risk.",
    document_id: str = "doc_verifier_deviation",
    page: int = 1,
    requirement_references: list[str] | None = None,
) -> RiskFinding:
    return RiskFinding(
        finding_id="finding_verifier_demo",
        document_set_id="ds_verifier_demo",
        risk_category="deviation_management",
        severity="high",
        likelihood=3,
        detectability=3,
        risk_statement=risk_statement,
        evidence_items=[
            {
                "document_id": document_id,
                "chunk_id": "chunk_verifier_deviation_p1",
                "page": page,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": "supports",
                "verifier_score": 0.9,
            }
        ],
        requirement_references=requirement_references
        or ["req_deviation_documented_impact_assessment"],
        missing_information=[],
        model_provider="mock",
        model_name="mock-reviewer",
        model_version="0.1.0",
        prompt_version="deviation_reviewer_v1",
        evidence_support="partial",
        recommended_action="Route to QA/SME for review.",
        auto_close_allowed=False,
        status="needs_human_review",
    )


def _add_multi_document_sources() -> None:
    source_texts = {
        "doc_change_limit": "von NMT 0,20 % auf NMT 0,10 % abgesenkt",
        "doc_change_limit_duplicate": "von NMT 0,20 % auf NMT 0,10 % abgesenkt",
        "doc_single_source": "NMT 0,10 % supporting source detail",
        "doc_sop": " ".join(
            [
                SOP_LIMIT_QUOTE,
                SOP_EQUIPMENT_QUOTE,
                SOP_QA_QUOTE,
                SOP_TRAINING_QUOTE,
            ]
        ),
        "doc_validation": " ".join(
            [
                EQUIPMENT_QUOTE,
                VALIDATION_LIMIT_QUOTE,
                VALIDATION_PACKAGE_QUOTE,
                VALIDATION_TRANSFER_QUOTE,
            ]
        ),
        "doc_risk_assessment": "Vergleichslabordaten akzeptiert; keine separate Bridge",
        "doc_change_qa": "QA-QC Reviewer: pending",
        "doc_execution_qa": QA_EXECUTION_QUOTE,
        "doc_change_training": TRAINING_CHANGE_QUOTE,
        "doc_execution_training": EXECUTION_TRAINING_QUOTE,
        "doc_change_scope": SCOPE_CHANGE_QUOTE,
        "doc_execution_scope": f"{EXECUTION_RETEST_QUOTE} A17-26044 Retest",
    }
    for document_id, text in source_texts.items():
        _add_document_with_chunk(document_id=document_id, text=text)


def _add_gold_evidence_documents(evidence_refs: list[object]) -> None:
    quotes_by_document: dict[str, list[str]] = {}
    for reference in evidence_refs:
        assert isinstance(reference, dict)
        document_id = _gold_document_id(str(reference["document_id"]))
        quotes_by_document.setdefault(document_id, []).append(str(reference["quote"]))
    for document_id, quotes in quotes_by_document.items():
        _add_document_with_chunk(document_id=document_id, text="\n".join(quotes))


def _add_gold_fixture_documents(evidence_refs: list[object]) -> None:
    fixture_root = Path(__file__).parent / "fixtures" / "pkg001"
    source_document_ids = {
        str(reference["document_id"])
        for reference in evidence_refs
        if isinstance(reference, dict)
    }
    for source_document_id in source_document_ids:
        text = (fixture_root / PKG001_SOURCE_FILES[source_document_id]).read_text(
            encoding="utf-8"
        )
        _add_document_with_chunk(
            document_id=_gold_document_id(source_document_id),
            text=text,
        )


def _gold_document_id(source_document_id: str) -> str:
    return "doc_pkg001_" + source_document_id.lower().replace("-", "_")


def _add_document_with_chunk(*, document_id: str, text: str) -> None:
    chunk_id = f"chunk_{document_id.removeprefix('doc_')}_p1"
    repository.add_document(
        document=Document(
            document_id=document_id,
            document_set_id="ds_verifier_demo",
            filename=f"{document_id}.txt",
            file_hash_sha256=sha256(document_id.encode()).hexdigest(),
            mime_type="text/plain",
            page_count=1,
            storage_uri=f"local://verifier/{document_id}.txt",
            parser_version="test-parser",
            parsing_status="parsed",
            parsing_quality_score=0.95,
            language="en",
            metadata={},
        ),
        chunks=[
            DocumentChunk(
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
        ],
    )


def _multi_document_finding(
    *,
    risk_statement: str,
    evidence: list[tuple[str, str]],
    support_types: list[str] | None = None,
    requirement_references: list[str] | None = None,
    missing_information: list[str] | None = None,
) -> RiskFinding:
    return RiskFinding(
        finding_id="finding_multi_document",
        document_set_id="ds_verifier_demo",
        risk_category="change_control",
        severity="high",
        likelihood=3,
        detectability=3,
        risk_statement=risk_statement,
        evidence_items=[
            {
                "document_id": document_id,
                "chunk_id": f"chunk_{document_id.removeprefix('doc_')}_p1",
                "page": 1,
                "quote": quote,
                "quote_hash": sha256(quote.encode()).hexdigest(),
                "support_type": (support_types or ["supports"] * len(evidence))[index],
                "verifier_score": 0.95,
            }
            for index, (document_id, quote) in enumerate(evidence)
        ],
        requirement_references=requirement_references
        or ["req_deviation_documented_impact_assessment"],
        missing_information=missing_information or [],
        model_provider="mock",
        model_name="mock-reviewer",
        model_version="0.1.0",
        prompt_version="multi_document_reviewer_v1",
        evidence_support="partial",
        recommended_action="Route to QA/SME for review.",
        auto_close_allowed=False,
        status="needs_human_review",
    )
