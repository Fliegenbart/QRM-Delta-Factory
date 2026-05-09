# Pharma AI Risk Orchestration Backend

Backend skeleton for a pharmaceutical AI risk orchestration system.

This service is intended as decision support for qualified QA, Regulatory, and SME reviewers. It does not autonomously approve risk decisions, claim regulatory acceptance, or replace human responsibility.

## Architecture Overview

The backend is organized around explicit module boundaries:

- `app/api/` - HTTP route modules
- `app/core/` - configuration and application-level utilities
- `app/db/` - database sessions and persistence setup
- `app/models/` - database models
- `app/schemas/` - Pydantic request/response contracts
- `app/services/` - application use cases
- `app/agents/` - LLM reviewer interfaces and mock providers
- `app/verifiers/` - evidence and citation verification
- `app/risk/` - conservative risk aggregation logic
- `app/evals/` - evaluation harnesses and fixtures
- `app/audit/` - audit trail and versioned event capture
- `app/storage/` - object/document storage integration
- `tests/` - automated tests

Current implemented scope is intentionally small:

- FastAPI app in `app/main.py`
- health endpoint at `GET /health`
- versioned requirement-library import at `POST /requirement-sets/import`
- active requirement-library search at `GET /requirements/search`
- document-set creation at `POST /document-sets`
- document upload at `POST /document-sets/{id}/documents`
- claim-ledger generation at `GET /document-sets/{id}/claims`
- multi-agent primary review at `POST /document-sets/{id}/run-primary-review`
- adversarial review at `POST /document-sets/{id}/run-adversarial-review`
- conservative risk fusion at `POST /document-sets/{id}/run-risk-fusion`
- review-pack generation at `GET /document-sets/{id}/review-pack`
- synchronous end-to-end pipeline runs at `POST /document-sets/{id}/pipeline-runs`
- pipeline-run retrieval at `GET /pipeline-runs/{id}`
- human review decisions at `POST /findings/{id}/review-decision`
- evaluation harness at `POST /evals/run`
- local filesystem storage behind a storage interface
- TXT and PDF parsing behind a testable `DocumentParser` abstraction
- page-level chunk creation and parsing-quality escalation
- deterministic mock claim extraction behind a `ClaimExtractor` interface
- parallel mock reviewer agents behind a `BaseModelProvider` interface
- versioned reviewer prompt templates under `app/agents/prompts/`
- deterministic evidence verification for reviewer findings
- adversarial challenges and risk-fusion storage for human review
- out-of-distribution and reviewer-coverage gates before auto-clear candidate status
- policy-versioned `RiskDecision` records with conservative auto-clear gates
- compact reviewer dossiers and auditable human review decisions
- validated fixture-based evals for recall, omission, false positives, citation precision, and requirement matching
- hash-chained audit trail with metadata sanitization and tamper detection
- API-key based tenant isolation for protected MVP endpoints
- in-memory audit events for requirement import/activation/deactivation, uploads, and parser runs
- environment-based config loading through `QRM_*` variables
- pytest tests for health, config loading, domain schemas, and document ingestion
- Docker Compose with App, PostgreSQL, and Redis

## Document Ingestion

Document sets must reference one active RequirementSet version. This prevents later findings from
being based on free model knowledge rather than a controlled internal requirement library.

Create a document set:

```bash
curl -X POST http://localhost:8000/document-sets \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_demo_pharma",
    "requirement_set_id": "rset_demo_gmp_qrm_2026_1",
    "declared_document_type": "change_control_package",
    "declared_process_area": "automated_visual_inspection",
    "uploaded_by": "user_qrm_author"
  }'
```

Upload a document into that set:

```bash
curl -X POST http://localhost:8000/document-sets/ds_example/documents \
  -F "uploaded_by=user_qrm_author" \
  -F "file=@example.pdf;type=application/pdf"
```

