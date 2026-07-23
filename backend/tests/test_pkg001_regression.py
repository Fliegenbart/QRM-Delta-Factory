from __future__ import annotations

from pathlib import Path

from app.evals.run_goldstandard import _package_document_paths, _wait_for_pipeline_completion


def test_pkg001_upload_manifest_excludes_oracle_and_answer_keys(tmp_path: Path) -> None:
    package_dir = tmp_path / "PKG-001"
    package_dir.mkdir()
    for name in [
        "change_control.md",
        "validation_or_test_evidence.md",
        "GOLD_STANDARD.json",
        "hidden_errors_answer_key.json",
    ]:
        (package_dir / name).write_text("fixture", encoding="utf-8")

    assert [path.name for path in _package_document_paths(package_dir)] == [
        "change_control.md",
        "validation_or_test_evidence.md",
    ]


def test_harness_polls_202_pipeline_run_until_terminal() -> None:
    client = _PipelineClient(
        get_payloads=[
            {"status": "running"},
            {"status": "needs_human_review", "model_manifest": []},
        ]
    )

    completed = _wait_for_pipeline_completion(
        client,
        {"pipeline_run_id": "prun_pkg001", "status": "running"},
        poll_interval_seconds=0,
        timeout_seconds=1,
    )

    assert completed["status"] == "needs_human_review"
    assert client.requested_paths == [
        "/pipeline-runs/prun_pkg001",
        "/pipeline-runs/prun_pkg001",
    ]


class _PipelineResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.status_code = 200
        self._payload = payload
        self.text = ""

    def json(self) -> dict[str, object]:
        return self._payload


class _PipelineClient:
    def __init__(self, *, get_payloads: list[dict[str, object]]) -> None:
        self.get_payloads = get_payloads
        self.requested_paths: list[str] = []

    def get(self, path: str) -> _PipelineResponse:
        self.requested_paths.append(path)
        return _PipelineResponse(self.get_payloads.pop(0))
