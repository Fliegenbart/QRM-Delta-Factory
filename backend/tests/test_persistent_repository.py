from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

from app.db.in_memory import _engine_options_for_database_url
from app.db.persistent import PersistentSnapshotRepository
from app.schemas.domain import DocumentSet, RequirementSet


def test_postgres_pooler_engine_options_disable_prepared_statements() -> None:
    options = _engine_options_for_database_url(
        "postgresql://postgres.example:secret@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"
    )

    assert options["connect_args"] == {"prepare_threshold": None}
    assert options["pool_pre_ping"] is True


def test_persistent_repository_restores_snapshot_from_sqlite(tmp_path) -> None:  # type: ignore[no-untyped-def]
    database_url = f"sqlite:///{tmp_path / 'qrm_state.db'}"
    first = PersistentSnapshotRepository(database_url=database_url)
    first.create_requirement_set(_requirement_set())
    first.create_document_set(_document_set())

    second = PersistentSnapshotRepository(database_url=database_url)

    assert second.get_requirement_set("rset_persist_demo") is not None
    assert second.get_document_set("ds_persist_demo") is not None
    assert second.list_document_sets()[0].document_set_id == "ds_persist_demo"


def test_persistent_repository_removes_retired_public_demo_case(tmp_path) -> None:  # type: ignore[no-untyped-def]
    database_url = f"sqlite:///{tmp_path / 'qrm_legacy_demo_state.db'}"
    first = PersistentSnapshotRepository(database_url=database_url)
    first.create_requirement_set(_requirement_set())
    first.create_document_set(_document_set(document_set_id="ds_demo_avi_threshold"))

    second = PersistentSnapshotRepository(database_url=database_url)

    assert second.get_document_set("ds_demo_avi_threshold") is None
    assert second.list_document_sets() == []


def test_persistent_repository_handles_parallel_snapshot_writes(tmp_path) -> None:  # type: ignore[no-untyped-def]
    database_url = f"sqlite:///{tmp_path / 'qrm_parallel_state.db'}"
    repository = PersistentSnapshotRepository(database_url=database_url)
    repository.create_requirement_set(_requirement_set())

    def create_document_set(index: int) -> str:
        document_set = _document_set(
            document_set_id=f"ds_persist_parallel_{index}",
            uploaded_by=f"user_qrm_author_{index}",
        )
        repository.create_document_set(document_set)
        return document_set.document_set_id

    with ThreadPoolExecutor(max_workers=8) as executor:
        document_set_ids = list(executor.map(create_document_set, range(20)))

    restored = PersistentSnapshotRepository(database_url=database_url)

    assert {
        document_set.document_set_id for document_set in restored.list_document_sets()
    }.issuperset(document_set_ids)


def _document_set(
    *,
    document_set_id: str = "ds_persist_demo",
    uploaded_by: str = "user_qrm_author",
) -> DocumentSet:
    return DocumentSet(
        document_set_id=document_set_id,
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_persist_demo",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="change_control",
        declared_process_area="aseptic_filling",
        uploaded_by=uploaded_by,
        status="uploaded",
    )


def _requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_persist_demo",
        tenant_id="tenant_demo_pharma",
        name="Persistent Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_persist_demo",
                "source_type": "internal_sop",
                "source_name": "SOP-PERSIST",
                "source_version": "1.0",
                "section": "1",
                "requirement_text": "Persistent demo requirement.",
                "applies_to_document_types": ["change_control"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "low",
                "required_evidence": ["demo record"],
                "auto_close_allowed": True,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )
