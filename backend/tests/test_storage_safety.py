from __future__ import annotations

from pathlib import Path

import pytest

from app.storage.local import LocalFilesystemStorage


def test_local_storage_rejects_path_traversal_writes(tmp_path: Path) -> None:
    storage = LocalFilesystemStorage(tmp_path / "storage")

    with pytest.raises(ValueError, match="outside local storage root"):
        storage.put_object(key="../outside.txt", content=b"leak")

    assert not (tmp_path / "outside.txt").exists()


def test_local_storage_rejects_path_traversal_reads(tmp_path: Path) -> None:
    storage = LocalFilesystemStorage(tmp_path / "storage")

    with pytest.raises(ValueError, match="outside local storage root"):
        storage.read_object(uri="local://../outside.txt")
