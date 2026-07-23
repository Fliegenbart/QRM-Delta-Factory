# Review Quality Sprint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn raw multi-agent output into a concise, evidence-backed QA review pack with measurable gold-standard quality gates and a readable German PDF.

**Architecture:** Preserve raw findings for auditability. Add deterministic root-finding aggregation and publication gates after evidence verification, then build the review pack from canonical root findings while retaining supporting finding IDs and evidence. Keep technical model coverage warnings separate from the human QA decision. Use the PKG-001 oracle only in test/evaluation code after execution has completed.

**Tech Stack:** FastAPI, Pydantic, pytest, Next.js, React, TypeScript, Vitest, browser-generated PDF.

---

### Task 1: Canonical root findings and publication gates

**Files:**
- Modify: `backend/app/services/risk_fusion.py`
- Modify: `backend/app/schemas/risk.py`
- Modify: `backend/tests/test_risk_fusion.py`

- [ ] Write failing tests for merging findings with the same risk theme and overlapping evidence, preserving separate findings with distinct evidence/risk themes, and dropping unsupported non-high findings from the published set.
- [ ] Run `./.venv/bin/python -m pytest tests/test_risk_fusion.py -q` and confirm the new tests fail because root-finding metadata and publication filtering do not exist.
- [ ] Add a deterministic canonical-finding builder that selects one representative per root cluster, unions supporting evidence and requirement IDs, retains source finding IDs, and publishes only evidence/requirement-supported findings. Keep raw repository findings unchanged.
- [ ] Add `published_finding_ids`, canonical cluster metadata, and technical coverage fields to `RiskDecision`.
- [ ] Re-run the focused suite and commit the backend aggregation change.

### Task 2: Human QA decision separated from technical model coverage

**Files:**
- Modify: `backend/app/services/risk_fusion.py`
- Modify: `backend/app/schemas/risk.py`
- Modify: `backend/app/services/pipeline.py`
- Modify: `backend/tests/test_risk_fusion.py`
- Modify: `backend/tests/test_pipeline_runs.py`

- [ ] Write failing tests proving that a failed model run blocks auto-clear and records a technical warning while the visible decision remains `human_review_required` when reviewable evidence exists.
- [ ] Run the focused tests and confirm they fail because model failure is currently the primary decision class.
- [ ] Populate `operational_blockers` and `model_coverage_status`; retain `blocked_due_to_model_failure` only for the no-reviewable-output fallback.
- [ ] Ensure pipeline completion remains `needs_human_review` for technical coverage warnings and never reports a completed automatic clearance.
- [ ] Re-run focused tests and commit the status change.

### Task 3: Review pack and UI are root-risk-first

**Files:**
- Modify: `backend/app/schemas/review_pack.py`
- Modify: `backend/app/services/review_pack.py`
- Modify: `backend/tests/test_review_pack.py`
- Modify: `src/lib/review-ui.ts`
- Modify: `app/review-ui/document-sets/[id]/review-pack/page.tsx`
- Modify: `tests/review-ui.test.ts`

- [ ] Write failing backend and frontend tests that expect one canonical risk card with supporting signal count/IDs, a human-readable QA decision, and a separately labelled technical coverage warning.
- [ ] Run the relevant pytest/Vitest tests and confirm the fields are absent.
- [ ] Expose canonical risk cards and supporting finding counts from `ReviewPackService`; make review progress count root risks rather than raw signals.
- [ ] Render a concise decision summary, root-risk cards, expandable supporting signals/evidence, and a distinct operational-warning panel.
- [ ] Re-run focused tests and commit the pack/UI change.

### Task 4: PDF and CSV export are concise and Unicode-safe

**Files:**
- Modify: `src/lib/review-pack-export.ts`
- Modify: `src/components/review-ui/review-pack-export-actions.tsx`
- Modify: `tests/review-pack-export.test.ts`

- [ ] Write failing tests for German headings/umlauts, a QA-facing decision headline, canonical risk count, and optional technical warning section.
- [ ] Run `npm test -- tests/review-pack-export.test.ts` and confirm the current PDF either lacks the requested text or uses the raw decision.
- [ ] Use WinAnsi font encoding with a safe German-character mapping, replace technical/raw labels, and export root risks once with supporting signal counts and evidence appendix.
- [ ] Re-render an exported fixture PDF with Poppler and inspect it visually for umlauts, wrapping, headers, and page transitions.
- [ ] Re-run the export tests and commit.

### Task 5: PKG-001 quality evaluation and release gate

**Files:**
- Modify: `backend/app/schemas/evals.py`
- Modify: `backend/app/services/eval_runner.py`
- Modify: `backend/app/services/regression_gate.py`
- Modify: `backend/app/evals/run_goldstandard.py`
- Create: `backend/tests/test_pkg001_regression.py`
- Modify: `backend/tests/test_eval_harness.py`
- Modify: `backend/tests/test_regression_gate.py`

- [ ] Write failing tests for PKG metrics: must-detect recall, duplicate count per gold finding, unsupported finding rate, false-positive-boundary violations, severity exact/under/over calls, and auto-clear prevention.
- [ ] Add a test that the upload manifest only includes package documents and rejects `GOLD_STANDARD.json` and answer-key filenames.
- [ ] Run the focused backend tests and confirm new metrics/gates are unavailable.
- [ ] Extend the evaluator/report and full-pipeline harness to score PKG-001 after execution using the oracle only as a post-run test artifact. Update the harness to poll/consume asynchronous pipeline completion rather than expecting HTTP 201.
- [ ] Configure the release gate to fail on any missed high finding, high under-call, auto-clear with blocker gold, or unsupported high/critical published finding.
- [ ] Re-run evaluator/regression/Pipeline tests and commit.

### Task 6: Provider roles and final verification

**Files:**
- Modify: `backend/app/services/review_orchestrator.py`
- Modify: `backend/tests/test_prompt_templates.py`
- Modify: `backend/tests/test_provider_adapters.py`
- Modify: `README.md`

- [ ] Write failing tests that require the primary reviewer to emit candidate findings, a critic to challenge only high-risk candidates, and deterministic publication/evidence gates to make the final decision.
- [ ] Keep configured provider selection compatible while making role responsibilities explicit in prompts and model manifest metadata.
- [ ] Run all backend/frontend tests, static checks, build, the mock goldstandard harness, and a local exported-PDF visual check.
- [ ] Deploy the verified commit to the isolated Hetzner backend/frontend services and verify one authenticated production run returns a concise root-risk pack without a 502.

## Coverage review

- Aggregation and reduction: Tasks 1 and 3.
- Evidence, false-positive, and severity calibration: Tasks 1, 2, and 5.
- Clear human-facing status: Tasks 2 and 3.
- PDF/export quality: Task 4.
- Model responsibilities: Task 6.
- Regression/Goldstandard safety without oracle leakage: Task 5.
- Live verification: Task 6.