The MVP supports `.txt`, `.pdf`, and `.docx` uploads. TXT and PDF text is extracted now.
DOCX is accepted through a placeholder parser and escalated for human review until real extraction
is implemented. OCR is intentionally not implemented yet; the parser layer is ready for a future
OCR provider.

Document quality is scored from extracted text per page, empty pages, replacement characters,
extreme shortness, and parser errors. Documents below `QRM_PARSING_QUALITY_THRESHOLD` are marked
`needs_human_review`.

## Claim Ledger

Build or read the claim ledger for a document set:

```bash
curl http://localhost:8000/document-sets/ds_example/claims
```

The MVP uses `MockClaimExtractor` for deterministic tests and demo fixtures. `LLMClaimExtractor`
exists only as a stub and does not call external APIs. Every stored claim must include source
traceability: `document_id`, `chunk_id`, `page`, `raw_text_quote`, and `confidence`.

The ledger rejects claims whose quote is empty or not present in the source chunk. Duplicate claims
are deduplicated, and shared identifiers such as batch IDs, CAPA IDs, deviation IDs, and
product/material IDs are linked through claim dependencies. Claim extraction writes an audit event
with extractor version and prompt version.

## Primary Review Orchestrator

Run the primary multi-agent review:

```bash
curl -X POST http://localhost:8000/document-sets/ds_example/run-primary-review
```

The orchestrator runs deterministic mock reviewer agents in parallel:

- `GMPDataIntegrityReviewer`
- `DeviationReviewer`
- `CAPAReviewer`
- `BatchImpactReviewer`
- `RegulatoryConsistencyReviewer`
- `ContradictionHunter`

Each agent works only from the Claim Ledger and active RequirementSet. Findings must validate
against the `RiskFinding` schema and include at least one `EvidenceItem`. If an agent has no
finding, it must return an explicit coverage summary. Invalid model output is stored as a failed
`ModelRun`; it does not clear the review. Raw model output is hashed and stored with an encryption
flag for a later storage/security implementation.

Reviewer prompts are loaded from versioned Markdown files in `app/agents/prompts/`. Each prompt
must define role, scope, inputs, output schema, hard rules, escalation logic, examples, the ban on
free world knowledge, and mandatory page/chunk/quote evidence. The loaded prompt version is stored
in every `ModelRun` and in the model-run audit event.

## Evidence Verification

Reviewer findings are passed through `EvidenceVerifierService` before they are stored as review
outputs. The verifier performs deterministic checks:

- referenced `document_id` exists
- referenced `chunk_id` exists
- quoted text matches the chunk exactly or with conservative fuzzy matching
- page number is plausible for the chunk
- referenced requirements exist
- referenced requirements apply to the document type and process area
- `auto_close_allowed` does not conflict with the referenced requirement

The verifier attaches a `FindingVerificationResult` to each finding. Findings with unsupported
quotes, non-applicable requirements, or `evidence_support=none` are not deleted. They are stored as
unverified review items and remain routed for human review.

## Adversarial Review Layer

Run the adversarial review after the primary review:

```bash
curl -X POST http://localhost:8000/document-sets/ds_example/run-adversarial-review
```

The adversarial layer uses deterministic role agents in this MVP:

- `MissedCriticalRiskHunter`
- `MissingEvidenceHunter`
- `CrossDocumentContradictionHunter`
- `FalseClearanceChallenger`

It receives the Claim Ledger, active RequirementSet, primary findings, and persisted coverage
summaries. It is not allowed to close findings or clear risk areas. It can only create additional
`RiskFinding` records, persistent `AdversarialChallenge` records, challenged no-issue claims, and
unresolved human-review questions. The response also exposes the explicit reviewer-contract fields
`new_findings` and `escalation_reasons`; `additional_findings` remains as a backwards-compatible
alias for existing MVP clients. High or critical challenges are always routed to human review.

Adversarial findings are merged with primary findings into a risk-fusion list. Challenges are
append-only in the current in-memory implementation and are never automatically deleted.

