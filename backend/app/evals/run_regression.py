from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from app.schemas.evals import RegressionRun
from app.services.regression_gate import RegressionGateService


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    baseline = _load_run(Path(args.baseline))
    candidate = _load_run(Path(args.candidate))
    report = RegressionGateService(
        citation_precision_threshold=args.citation_precision_threshold,
        requirement_match_accuracy_threshold=args.requirement_match_accuracy_threshold,
        max_human_review_rate_increase=args.max_human_review_rate_increase,
    ).compare(baseline=baseline, candidate=candidate)

    if args.markdown_output:
        Path(args.markdown_output).write_text(report.markdown_report, encoding="utf-8")
    if args.json_output:
        Path(args.json_output).write_text(
            json.dumps(report.json_report, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    print(report.markdown_report)
    return 0 if report.passed else 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare baseline and candidate eval runs with the regression gate.",
    )
    parser.add_argument("--baseline", required=True, help="Path to baseline RegressionRun JSON")
    parser.add_argument("--candidate", required=True, help="Path to candidate RegressionRun JSON")
    parser.add_argument(
        "--citation-precision-threshold",
        type=float,
        default=0.9,
        help="Minimum allowed candidate citation precision per dataset.",
    )
    parser.add_argument(
        "--requirement-match-accuracy-threshold",
        type=float,
        default=0.9,
        help="Minimum allowed candidate requirement match accuracy per dataset.",
    )
    parser.add_argument(
        "--max-human-review-rate-increase",
        type=float,
        default=0.25,
        help="Maximum allowed average human review rate increase unless recall improves.",
    )
    parser.add_argument("--markdown-output", help="Optional Markdown report output path")
    parser.add_argument("--json-output", help="Optional JSON report output path")
    return parser


def _load_run(path: Path) -> RegressionRun:
    return RegressionRun.model_validate(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    raise SystemExit(main())
