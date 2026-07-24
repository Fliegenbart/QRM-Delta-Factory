# Strong AI Review Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the production QRM workflow reliably synthesize the five PKG-001 risks from complete source evidence, use the intended model mix, preserve conservative human-review gating, and block releases when the visible review pack regresses.

**Architecture:** Keep deterministic parsing, citation integrity, requirement applicability, and the human decision boundary. Replace the lossy claims-only reviewer input with bounded, role-relevant source excerpts; version and refresh the canonical requirement library; harden provider normalization; and permit canonical publication only when a finding is supported by multiple exact, source-diverse citations with matching factual anchors. Validate the final user-visible ReviewPack against PKG-001, not only internal raw findings.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, pytest, TypeScript, Next.js, Vitest, Docker Compose, PostgreSQL snapshot persistence.

---

### Task 1: Deliver source evidence to every reviewer

**Files:**
- Modify: `backend/app/services/review_orchestrator.py`
- Modify: `backend/app/core/config.py`
- Test: `backend/tests/test_primary_review_orchestrator.py`

- [x] Add a failing test proving that the Validation, Regulatory, Batch Impact, Contradiction and critic reviewers receive bounded exact source excerpts containing the PKG-001 limit, equipment, QA, training and retest evidence.
- [x] Run the focused pytest target and confirm it fails because `ReviewerAgent.run()` currently receives only claims and requirements.
- [x] Add role-relevant, source-diverse chunk selection with explicit maximum chunk and character limits. Include `evidence_context` in the provider input and derive case signals from both claims and chunks.
- [x] Strengthen the shared reviewer contract: cross-document findings must cite every source needed to establish the requirement, observed state and contradiction.
- [x] Run the focused orchestrator tests and confirm they pass.

### Task 2: Refresh the canonical requirement library safely

**Files:**
- Modify: `src/data/gmp-general-requirement-library.json`
- Modify: `src/lib/review-api.ts`
- Test: `tests/review-ui.test.ts`
- Test: `backend/tests/test_requirement_library.py`

- [x] Add a failing frontend test proving that an apparently modern 23-rule set missing the current canonical IDs is refreshed.
- [x] Add a failing backend test proving the canonical library version contains all five PKG-001 rules and a new version marker.
- [x] Replace the legacy-name heuristic with deterministic canonical version/requirement-ID comparison for the configured default set.
- [x] Bump the canonical library version without changing the configured tenant-specific set ID.
- [x] Run the focused frontend and backend tests and confirm they pass.

### Task 3: Harden provider output and restore the intended model mix

**Files:**
- Modify: `backend/app/agents/providers/base.py`
- Modify: `backend/app/services/review_orchestrator.py`
- Modify: `docker-compose.hetzner.yml`
- Test: `backend/tests/test_provider_adapters.py`
- Test: `backend/tests/test_primary_review_orchestrator.py`

- [x] Add failing tests for Anthropic-style string-valued findings using valid JSON, fenced JSON, and Python-literal list syntax.
- [x] Add a failing test proving default production role routing is mixed across Anthropic, OpenAI and Mistral when no explicit override is supplied.
- [x] Implement bounded safe parsing for string-valued findings and keep invalid/truncated content fail-closed.
- [x] Remove the Mistral-only production default override and enable all three configured critic providers by default while preserving an explicit administrator override.
- [x] Run focused provider and orchestration tests and confirm they pass.

### Task 4: Publish evidence-backed multi-document findings

**Files:**
- Modify: `backend/app/verifiers/evidence.py`
- Modify: `backend/app/services/risk_fusion.py` only if needed by the verified contract
- Test: `backend/tests/test_evidence_verifier.py`
- Test: `backend/tests/test_risk_fusion.py`

- [x] Add failing verifier tests for all five PKG-001 risk statements using exact expected source quotes and applicable requirements.
- [x] Add negative tests showing that unrelated duplicate quotes, missing factual anchors, a single weak source, or a contextual/contradicting citation cannot become strong.
- [x] Implement a deterministic multi-document synthesis rule: exact citations, at least two source documents, supports-only evidence, applicable requirement, no missing information, and complete factual-anchor coverage.
- [x] Preserve the conservative lexical path for single-source findings and existing fail-closed behavior.
- [x] Run verifier and fusion tests and confirm the five positive cases publish while negative cases remain partial/none.

### Task 5: Make PKG-001 a release gate

**Files:**
- Modify: `backend/app/evals/run_goldstandard.py`
- Modify: `backend/tests/test_pkg001_regression.py`
- Add: `backend/tests/fixtures/pkg001/*`
- Modify: `tests/review-pack-export.test.ts`

- [x] Add the synthetic PKG-001 documents and oracle as a checked-in test fixture, excluding the oracle from uploads.
- [x] Add failing tests that infer `change_control_package` and `qc_lab` from the package metadata instead of the deviation defaults.
- [x] Add failing review-pack assertions for five target themes, zero missed high findings, no empty canonical section, and no false credit from generic partial hints.
- [x] Make package-mode evaluation exit non-zero when the visible ReviewPack misses a blocking oracle finding.
- [x] Add a PDF-export regression proving the five target statements remain in the canonical section with human-readable source names.
- [x] Run the focused backend and frontend regression tests and confirm they pass.

### Task 6: Integrate, release and verify production

**Files:**
- Modify only files required by Tasks 1-5.

- [ ] Run full backend pytest, frontend Vitest, typecheck, production build, Ruff, MyPy and `git diff --check`.
- [ ] Commit the verified implementation on `codex/pharmaqrm-production` and push it.
- [ ] Back up the production database/snapshot before deploying.
- [ ] Deploy backend and frontend to Hetzner without changing `gmp.labpulse.ai`.
- [ ] Verify deployed commit, container health, active canonical requirement IDs, and actual mixed provider routing without exposing secrets.
- [ ] Run PKG-001 through production with `change_control_package` + `qc_lab`, score the resulting ReviewPack against the five-error oracle, and inspect the exported PDF.
- [ ] Report exact recall, provider statuses, canonical/partial counts, deployment revision and any residual limitations.