Current deterministic adversarial checks include missed high-risk impact claims, missing required
evidence, weak no-issue coverage, cross-document contradictions, unsupported "Operator Error" root
cause claims, and low document-quality escalation. These checks are conservative review triggers,
not automated final decisions.

## Risk Fusion

Run conservative risk fusion after primary review, verification, and adversarial review:

```bash
curl -X POST http://localhost:8000/document-sets/ds_example/run-risk-fusion
```

Risk Fusion aggregates primary findings, adversarial findings, verification results, document
quality, model failures, model disagreement, missing required attachments, out-of-distribution
signals, and reviewer coverage. It does not use majority voting. A plausible high or critical item
is enough to require human review, and weak or partial high/critical evidence blocks auto-clear.

Out-of-distribution gates currently score:

- unknown document type
- unknown process area
- unsupported language
- low parsing quality
- missing required documents
- unusually few claims
- unusually many unclear claims
- no matching requirements
- failed model run for a required reviewer role

Coverage gates check which reviewer roles are required for the declared document type and process
area, whether those roles completed, whether any required role failed, and whether the active
RequirementSet covers the package scope. Missing Requirements are not treated as a clean result;
they are a human-review reason. Coverage gaps in high/critical-relevant scopes block auto-clear.

The output is a policy-versioned `RiskDecision` with:

- decision class
- max severity
- document quality score
- out-of-scope score
- reviewer coverage score
- OOD and coverage reasons
- model disagreement score
- auto-clear blockers
- required human-review reasons
- deterministic finding clusters

`auto_clear_candidate` is only returned when all gates pass. It is still a candidate state for
human-controlled workflow design, not an autonomous regulatory decision.

## End-to-End Pipeline Runs

After documents are uploaded, run the full orchestration pipeline:

```bash
curl -X POST http://localhost:8000/document-sets/ds_example/pipeline-runs
```

For the MVP this runs synchronously, but the service exposes a small `PipelineJobQueue` protocol so
the same boundary can later be backed by Celery or RQ. The pipeline executes:

1. Parse DocumentSet
2. Quality Gate
3. Requirement Retrieval
4. Claim Ledger Extraction
5. Primary Multi-Agent Review
6. Evidence Verification
7. Adversarial Review
8. Verification of adversarial findings
9. Risk Fusion
10. Review Pack Generation
11. Audit Trail Completion

Each step writes a pipeline audit event. If a technical step fails, the run is marked `failed` and
the DocumentSet is routed to human review. If a model run fails but the pipeline can continue, Risk
Fusion treats it as a coverage risk and the PipelineRun is marked `needs_human_review`, not cleared.

Retrieve a run:

```bash
curl http://localhost:8000/pipeline-runs/prun_example
```

## Review Pack Generator

Generate a compact review dossier after Risk Fusion:

```bash
curl http://localhost:8000/document-sets/ds_example/review-pack
```

The Review Pack is built deterministically from the latest `RiskDecision` and related evidence. It
summarizes top risks, finding clusters, cited source evidence with page/chunk IDs, model positions,
verifier results, OOD/Coverage reasons, missing information, recommended reviewer actions, and
audit references.

Record a human reviewer decision:

```bash
curl -X POST http://localhost:8000/findings/finding_example/review-decision \
  -H "Content-Type: application/json" \
  -d '{
    "reviewer_id": "reviewer_qa_1",
    "decision": "request_more_information",
    "rationale": "Current validation addendum is required before QA disposition."
  }'
```

Supported reviewer actions include confirm, downgrade, reject false positive, request more
information, link to CAPA, and escalate to QA. Each stored decision writes an audit event.

## False-Positive Analytics

Analyze repeated human overrides:

```bash
curl http://localhost:8000/analytics/false-positives
```

`HumanOverrideAnalyzer` reads human decisions with `reject_false_positive` or `downgrade` and
clusters them by requirement, risk category, reviewer-agent role, prompt version, evidence support,
and document type. The output suggests possible prompt clarifications, requirement-rule
clarifications, deterministic verifier checks, and low-risk do-not-auto-escalate candidates.

