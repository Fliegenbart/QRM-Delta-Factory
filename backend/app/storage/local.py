from __future__ import annotations

from pathlib import Path
from typing import Protocol


class StorageBackend(Protocol):
    def put_object(self, *, key: str, content: bytes) -> str:
        ...

    def read_object(self, *, uri: str) -> bytes:
        ...

    def delete_object(self, *, uri: str) -> None:
        ...


class LocalFilesystemStorage:
    """S3-like local storage used for tests and local development."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def put_object(self, *, key: str, content: bytes) -> str:
        clean_key, path = self._safe_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return f"local://{clean_key}"

    def read_object(self, *, uri: str) -> bytes:
        _, path = self._path_for_uri(uri)
        return path.read_bytes()

    def delete_object(self, *, uri: str) -> None:
        _, path = self._path_for_uri(uri)
        path.unlink(missing_ok=True)

    def _path_for_uri(self, uri: str) -> tuple[str, Path]:
        if not uri.startswith("local://"):
            raise ValueError("LocalFilesystemStorage only supports local:// URIs")
        key = uri.removeprefix("local://")
        return self._safe_path(key)

    def _safe_path(self, key: str) -> tuple[str, Path]:
        clean_key = key.lstrip("/")
        path = (self.root / clean_key).resolve()
        try:
            path.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("Storage key resolves outside local storage root") from exc
        return clean_key, path
