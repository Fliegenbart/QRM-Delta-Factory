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
from app.services.review_orchestrator import PrimaryReviewOrchestrator, default_reviewer_agents
from tests.test_primary_review_orchestrator import _claims, _document_set, _requirement_set

PROMPT_DIR = Path(__file__).resolve().parents[1] / "app" / "agents" / "prompts"
PROMPT_FILES = [
    "gmp_data_integrity_reviewer_v1.md",
    "deviation_reviewer_v1.md",
    "capa_reviewer_v1.md",
    "batch_impact_reviewer_v1.md",
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
        "Wenn Evidenz fehlt, setze missing_information. Erfinde keine Evidenz.",
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


def test_missing_prompt_template_fails_cleanly(tmp_path: Path) -> None:
    loader = PromptTemplateLoader(prompts_dir=tmp_path)

    with pytest.raises(PromptTemplateNotFoundError):
        loader.load("missing_template_v1.md")


def test_default_agents_load_prompt_versions_from_template_files() -> None:
    agents = default_reviewer_agents()

    assert [agent.prompt_version for agent in agents] == [
        "gmp_data_integrity_reviewer_v1",
        "deviation_reviewer_v1",
        "capa_reviewer_v1",
        "batch_impact_reviewer_v1",
        "regulatory_consistency_reviewer_v1",
        "contradiction_hunter_v1",
    ]
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

    assert result.model_runs[0].prompt_version == "deviation_reviewer_v1"
    model_run_audit = [
        event for event in audit_log.list_events() if event.event_type == "model_run_recorded"
    ][0]
    assert model_run_audit.payload["prompt_version"] == "deviation_reviewer_v1"