These are recommendations only. The analyzer does not edit findings, Risk Fusion, prompts,
requirements, verifier rules, or policy. Any accepted change needs a new version and an evaluation
run. High and Critical findings keep their recall guard and are not auto-closed by false-positive
patterns.

## Evaluation Harness

Run a validated synthetic eval fixture:

```bash
curl -X POST http://localhost:8000/evals/run \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": "evalds_deviation_missing_batch_impact"}'
```

The MVP eval harness loads fixtures from `examples/evals/` and reports:

- recall by severity
- false omission rate
- false positive rate
- citation precision
- requirement match accuracy
- auto-clear false negative count
- human review rate

Current example datasets:

- `evalds_clean_low_risk`
- `evalds_deviation_missing_batch_impact`
- `evalds_capa_missing_effectiveness_check`

An eval fails if a `critical` must-detect gold finding is missed, or if auto-clear occurs despite
known `high` or `critical` gold findings. Reports are returned as structured JSON plus Markdown.

## Regression Gate Release Process

Any change to model configuration, prompt versions, RequirementSet versions, orchestration version,
or Risk Fusion policy must be compared against the validated eval datasets before release. The
intended process is:

1. Run the eval suite with the current released configuration and store it as the baseline
   `RegressionRun` JSON.
2. Run the same eval suite with the candidate configuration and store it as the candidate
   `RegressionRun` JSON.
3. Compare both runs with the regression gate:

```bash
python -m app.evals.run_regression \
  --baseline baseline-regression-run.json \
  --candidate candidate-regression-run.json \
  --markdown-output regression-gate-report.md \
  --json-output regression-gate-report.json
```

The gate blocks release if:

- any Critical `must_detect` gold finding is missed by the candidate
- auto-clear occurs despite a known High/Critical gold finding
- citation precision falls below the configured threshold
- requirement match accuracy falls below the configured threshold
- human review rate increases beyond the configured limit without must-detect recall improvement

The report is advisory for release governance, but the blocking decision is deterministic. A failed
gate means the candidate configuration should not be promoted until the issue is fixed, a new
version is created where applicable, and the eval run passes.

## Audit Trail

The in-memory MVP audit layer is designed as an append-only hash chain. Each event stores:

- audit event ID
- tenant ID
- actor type and actor ID
- event type
- entity type and entity ID
- timestamp
- input and output hashes
- sanitized metadata
- previous event hash
- event hash

The event hash is calculated from the event data plus the previous event hash. `verify_hash_chain()`
detects tampering or broken ordering.

Canonical audit events are emitted for the main pipeline:

- `document_uploaded`
- `document_parsed`
- `chunks_created`
- `claims_extracted`
- `requirements_retrieved`
- `model_run_started`
- `model_run_completed`
- `model_run_failed`
- `finding_created`
- `finding_verified`
- `risk_fusion_completed`
- `review_pack_created`
- `human_review_decision_created`
- `eval_run_completed`

Metadata is sanitized before storage. Secret-like keys and full-text-like fields are replaced with
hash/length summaries, so the audit trail keeps traceability without storing raw sensitive document
text or secrets.

## Requirement Library

Import a versioned RequirementSet from YAML or JSON:

```bash
curl -X POST http://localhost:8000/requirement-sets/import \
  -F "imported_by=user_quality_admin" \
  -F "file=@examples/requirements/deviation_management.yaml;type=application/x-yaml"
```

Activate the imported version:

```bash
curl -X POST http://localhost:8000/requirement-sets/rset_demo_gmp_qrm_2026_1/activate
```

Search active requirements:

```bash
curl "http://localhost:8000/requirements/search?document_type=change_control&process_area=aseptic_filling&criticality=high"
```

Validation rules enforced on import:

- `requirement_id` must be unique inside one `RequirementSet`
- `source_version`, `effective_from`, and `criticality` are required
- `required_evidence` cannot be empty for `high` or `critical` requirements

