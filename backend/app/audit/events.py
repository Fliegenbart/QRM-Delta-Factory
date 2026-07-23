from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from threading import RLock
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import get_settings
from app.core.redaction import redact_log_metadata
from app.db.in_memory import _engine_options_for_database_url, _normalize_database_url

SHA256_EMPTY = sha256(b"").hexdigest()


class ActorType(StrEnum):
    USER = "user"
    SYSTEM = "system"
    MODEL = "model"
    SERVICE = "service"


class AuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audit_event_id: str
    tenant_id: str = Field(min_length=1)
    actor_type: ActorType
    actor_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    entity_type: str = Field(min_length=1)
    entity_id: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    input_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    output_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    metadata: dict[str, Any] = Field(default_factory=dict)
    previous_event_hash: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    event_hash: str = Field(pattern=r"^[a-f0-9]{64}$")

    @property
    def event_id(self) -> str:
        return self.audit_event_id

    @property
    def occurred_at(self) -> datetime:
        return self.timestamp

    @property
    def payload(self) -> dict[str, Any]:
        return self.metadata


class AuditService:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def append_event(
        self,
        *,
        tenant_id: str,
        actor_type: ActorType | str,
        actor_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        input_hash: str | None = None,
        output_hash: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        sanitized_metadata = redact_log_metadata(metadata or {})
        previous_event_hash = self._events[-1].event_hash if self._events else None
        audit_event_id = f"audit_{len(self._events) + 1}"
        timestamp = datetime.now(UTC)
        resolved_input_hash = input_hash or _hash_json(
            {
                "event_type": event_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "metadata": sanitized_metadata,
            }
        )
        resolved_output_hash = output_hash or _hash_json(
            {
                "audit_event_id": audit_event_id,
                "event_type": event_type,
                "metadata_summary": _metadata_summary(sanitized_metadata),
            }
        )
        resolved_actor_type = ActorType(actor_type)
        base_payload = _event_hash_payload(
            audit_event_id=audit_event_id,
            tenant_id=tenant_id,
            actor_type=resolved_actor_type,
            actor_id=actor_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            timestamp=timestamp,
            input_hash=resolved_input_hash,
            output_hash=resolved_output_hash,
            metadata=sanitized_metadata,
            previous_event_hash=previous_event_hash,
        )
        event = AuditEvent(
            audit_event_id=audit_event_id,
            tenant_id=tenant_id,
            actor_type=resolved_actor_type,
            actor_id=actor_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            timestamp=timestamp,
            input_hash=resolved_input_hash,
            output_hash=resolved_output_hash,
            metadata=sanitized_metadata,
            previous_event_hash=previous_event_hash,
            event_hash=_hash_json(base_payload),
        )
        self._events.append(event)
        return event

    def append(
        self,
        *,
        event_type: str,
        actor_id: str,
        entity_type: str,
        entity_id: str,
        payload: dict[str, Any] | None = None,
        actor_type: ActorType | str | None = None,
        tenant_id: str | None = None,
        input_hash: str | None = None,
        output_hash: str | None = None,
    ) -> AuditEvent:
        metadata = payload or {}
        return self.append_event(
            tenant_id=tenant_id or str(metadata.get("tenant_id", "tenant_unknown")),
            actor_type=actor_type or _infer_actor_type(actor_id),
            actor_id=actor_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            input_hash=input_hash,
            output_hash=output_hash,
            metadata=metadata,
        )

    def get_events_for_entity(self, entity_type: str, entity_id: str) -> list[AuditEvent]:
        return [
            event
            for event in self._events
            if event.entity_type == entity_type and event.entity_id == entity_id
        ]

    def verify_hash_chain(self) -> bool:
        previous_hash: str | None = None
        for event in self._events:
            if event.previous_event_hash != previous_hash:
                return False
            if _event_hash(event) != event.event_hash:
                return False
            previous_hash = event.event_hash
        return True

    def list_events(self) -> list[AuditEvent]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()


class PersistentAuditService(AuditService):
    """Append-only audit log that survives application restarts.

    The in-memory parent remains useful for deterministic unit tests. Production uses
    this implementation whenever repository persistence is enabled.
    """

    def __init__(self, *, database_url: str) -> None:
        super().__init__()
        normalized_database_url = _normalize_database_url(database_url)
        self._engine: Engine = create_engine(
            normalized_database_url,
            future=True,
            **_engine_options_for_database_url(normalized_database_url),
        )
        self._lock = RLock()
        self._create_table()
        self._refresh()

    def append_event(
        self,
        *,
        tenant_id: str,
        actor_type: ActorType | str,
        actor_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        input_hash: str | None = None,
        output_hash: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        with self._lock:
            self._refresh()
            event = super().append_event(
                tenant_id=tenant_id,
                actor_type=actor_type,
                actor_id=actor_id,
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                input_hash=input_hash,
                output_hash=output_hash,
                metadata=metadata,
            )
            try:
                with self._engine.begin() as connection:
                    connection.execute(
                        text(
                            """
                            INSERT INTO qrm_audit_events (event_order, audit_event_id, payload)
                            VALUES (:event_order, :audit_event_id, :payload)
                            """
                        ),
                        {
                            "event_order": len(self._events),
                            "audit_event_id": event.audit_event_id,
                            "payload": event.model_dump_json(),
                        },
                    )
            except Exception:
                self._refresh()
                raise
            return event

    def clear(self) -> None:
        with self._lock:
            with self._engine.begin() as connection:
                connection.execute(text("DELETE FROM qrm_audit_events"))
            self._events.clear()

    def _create_table(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS qrm_audit_events (
                        event_order INTEGER PRIMARY KEY,
                        audit_event_id VARCHAR(128) NOT NULL UNIQUE,
                        payload TEXT NOT NULL
                    )
                    """
                )
            )

    def _refresh(self) -> None:
        with self._engine.begin() as connection:
            rows = connection.execute(
                text("SELECT payload FROM qrm_audit_events ORDER BY event_order ASC")
            ).all()
        self._events = [AuditEvent.model_validate(json.loads(str(row.payload))) for row in rows]


InMemoryAuditLog = AuditService


def _event_hash(event: AuditEvent) -> str:
    return _hash_json(
        _event_hash_payload(
            audit_event_id=event.audit_event_id,
            tenant_id=event.tenant_id,
            actor_type=event.actor_type,
            actor_id=event.actor_id,
            event_type=event.event_type,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            timestamp=event.timestamp,
            input_hash=event.input_hash,
            output_hash=event.output_hash,
            metadata=event.metadata,
            previous_event_hash=event.previous_event_hash,
        )
    )


def _infer_actor_type(actor_id: str) -> ActorType:
    if actor_id.startswith("reviewer_") or (
        actor_id.startswith("user_") and actor_id != "user_system"
    ):
        return ActorType.USER
    if actor_id.startswith("model_"):
        return ActorType.MODEL
    if actor_id.startswith("service_"):
        return ActorType.SERVICE
    return ActorType.SYSTEM


def _metadata_summary(metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "keys": sorted(metadata),
        "size": len(metadata),
    }


def _hash_json(payload: dict[str, Any]) -> str:
    import json

    return sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def _event_hash_payload(
    *,
    audit_event_id: str,
    tenant_id: str,
    actor_type: ActorType,
    actor_id: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    timestamp: datetime,
    input_hash: str,
    output_hash: str,
    metadata: dict[str, Any],
    previous_event_hash: str | None,
) -> dict[str, Any]:
    return {
        "audit_event_id": audit_event_id,
        "tenant_id": tenant_id,
        "actor_type": actor_type.value,
        "actor_id": actor_id,
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "timestamp": timestamp.isoformat(),
        "input_hash": input_hash,
        "output_hash": output_hash,
        "metadata": metadata,
        "previous_event_hash": previous_event_hash,
    }


def _build_audit_log() -> AuditService:
    settings = get_settings()
    if settings.audit_log_enabled and settings.persistence_enabled:
        return PersistentAuditService(database_url=settings.database_url)
    return AuditService()


audit_log = _build_audit_log()
