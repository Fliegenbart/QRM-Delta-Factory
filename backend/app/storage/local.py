from __future__ import annotations

from pathlib import Path
from typing import Protocol


class StorageBackend(Protocol):
    def put_object(self, *, key: str, content: bytes) -> str:
        ...

    def read_object(self, *, uri: str) -> bytes:
        ...


class LocalFilesystemStorage:
    """S3-like local storage used for tests and local development."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def put_object(self, *, key: str, content: bytes) -> str:
        clean_key = key.lstrip("/")
        path = self.root / clean_key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return f"local://{clean_key}"

    def read_object(self, *, uri: str) -> bytes:
        if not uri.startswith("local://"):
            raise ValueError("LocalFilesystemStorage only supports local:// URIs")
        key = uri.removeprefix("local://")
        return (self.root / key).read_bytes()
