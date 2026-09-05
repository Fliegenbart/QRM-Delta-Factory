"""A trickling server must not hold a provider call forever.

httpx's read timeout is per received chunk; a gateway that keeps the
connection open and dribbles bytes resets it endlessly. One such connection
held the blind3 benchmark on a single requirement for eleven hours.
"""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator

import pytest

from app.agents.providers import BaseModelProvider, ProviderCallError
from app.agents.providers.base import ProviderRuntimeOptions
from app.agents.providers.openai_provider import OpenAIProvider
from app.core.config import get_settings
from app.schemas.requirement_review import EntailmentCheck


@pytest.fixture()
def trickling_server() -> Iterator[int]:
    """An HTTP 'server' that answers headers, then dribbles one byte per 100ms."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    stop = threading.Event()

    def _serve() -> None:
        try:
            connection, _addr = server.accept()
        except OSError:
            return
        with connection:
            connection.recv(65536)
            connection.sendall(
                b"HTTP/1.1 200 OK\r\ncontent-type: application/json\r\n"
                b"content-length: 100000\r\n\r\n"
            )
            while not stop.is_set():
                try:
                    connection.sendall(b" ")
                except OSError:
                    return
                time.sleep(0.1)

    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        stop.set()
        server.close()


def test_trickling_response_hits_the_hard_deadline(
    monkeypatch: pytest.MonkeyPatch, trickling_server: int
) -> None:
    monkeypatch.setenv("QRM_EXTERNAL_MODEL_CALLS_ENABLED", "true")
    monkeypatch.setenv("QRM_ALLOWED_MODEL_PROVIDERS", "openai")
    monkeypatch.setenv("QRM_OPENAI_API_KEY", "test-key")
    get_settings.cache_clear()

    provider = OpenAIProvider(
        configured_model_id="gpt-5.4",
        runtime_options=ProviderRuntimeOptions(
            timeout_seconds=0.4,
            max_retries=0,
            retry_deadline_seconds=30.0,
            max_concurrent_calls=2,
            circuit_breaker_failure_threshold=99,
            circuit_breaker_cooldown_seconds=1.0,
        ),
    )
    provider.endpoint = f"http://127.0.0.1:{trickling_server}/v1/chat/completions"

    started = time.monotonic()
    try:
        with pytest.raises(ProviderCallError) as failure:
            provider.run_structured(
                prompt="p", input_schema={}, output_schema=EntailmentCheck
            )
    finally:
        get_settings.cache_clear()
        BaseModelProvider._provider_failure_counts.clear()
        BaseModelProvider._provider_opened_at.clear()

    elapsed = time.monotonic() - started
    # 0.4s per-read timeout never fires (a byte lands every 0.1s); the hard
    # deadline (0.4*1.25+15 ≈ 15.5s) must. Generous margin for slow CI.
    assert elapsed < 25.0
    assert "hard deadline" in str(failure.value)
    assert failure.value.retryable is True
