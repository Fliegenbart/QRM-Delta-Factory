"""Deterministic completeness check for absence-type findings.

The claim ledger only contains what the documents *state*. Missing mandatory
records (an undefined effectiveness check, an undocumented QA approval, a CAPA
without a responsible party) therefore never surface as claims and are
systematically invisible to the reviewer agents. This module closes that gap
requirement-driven and without any model call:

For every requirement that applies to the document set, each required-evidence
entry is mapped to an evidence concept. A concept only *fires* when its trigger
context is present in the claim ledger (a CAPA requirement only applies when
CAPA claims exist) and no presence signal (claim type or keyword) is found.
Unknown evidence strings are skipped conservatively - no finding is better
than a false alarm.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.schemas.domain import Claim, ClaimType, Requirement


@dataclass(frozen=True)
class EvidenceConcept:
    concept_id: str
    # Natural German label, used verbatim in the finding statement.
    label_de: str
    # Keywords that map a requirement.required_evidence string to this concept.
    evidence_string_keywords: tuple[str, ...]
    # Presence signals: any matching claim counts as "evidence exists".
    presence_claim_types: tuple[ClaimType, ...]
    presence_keywords: tuple[str, ...]
    # Trigger context: the concept only applies when this topic is present.
    trigger_claim_types: tuple[ClaimType, ...]
    trigger_keywords: tuple[str, ...]


EVIDENCE_CONCEPTS: tuple[EvidenceConcept, ...] = (
    EvidenceConcept(
        concept_id="effectiveness_check",
        label_de=(
            "Definition oder Durchfuehrung einer Wirksamkeitspruefung"
            " (Effectiveness Check) im CAPA-Plan"
        ),
        evidence_string_keywords=("effectiveness", "wirksamkeit"),
        presence_claim_types=(ClaimType.EFFECTIVENESS_CHECK,),
        presence_keywords=(
            "effectiveness check",
            "wirksamkeitspruefung",
            "wirksamkeitsprüfung",
            "wirksamkeitskontrolle",
            "wirksamkeitsnachweis",
        ),
        trigger_claim_types=(ClaimType.CAPA_ACTION,),
        trigger_keywords=("capa",),
    ),
    EvidenceConcept(
        concept_id="qa_approval",
        label_de="QA-Freigabe bzw. dokumentierte Genehmigung durch die Qualitaetssicherung",
        evidence_string_keywords=("qa approval", "qa-freigabe", "approval record", "qa review"),
        presence_claim_types=(ClaimType.QA_APPROVAL,),
        presence_keywords=(
            "qa-freigabe",
            "qa approval",
            "freigegeben durch",
            "genehmigt durch",
            "qualitaetssicherung",
            "qualitätssicherung",
        ),
        trigger_claim_types=(ClaimType.DEVIATION_DESCRIPTION, ClaimType.CAPA_ACTION),
        trigger_keywords=("abweichung", "deviation", "capa", "change"),
    ),
    EvidenceConcept(
        concept_id="responsible_party",
        label_de="benannter Massnahmenverantwortlicher fuer die CAPA",
        evidence_string_keywords=("verantwortlich", "responsible"),
        presence_claim_types=(ClaimType.RESPONSIBLE_PARTY,),
        presence_keywords=(
            "verantwortlich",
            "responsible",
            "assigned to",
            "zustaendig",
            "zuständig",
        ),
        trigger_claim_types=(ClaimType.CAPA_ACTION,),
        trigger_keywords=("capa", "massnahme", "maßnahme"),
    ),
    EvidenceConcept(
        concept_id="impact_assessment",
        label_de="dokumentierte Bewertung der Auswirkung auf Produktqualitaet und Chargen",
        evidence_string_keywords=("impact", "auswirkung", "chargenliste"),
        presence_claim_types=(ClaimType.IMPACT_ASSESSMENT,),
        presence_keywords=(
            "impact assessment",
            "auswirkungsbewertung",
            "einfluss auf die produktqualitaet",
            "einfluss auf die produktqualität",
            "bewertung der auswirkung",
        ),
        trigger_claim_types=(ClaimType.DEVIATION_DESCRIPTION,),
        trigger_keywords=("abweichung", "deviation"),
    ),
)


@dataclass(frozen=True)
class MissingEvidenceFinding:
    requirement: Requirement
    required_evidence: str
    concept: EvidenceConcept
    anchor_claim: Claim
    statement: str
    missing_information: list[str]


def find_missing_required_evidence(
    requirements: Sequence[Requirement],
    claims: Sequence[Claim],
) -> list[MissingEvidenceFinding]:
    results: list[MissingEvidenceFinding] = []
    seen_concepts: set[str] = set()
    for requirement in requirements:
        for evidence in requirement.required_evidence:
            concept = _concept_for_evidence_string(evidence)
            if concept is None or concept.concept_id in seen_concepts:
                continue
            if not _is_triggered(concept, claims):
                continue
            if _is_present(concept, claims):
                continue
            anchor = _anchor_claim(concept, claims)
            if anchor is None:
                continue
            seen_concepts.add(concept.concept_id)
            statement = (
                f"Pflichtnachweis fehlt: {requirement.source_name}"
                f" Abschnitt {requirement.section} fordert '{evidence}'."
                f" Die Unterlagen enthalten keine(n) {concept.label_de} -"
                " im Claim Ledger existiert kein entsprechender Nachweis-Claim,"
                " obwohl der ausloesende Vorgang dokumentiert ist."
            )
            results.append(
                MissingEvidenceFinding(
                    requirement=requirement,
                    required_evidence=evidence,
                    concept=concept,
                    anchor_claim=anchor,
                    statement=statement,
                    missing_information=[
                        f"Keine dokumentierte {concept.label_de} in den Unterlagen enthalten"
                        f" (gefordert: {evidence})"
                    ],
                )
            )
    return results


def _concept_for_evidence_string(evidence: str) -> EvidenceConcept | None:
    normalized = evidence.lower()
    for concept in EVIDENCE_CONCEPTS:
        if any(keyword in normalized for keyword in concept.evidence_string_keywords):
            return concept
    return None


def _claim_text(claim: Claim) -> str:
    return " ".join(
        [
            claim.normalized_subject,
            claim.normalized_predicate,
            claim.normalized_object,
            claim.raw_text_quote,
        ]
    ).lower()


def _is_triggered(concept: EvidenceConcept, claims: Sequence[Claim]) -> bool:
    match = _matching_claim(claims, concept.trigger_claim_types, concept.trigger_keywords)
    return match is not None


def _is_present(concept: EvidenceConcept, claims: Sequence[Claim]) -> bool:
    return (
        _matching_claim(claims, concept.presence_claim_types, concept.presence_keywords)
        is not None
    )


def _anchor_claim(concept: EvidenceConcept, claims: Sequence[Claim]) -> Claim | None:
    return _matching_claim(claims, concept.trigger_claim_types, concept.trigger_keywords)


def _matching_claim(
    claims: Sequence[Claim],
    claim_types: tuple[ClaimType, ...],
    keywords: tuple[str, ...],
) -> Claim | None:
    for claim in claims:
        if claim.claim_type in claim_types:
            return claim
    for claim in claims:
        text = _claim_text(claim)
        if any(keyword in text for keyword in keywords):
            return claim
    return None