The synthetic example library covers Deviation Management, CAPA, Batch Impact Assessment,
QA Approval, Data Integrity, and Change Control.

## Local Development

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
mypy app
```

## Docker

From the repository root:

```bash
docker compose up --build
```

Services:

- FastAPI app: `http://localhost:8000`
- Healthcheck: `http://localhost:8000/health`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Configuration

No real secrets are committed. Copy the example and change values locally:

```bash
cp backend/.env.example backend/.env
```

Configuration keys use the `QRM_` prefix.

## Security Assumptions And Tenant Isolation

MVP authentication uses `X-API-Key`. Configure tenant-scoped keys with:

```bash
QRM_API_KEYS="tenant_demo_pharma=replace-with-real-secret"
```

When `QRM_API_KEYS` is set, protected endpoints reject missing or invalid keys with `401`.
The API key maps to one `tenant_id`; document sets, requirement sets, findings, review packs,
and review decisions are scoped so one tenant cannot read or mutate another tenant's data.
`/health` remains public for deployment checks.

Security defaults:

- `QRM_EXTERNAL_MODEL_CALLS_ENABLED=false`
- `QRM_ALLOWED_MODEL_PROVIDERS="mock"`
- `QRM_ALLOWED_NETWORK_DOMAINS=""`

External model provider classes are stubs in this MVP. If external model calls are disabled, they
fail closed before making any provider request. No real API keys should be committed; use
environment variables or a deployment secret manager.

## Model Provider Adapters

Provider adapter modules are prepared under `app/agents/providers/`:

- `base.py`
- `openai_provider.py`
- `anthropic_provider.py`
- `gemini_provider.py`
- `mock_provider.py`

All providers implement the same typed `BaseModelProvider` interface and return structured output
validated against a Pydantic schema. `MockProvider` remains the default for tests and local
deterministic behavior.

External providers are fail-closed by default:

```bash
QRM_EXTERNAL_MODEL_CALLS_ENABLED=false
QRM_ALLOWED_MODEL_PROVIDERS="mock"
```

To prepare a later real-provider deployment, configure explicit provider allowlists, model IDs,
and secrets through environment variables only:

```bash
QRM_EXTERNAL_MODEL_CALLS_ENABLED=true
QRM_ALLOWED_MODEL_PROVIDERS="openai,anthropic,gemini"
QRM_OPENAI_API_KEY="..."
QRM_ANTHROPIC_API_KEY="..."
QRM_GEMINI_API_KEY="..."
QRM_OPENAI_MODEL_ID="..."
QRM_ANTHROPIC_MODEL_ID="..."
QRM_GEMINI_MODEL_ID="..."
QRM_MODEL_PROVIDER_TIMEOUT_SECONDS=30
QRM_MODEL_PROVIDER_MAX_RETRIES=0
QRM_MODEL_PROVIDER_CIRCUIT_BREAKER_THRESHOLD=3
```

The MVP adapters still do not make real network calls. They validate configuration and raise clear
provider errors. Provider failures are persisted as failed model runs by the orchestrator, and Risk
Fusion treats failed model coverage as an auto-clear blocker.

Log and audit metadata is redacted before storage. Secret-like keys and full-text-like fields are
stored only as hash/length summaries. The MVP should not log full document text.

Known MVP limits:

- API keys are static shared secrets, not user identities or rotating credentials.
- Child records such as claims and findings are tenant-scoped through their `document_set_id`;
  a production database should also include explicit tenant columns and database-level row policies.
- No active outbound network allowlist enforcement exists yet; `QRM_ALLOWED_NETWORK_DOMAINS` is
  configuration groundwork.
- Production use needs a formal auth model, key rotation, least-privilege roles, rate limits,
  database row-level isolation, and security validation under the customer's quality system.

## GxP / Regulatory Note

This is a prototype foundation. Production use would require validation under the customer's quality system, SOPs, access control, audit trail controls, supplier assessment, privacy/security review, model governance, backup and restore testing, and periodic review.
