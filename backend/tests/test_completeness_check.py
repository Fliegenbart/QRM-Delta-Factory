from __future__ import annotations

from hashlib import sha256

from app.schemas.domain import Claim, ClaimType, Requirement
from app.services.completeness_check import find_missing_required_evidence


def _claim(claim_type: ClaimType, quote: str, claim_id_suffix: str) -> Claim:
    return Claim(
        claim_id=f"claim_{sha256(claim_id_suffix.encode()).hexdigest()[:20]}",
        document_id="doc_test",
        chunk_id="chunk_test_p1",
        page=1,
        claim_type=claim_type,
        normalized_subject="subject",
        normalized_predicate="states",
        normalized_object="object",
        raw_text_quote=quote,
        confidence=0.9,
        dependencies=[],
        created_by_model="test",
        prompt_version="test-v1",
    )


def _capa_requirement() -> Requirement:
    return Requirement(
        requirement_id="req_test_capa_effectiveness",
        source_type="internal_sop",
        source_name="SOP-CAPA-003 CAPA Management",
        source_version="1.0",
        section="7.5",
        requirement_text=(
            "CAPA-Massnahmen duerfen nur mit dokumentierter Wirksamkeitspruefung"
            " abgeschlossen werden."
        ),
        applies_to_document_types=["deviation", "capa"],
        applies_to_process_areas=["drug_product_manufacturing"],
        criticality="high",
        required_evidence=["CAPA Record", "Effectiveness Check Nachweis"],
        auto_close_allowed=False,
        effective_from="2026-01-01T00:00:00Z",
        effective_to=None,
    )


def test_missing_effectiveness_check_is_found_when_capa_present() -> None:
    claims = [
        _claim(
            ClaimType.CAPA_ACTION,
            "CAPA-MET-2026-09: Wartungsintervalle werden von 6 auf 3 Monate verkuerzt.",
            "capa",
        ),
    ]

    results = find_missing_required_evidence([_capa_requirement()], claims)

    assert len(results) == 1
    finding = results[0]
    assert finding.concept.concept_id == "effectiveness_check"
    assert finding.anchor_claim.claim_type == ClaimType.CAPA_ACTION
    assert "Wirksamkeitspruefung" in finding.statement
    assert finding.requirement.requirement_id == "req_test_capa_effectiveness"


def test_no_finding_when_effectiveness_check_documented() -> None:
    claims = [
        _claim(ClaimType.CAPA_ACTION, "CAPA-MET-2026-09 wird umgesetzt.", "capa"),
        _claim(
            ClaimType.EFFECTIVENESS_CHECK,
            "Effectiveness Check: Trendauswertung nach 3 Monaten geplant.",
            "check",
        ),
    ]

    assert find_missing_required_evidence([_capa_requirement()], claims) == []


def test_no_finding_when_effectiveness_mentioned_only_in_text() -> None:
    claims = [
        _claim(ClaimType.CAPA_ACTION, "CAPA-MET-2026-09 wird umgesetzt.", "capa"),
        _claim(
            ClaimType.DEVIATION_DESCRIPTION,
            "Die Wirksamkeitspruefung erfolgt nach Abschluss der Massnahme.",
            "text",
        ),
    ]

    assert find_missing_required_evidence([_capa_requirement()], claims) == []


def test_no_finding_without_trigger_context() -> None:
    claims = [
        _claim(
            ClaimType.TEST_RESULT,
            "Test result: Viskositaet innerhalb der Spezifikation.",
            "unrelated",
        ),
    ]

    assert find_missing_required_evidence([_capa_requirement()], claims) == []


def test_unknown_evidence_strings_are_skipped() -> None:
    requirement = _capa_requirement().model_copy(
        update={"required_evidence": ["Rheologisches Gutachten"]}
    )
    claims = [_claim(ClaimType.CAPA_ACTION, "CAPA-1 dokumentiert.", "capa")]

    assert find_missing_required_evidence([requirement], claims) == []


def test_concept_reported_once_across_requirements() -> None:
    requirement_a = _capa_requirement()
    requirement_b = _capa_requirement().model_copy(
        update={"requirement_id": "req_test_capa_effectiveness_b"}
    )
    claims = [_claim(ClaimType.CAPA_ACTION, "CAPA-1 dokumentiert.", "capa")]

    results = find_missing_required_evidence([requirement_a, requirement_b], claims)

    assert len(results) == 1
