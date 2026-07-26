from __future__ import annotations

from pathlib import Path

import pytest

from app.agents.prompt_templates import (
    REQUIRED_PROMPT_SECTIONS,
    PromptTemplateLoader,
    PromptTemplateNotFoundError,
)
from app.audit.events import audit_log
from app.db.in_memory import repository
from app.services.review_orchestrator import (
    OUTPUT_LANGUAGE_DIRECTIVE,
    REVIEWER_OUTPUT_CONTRACT,
    PrimaryReviewOrchestrator,
    default_reviewer_agents,
)
from tests.test_primary_review_orchestrator import _claims, _document_set, _requirement_set

PROMPT_DIR = Path(__file__).resolve().parents[1] / "app" / "agents" / "prompts"
PROMPT_FILES = [
    "gmp_data_integrity_reviewer_v1.md",
    "deviation_reviewer_v1.md",
    "capa_reviewer_v1.md",
    "batch_impact_reviewer_v1.md",
    "validation_and_sterility_reviewer_v1.md",
    "regulatory_consistency_reviewer_v1.md",
    "contradiction_hunter_v1.md",
]


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()


def test_each_reviewer_prompt_template_contains_required_sections() -> None:
    loader = PromptTemplateLoader(prompts_dir=PROMPT_DIR)

    for file_name in PROMPT_FILES:
        template = loader.load(file_name)
        assert template.version == "v1"
        assert template.prompt_version == file_name.removesuffix(".md")
        for section in REQUIRED_PROMPT_SECTIONS:
            assert f"## {section}" in template.content


def test_each_reviewer_prompt_uses_specialized_pharma_risk_reviewer_contract() -> None:
    loader = PromptTemplateLoader(prompts_dir=PROMPT_DIR)
    required_contract_phrases = [
        "spezialisierter pharmazeutischer Risk Reviewer",
        "Verwende ausschliesslich die bereitgestellten Claims, Chunks und Requirements.",
        "Jedes Finding braucht mindestens ein EvidenceItem",
        "Setze missing_information nur fuer offene Fakten, die im Paket nicht verifizierbar sind.",
        "No issue",
        "Schlechte Dokumentqualitaet, fehlende Anhaenge oder fehlende Requirements",
        "Gib keine narrativen Freitextantworten ausserhalb des JSON-Schemas zurueck.",
        "Critical:",
        "High:",
        "Denke konservativ",
    ]

    for file_name in PROMPT_FILES:
        template = loader.load(file_name)
        for phrase in required_contract_phrases:
            assert phrase in template.content


def test_primary_review_contract_marks_model_output_as_candidates_for_deterministic_publication(
) -> None:
    assert "candidate finding" in REVIEWER_OUTPUT_CONTRACT.lower()
    assert "do not create a finding" in REVIEWER_OUTPUT_CONTRACT.lower()
    assert "evidence or requirement support is missing" in REVIEWER_OUTPUT_CONTRACT.lower()


def test_primary_review_contract_requires_precise_evidence_and_missingness_semantics() -> None:
    contract = REVIEWER_OUTPUT_CONTRACT.lower()

    assert "relation of that quote to the risk statement" in contract
    assert "document-to-document discrepancy" in contract
    assert "distinct source documents" in contract
    assert "non-duplicate exact excerpts" in contract
    assert "identifier, version, or numeric anchor" in contract
    assert "must occur verbatim in at least one attached quote" in contract
    assert "missing_information=[]" in REVIEWER_OUTPUT_CONTRACT
    assert "recommended_action" in REVIEWER_OUTPUT_CONTRACT
    assert "cross-document reviewers must cite the source pair" in contract


def test_missing_prompt_template_fails_cleanly(tmp_path: Path) -> None:
    loader = PromptTemplateLoader(prompts_dir=tmp_path)

    with pytest.raises(PromptTemplateNotFoundError):
        loader.load("missing_template_v1.md")


def test_default_agents_load_prompt_versions_from_template_files() -> None:
    agents = default_reviewer_agents()

    expected_template_versions = [
        "gmp_data_integrity_reviewer_v1",
        "deviation_reviewer_v1",
        "capa_reviewer_v1",
        "batch_impact_reviewer_v1",
        "validation_and_sterility_reviewer_v1",
        "regulatory_consistency_reviewer_v1",
        "contradiction_hunter_v1",
    ]
    assert [
        agent.prompt_version.split("+sha256:", maxsplit=1)[0] for agent in agents
    ] == expected_template_versions
    assert all(
        len(agent.prompt_version.split("+sha256:", maxsplit=1)[1]) == 64
        for agent in agents
    )
    assert all(agent.prompt_template is not None for agent in agents)


def test_prompt_version_is_persisted_in_model_run_and_audit() -> None:
    repository.create_requirement_set(_requirement_set())
    repository.create_document_set(_document_set())
    repository.replace_claim_ledger(document_set_id="ds_review_demo", claims=_claims())

    result = PrimaryReviewOrchestrator(
        repository=repository,
        audit_log=audit_log,
        agents=[default_reviewer_agents()[1]],
    ).run_primary_review("ds_review_demo")

    prompt_version = result.model_runs[0].prompt_version
    assert prompt_version.startswith("deviation_reviewer_v1+sha256:")
    assert len(prompt_version.removeprefix("deviation_reviewer_v1+sha256:")) == 64
    model_run_audit = [
        event for event in audit_log.list_events() if event.event_type == "model_run_recorded"
    ][0]
    assert model_run_audit.payload["prompt_version"] == prompt_version


def test_language_directive_demands_umlauts_over_ascii_substitutes() -> None:
    """The directive has to name the rule, and follow it.

    It previously read "Uebernimm woertliche Zitate unveraendert" -- an instruction
    to write German, written without German orthography. Models follow the register
    of their instructions: every finding from the OpenAI-routed reviewers came back
    with "Fuer", "waehrend" and "gemaess", while Mistral and Anthropic wrote
    correctly. In a review pack sent to a customer that reads as a defect.
    """
    directive = OUTPUT_LANGUAGE_DIRECTIVE
    assert "ä" in directive and "ö" in directive and "ü" in directive and "ß" in directive
    for substitute in ("Uebernimm", "woertliche", "unveraendert", "uebersetze"):
        assert substitute not in directive
    # The surrounding templates still use substitutes, so the rule must say it wins.
    assert "korrekten Umlaute" in directive
    assert "übrigen Anweisungen" in directive


def test_reviewer_prompts_carry_the_umlaut_rule() -> None:
    """Every agent gets the rule, not just the ones that needed it."""
    for agent in default_reviewer_agents():
        prompt = "\n\n".join(
            [agent.prompt_template.content, OUTPUT_LANGUAGE_DIRECTIVE, REVIEWER_OUTPUT_CONTRACT]
        )
        assert "korrekten Umlaute" in prompt, agent.role


def test_server_authored_finding_text_uses_umlauts() -> None:
    """Text the server writes itself has no model to blame.

    The rule layers and the completeness check compose their own German, and it
    reached the pack as "Massnahmenverantwortlicher", "pruefen" and "ausloesende".
    Matching tokens are excluded on purpose: _fold() folds umlauts to ASCII before
    comparing against document text, so those must stay in substitute form.
    """
    from app.services.completeness_check import EVIDENCE_CONCEPTS

    substitutes = ("fuer", "pruef", "massnahm", "ausloes", "qualitaet", "durchfuehr")
    for concept in EVIDENCE_CONCEPTS:
        folded = concept.label_de.lower()
        assert not any(bad in folded for bad in substitutes), concept.concept_id
