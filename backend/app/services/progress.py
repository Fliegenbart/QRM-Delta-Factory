"""In-process progress details for running pipelines.

The pipeline persists which step a run is on; what happens inside the long
step -- "Anforderung 12 von 26 beurteilt" -- changes every few seconds and
would write a full repository snapshot each time if it went through the
repository. It lives here instead, keyed by document set, and is merged into
the run when it is read. One uvicorn worker executes the background task and
answers the poll, so the dictionary is the whole truth; it is empty after a
restart, which is exactly when a run is no longer progressing.
"""

from __future__ import annotations

from collections.abc import Callable
from threading import Lock

_lock = Lock()
_details: dict[str, str] = {}


def report(document_set_id: str, detail: str) -> None:
    with _lock:
        _details[document_set_id] = detail


def detail_for(document_set_id: str) -> str | None:
    with _lock:
        return _details.get(document_set_id)


def clear(document_set_id: str) -> None:
    with _lock:
        _details.pop(document_set_id, None)


def reporter(document_set_id: str) -> Callable[[str], None]:
    return lambda detail: report(document_set_id, detail)
