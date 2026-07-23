# Production Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the QRM production path fail-safe for data, access, jobs, audit evidence, provider outages, and the review result contract.

**Architecture:** Replace mutable global-snapshot behavior at system boundaries with explicit fail-safe guards, durable append-only records, and database-backed job leases. The frontend will derive access from a verified user membership instead of a deployment-wide tenant assumption, while the backend remains the final authorization authority. Review-pack findings will carry an explicit publication state so partial QA hints cannot be mistaken for verified risks.

**Tech Stack:** Next.js, Supabase SSR, FastAPI, SQLAlchemy/PostgreSQL, Redis, Pydantic, pytest, Vitest.

---

### Task 1: Make evaluation and deletion fail-safe

**Files:**
- Modify: `backend/app/evals/run_goldstandard.py`
- Modify: `backend/app/db/in_memory.py`
- Modify: `backend/app/storage/local.py`
- Modify: `backend/app/api/document_sets.py`
- Test: `backend/tests/test_eval_harness.py`
- Test: `backend/tests/test_storage_safety.py`

- [ ] Add a regression test that imports a persistent repository before invoking the goldstandard runner and proves the persistent snapshot is unchanged.
- [ ] Replace runner use of the global repository with a newly constructed in-memory repository injected into an application factory; refuse execution unless persistence is disabled and the storage root is the dedicated temporary root.
- [ ] Add storage deletion with path containment checks, make case deletion remove document bytes before metadata, and record a retryable deletion failure rather than returning a false successful deletion.
- [ ] Run `./.venv/bin/python -m pytest tests/test_eval_harness.py tests/test_storage_safety.py -q` from `backend/`.

### Task 2: Persist audit evidence and remove mutable startup behavior

**Files:**
- Create: `backend/app/audit/persistent.py`
- Modify: `backend/app/audit/events.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/db/in_memory.py`
- Modify: `backend/app/services/review_pack.py`
- Test: `backend/tests/test_audit_trail.py`
- Test: `backend/tests/test_persistent_repository.py`

- [ ] Add a failing restart test proving audit events and their hash chain survive a new repository/application instance.
- [ ] Store audit events in an append-only SQL table with tenant ID, predecessor hash, event hash and creation timestamp; use transactions for ordering.
- [ ] Remove automatic document deletion from repository load; migrate the legacy ID only through an explicit, auditable maintenance command.
- [ ] Add snapshot revision/checksum and compare-and-swap writes so a stale process cannot overwrite a newer snapshot.
- [ ] Run focused audit and persistence tests.

### Task 3: Make pipeline runs durable, idempotent and recoverable

**Files:**
- Create: `backend/app/services/pipeline_jobs.py`
- Modify: `backend/app/api/pipeline_runs.py`
- Modify: `backend/app/services/pipeline.py`
- Modify: `backend/app/main.py`
- Modify: `docker-compose.hetzner.yml`
- Test: `backend/tests/test_pipeline_runs.py`

- [ ] Add failing tests for duplicate start requests, stale running recovery, and terminal failure after lease expiry.
- [ ] Persist a job row with a unique active-run constraint per document set, lease/heartbeat, attempt count and idempotency key.
- [ ] Dispatch through a worker loop backed by the durable job table; on startup reclaim expired leases and mark/retry deterministically.
- [ ] Return the existing active run for an idempotent duplicate request and add explicit retry/cancel route behavior.
- [ ] Run pipeline tests and a Docker Compose integration smoke test.

### Task 4: Bound providers and preserve confidentiality

**Files:**
- Modify: `backend/app/agents/providers/base.py`
- Modify: `backend/app/agents/providers/external_base.py`
- Modify: `backend/app/services/review_orchestrator.py`
- Modify: `backend/app/core/config.py`
- Modify: `docker-compose.hetzner.yml`
- Test: `backend/tests/test_provider_adapters.py`
- Test: `backend/tests/test_primary_review_orchestrator.py`

- [ ] Add failing 429 and timeout tests that assert one retry owner, a bounded job deadline, provider-wide circuit state, and recorded retry metadata.
- [ ] Replace nested retry loops with one jittered retry policy that honors capped Retry-After and per-job deadline.
- [ ] Limit concurrent calls per provider/model and persist a shared circuit state in Redis.
- [ ] Disable raw output retention by default; when retention is enabled, require authenticated encryption with a production key and persist only ciphertext.
- [ ] Run provider and orchestration tests.

### Task 5: Enforce tenant membership and quality roles end-to-end

**Files:**
- Create: `utils/supabase/authorization.ts`
- Modify: `utils/supabase/middleware.ts`
- Modify: `utils/supabase/actor.ts`
- Modify: `src/lib/review-runtime-config.ts`
- Modify: `src/lib/review-api.ts`
- Modify: `app/api/review-ui/**/route.ts`
- Modify: `backend/app/core/security.py`
- Modify: `backend/app/api/*.py`
- Test: `tests/review-actor.test.ts`
- Test: `tests/review-document-set-route.test.ts`
- Test: `backend/tests/test_security_tenant_isolation.py`

- [ ] Add failing two-user/two-tenant tests and role-denial tests for delete, requirement import/activation, calibration and regression actions.
- [ ] Resolve tenant membership and role from verified Supabase claims server-side; deny users without an explicit membership.
- [ ] Forward a short-lived signed identity assertion to the backend and verify tenant/role there for every resource and controlled action.
- [ ] Map read, review, quality-admin and system-owner permissions to exact routes.
- [ ] Run frontend and backend authorization tests.

### Task 6: Make the review result contract unambiguous and reproducible

**Files:**
- Modify: `backend/app/schemas/review_pack.py`
- Modify: `backend/app/services/review_pack.py`
- Modify: `app/review-ui/document-sets/[id]/review-pack/page.tsx`
- Modify: `src/lib/review-pack-export.ts`
- Modify: `backend/Dockerfile`
- Modify: `backend/pyproject.toml`
- Create: `backend/requirements.lock`
- Test: `backend/tests/test_review_pack.py`
- Test: `tests/review-pack-export.test.ts`

- [ ] Add failing tests that prove partial hints are labelled as non-canonical in API, UI and PDF/CSV output.
- [ ] Add explicit `canonical` versus `qa_hint_partial` publication state and separate headings, badges, export fields and watermarks.
- [ ] Include verifier status and technical coverage state with every exported finding.
- [ ] Pin Python dependencies and container image digests; record immutable build/model revision provenance in the pipeline manifest.
- [ ] Run complete backend tests, frontend typecheck/tests, production build, and a live non-mutating health/auth smoke test.
