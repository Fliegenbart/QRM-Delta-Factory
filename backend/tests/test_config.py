from pytest import MonkeyPatch

from app.core.config import Settings


def test_config_loads_safe_defaults() -> None:
    settings = Settings()

    assert settings.app_name == "Pharma AI Risk Orchestration Backend"
    assert settings.environment == "local"
    assert settings.allow_model_live_internet is False
    assert "postgresql+psycopg://" in settings.database_url
    assert settings.redis_url.startswith("redis://")


def test_config_accepts_environment_override(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("QRM_ENVIRONMENT", "test")
    monkeypatch.setenv("QRM_APP_VERSION", "9.9.9-test")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.app_version == "9.9.9-test"
