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
    allowed_model_providers: str = Field(default="mock")
    allowed_network_domains: str = Field(default="")
    openai_model_id: str = Field(default="")
    anthropic_model_id: str = Field(default="")
    gemini_model_id: str = Field(default="")
    model_provider_timeout_seconds: float = Field(default=30.0, gt=0)
    model_provider_max_retries: int = Field(default=0, ge=0)
    model_provider_circuit_breaker_threshold: int = Field(default=3, gt=0)

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
