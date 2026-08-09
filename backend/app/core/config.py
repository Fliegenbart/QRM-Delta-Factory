import os
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "test", "staging", "production"]


def _default_local_storage_root() -> str:
    if os.getenv("VERCEL"):
        return "/tmp/qrm-local-storage"
    return "./.local-storage"


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Values are intentionally non-secret local defaults. Real deployments should inject
    environment-specific secrets through the platform secret manager.
    """

    model_config = SettingsConfigDict(
        env_prefix="QRM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Pharma AI Risk Orchestration Backend")
    app_version: str = Field(default="0.1.0")
    environment: EnvironmentName = Field(default="local")
    database_url: str = Field(
        default="postgresql+psycopg://qrm_app:qrm_app_dev@postgres:5432/qrm_orchestration"
    )
    redis_url: str = Field(default="redis://redis:6379/0")
    local_storage_root: str = Field(default_factory=_default_local_storage_root)
    parsing_quality_threshold: float = Field(default=0.65, ge=0, le=1)
    ood_score_threshold: float = Field(default=0.5, ge=0, le=1)
    supported_document_languages: str = Field(default="en")
    minimum_claim_count: int = Field(default=1, ge=0)
    unclear_claim_ratio_threshold: float = Field(default=0.4, ge=0, le=1)
    audit_log_enabled: bool = Field(default=True)
    allow_model_live_internet: bool = Field(default=False)
    api_keys: str = Field(
        default="",
        description="Comma-separated tenant_id=api-key pairs for MVP API-key auth.",
    )
    persistence_enabled: bool = Field(default=False)
    external_model_calls_enabled: bool = Field(default=False)
    llm_claim_extraction_enabled: bool = Field(
        default=False,
        description=(
            "Use a model for preliminary claim extraction. Keep this disabled in "
            "production so source indexing remains deterministic and bounded; the "
            "primary review can still use the configured model provider."
        ),
    )
    allowed_model_providers: str = Field(default="mock")
    allowed_network_domains: str = Field(default="")
    openai_model_id: str = Field(default="")
    anthropic_model_id: str = Field(default="")
    gemini_model_id: str = Field(default="")
    mistral_model_id: str = Field(default="")
    reviewer_provider_override: str = Field(
        default="",
        description="Force a single provider for all reviewer agents and claim extraction"
        " (e.g. 'mistral' for an EU-only stack). Empty keeps the per-role default mix.",
    )
    requirement_review_assessor_provider: str = Field(
        default="mistral",
        description="Provider for the requirement-centric review path's assessor calls."
        " Mistral by default: it carried 31 of 34 credited detections on the held-out"
        " corpus and is the cheapest of the three.",
    )
    requirement_review_entailment_provider: str = Field(
        default="anthropic",
        description="Provider for the requirement path's entailment verification."
        " Deliberately a different provider than the assessor, so the checker does"
        " not share the assessor's blind spots.",
    )
    requirement_review_enabled: bool = Field(
        default=True,
        description="Run the requirement-centric coverage review as part of the"
        " pipeline. It answers the question a QA reviewer actually asks -- is every"
        " obligation met, and where is the proof -- and publishes one verdict per"
        " requirement instead of a findings feed. Additive: the finding pack is"
        " produced either way, and a failing coverage review never fails the run.",
    )
    requirement_review_assessor_samples: int = Field(
        default=2,
        ge=1,
        le=3,
        description="Independent assessor samples per requirement group, merged by"
        " alarm-side precedence. Nine of 34 planted errors flipped between two"
        " single-sample runs on identical inputs; the union stood at 30. Set 1 to"
        " restore single-sample behaviour.",
    )
    critic_providers: str = Field(
        default="",
        description="Comma-separated providers that run an additional broad-scope red-team"
        " critic agent each (e.g. 'anthropic,openai'). Critics keep their own provider even"
        " when reviewer_provider_override is set.",
    )
    model_provider_timeout_seconds: float = Field(default=30.0, gt=0)
    # A transient 429 or 502 previously failed the reviewer role outright, which
    # fail-secure turns into a blocked auto-clear for the whole case. Retrying is
    # bounded by model_provider_retry_deadline_seconds and the shared circuit
    # breaker, so two attempts cannot extend a run beyond the pipeline lease.
    model_provider_max_retries: int = Field(default=2, ge=0)
    # The deadline caps the whole retry loop, so it has to fit several single
    # attempts plus backoff. At 120s with a 240s per-call timeout a slow first
    # attempt could never be retried at all -- two entailment calls died exactly
    # that way in the 2026-07-27 held-out run. 600s covers two full attempts at
    # the 240s production timeout with backoff to spare.
    model_provider_retry_deadline_seconds: float = Field(default=600.0, gt=0)
    model_provider_max_concurrency: int = Field(default=2, gt=0)
    # Reviewers emit JSON with a finding list and verbatim evidence quotes, so a
    # cut-off response is not a shorter answer but a dead role: the provider
    # raises "output was truncated" and the agent produces nothing. The last
    # healthy run averaged 2,814 output tokens per Mistral call and 6,502 per
    # Anthropic call, so a 1,600 cap truncated nearly every reviewer.
    model_provider_max_output_tokens: int = Field(default=8192, ge=256, le=8192)
    model_provider_circuit_breaker_threshold: int = Field(default=3, gt=0)
    # How long an open breaker stays open before one probe call is admitted.
    model_provider_circuit_breaker_cooldown_seconds: float = Field(default=60.0, gt=0)
    reviewer_max_claims_per_agent: int = Field(default=20, ge=8, le=200)
    reviewer_max_source_excerpts_per_agent: int = Field(default=8, ge=1, le=40)
    reviewer_max_source_excerpt_chars: int = Field(default=1200, ge=100, le=10000)
    reviewer_max_source_context_chars: int = Field(default=6000, ge=512, le=40000)
    # Where the calibration regression gate looks for eval fixtures. Point this
    # at a corpus produced by real pipeline runs to make the gate meaningful;
    # the checked-in examples are prerecorded and cannot pass it.
    eval_fixture_dir: str = Field(default="examples/evals")
    pipeline_run_lease_seconds: int = Field(default=900, gt=0)
    retain_raw_model_outputs: bool = Field(default=False)
    max_upload_bytes: int = Field(default=20 * 1024 * 1024, gt=0)

    def api_key_to_tenant_id(self) -> dict[str, str]:
        key_map: dict[str, str] = {}
        for entry in _split_csv(self.api_keys):
            separator = "=" if "=" in entry else ":"
            if separator not in entry:
                continue
            tenant_id, api_key = [part.strip() for part in entry.split(separator, 1)]
            if tenant_id and api_key:
                key_map[api_key] = tenant_id
        return key_map

    def allowed_model_provider_set(self) -> set[str]:
        return set(_split_csv(self.allowed_model_providers))

    def allowed_network_domain_set(self) -> set[str]:
        return set(_split_csv(self.allowed_network_domains))

    def supported_document_language_set(self) -> set[str]:
        return set(_split_csv(self.supported_document_languages))


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
