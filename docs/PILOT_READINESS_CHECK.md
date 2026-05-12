# Pilot Readiness Check

Date: 2026-05-09  
Scope: Pharma QRM Delta Factory prototype application, backend-first risk orchestration workflow, Vercel production deployment.

## Executive Summary

The system is ready for a controlled synthetic walkthrough.

It is not yet ready for unsupervised customer document processing or production-like regulated use. The main blocker is not code stability; it is operational readiness around secrets, access boundaries, provider activation, customer data handling, and pilot governance.

Recommended next step: use the current deployment for a Szilard/internal walkthrough, then complete the P0 actions below before accepting real customer documents.

## Verified Working

- Frontend production route is reachable:
  - `https://qrm-delta-factory.vercel.app/case-workspace`
  - HTTP status: `200`
- Review UI production route is reachable:
  - `https://qrm-delta-factory.vercel.app/review-ui`
  - HTTP status: `200`
- Built-in sample seeding has been removed from the visible tool. Synthetic test packages should be generated externally and uploaded through the backend workflow.
- Review decision write path works through the frontend API proxy:
  - Decision tested: `request_more_information`
  - Response status: `200`
- Frontend verification:
  - `npm test`: `38 passed`
  - `npm run build`: passed
- Backend verification:
  - `pytest`: `136 passed`
  - `ruff check .`: passed
  - `mypy app`: passed
- Secret scan of repo did not find the pasted real API keys or Supabase password in source files.
- Old frontend ensemble/agent layer has been removed from the Next.js app.
- Live Vercel frontend deployment is on commit `44cfed9`.

## Current Walkthrough Story

The prototype should show the intended safety posture:

1. A synthetic, externally generated test package is uploaded.
2. The backend pipeline generates a human-review dossier.
3. The system does not auto-clear unclear or high-risk cases.
4. Missing evidence, contradictions, weak citations, OOD signals, and potential high-risk impacts route the case to human review.
5. A reviewer can record a decision.

This is a good walkthrough of decision support, not autonomous regulatory decision-making.

## P0 Before Real Customer Pilot

These should be completed before using real or customer-provided documents.

### 1. Rotate Exposed Secrets

Real API keys and database credentials were shared in chat. They were not committed to the repo, but they should still be treated as exposed.

Actions:

- Rotate OpenAI key.
- Rotate Anthropic key.
- Rotate Gemini key.
- Rotate Supabase database password or create a fresh least-privilege database user for the pilot.
- Remove unused real model keys from Vercel frontend env unless they are intentionally required.
- Keep `QRM_EXTERNAL_MODEL_CALLS_ENABLED=false` until a formal pilot decision enables external providers.

### 2. Decide Backend Access Model

The backend deployment is protected by Vercel Authentication when accessed directly. The frontend proxy works, but direct API testing by a pilot customer would not.

Actions:

- For an internal walkthrough: keep protection as-is.
- For a customer pilot: either keep all access through the frontend or configure a deliberate API access path with API key, tenant isolation, and clear logging.
- Do not open the backend publicly without confirming tenant-scoped API-key enforcement on every pilot endpoint.

### 3. Create a Dedicated Pilot Tenant and API Key

Pilot data must be separated from synthetic test packages and local evaluation fixtures.

Actions:

- Create one tenant ID per pilot.
- Create a dedicated API key per tenant.
- Confirm cross-tenant access tests still pass against persistent storage.
- Avoid mixing pilot data with synthetic test packages.

### 4. Lock the Pilot to Mock Providers Unless Explicitly Approved

The current architecture supports real provider adapters, but tests should continue to use deterministic mock providers.

Actions:

- Keep external model calls disabled for first customer walkthrough.
- If real providers are later enabled, record provider, model ID, prompt version, request hash, response hash, and policy version.
- Confirm no full sensitive document text is logged or stored in model-run metadata.

### 5. Define Data Handling Rules

The current app is a prototype. Customer documents require an explicit handling boundary.

Actions:

- Use anonymized or non-critical documents for the first pilot.
- Document retention period.
- Document deletion process.
- Who can access uploaded files.
- Whether files may leave the customer environment.
- Whether external LLM providers are allowed.

## P1 Before Paid Pilot

### 1. End-to-End Customer Fixture

Create one realistic anonymized pilot fixture:

- One change control or deviation record.
- Existing risk/FMEA excerpt.
- SOP excerpt.
- Validation or effectiveness evidence.
- At least one intentionally missing required attachment.

Then run the full pipeline and compare output against human expectations.

### 2. Pilot Export Review

Generate the Review Pack and review it with a pharma QA/Regulatory person.

Check:

- Is the language consultant-friendly?
- Are findings too noisy?
- Are source quotes enough for a reviewer to work quickly?
- Are human actions clear?
- Does the pack look like a credible deliverable?

### 3. False Positive Calibration

Use reviewer decisions to identify noisy patterns.

Do not automatically suppress high or critical findings. Any prompt, requirement, or policy change should create a new version and run regression tests.

### 4. Basic Operational Runbook

Add a short runbook:

- How to start a synthetic walkthrough.
- How to seed data.
- How to confirm backend health.
- How to recover if Supabase or Vercel fails.
- How to rotate keys.

## P2 Later

- Proper file upload UI for customer documents.
- Background job queue for larger document sets.
- Better document parser quality reporting in the UI.
- Pilot-specific dashboard for throughput and human-review workload.
- Formal validation package refinement.
- More realistic requirement libraries per document type and process area.

## Known Limitations

- This is still a prototype.
- It does not claim GMP compliance, validation, approval, or regulatory acceptance.
- It does not replace qualified SME, QA, or Regulatory reviewers.
- The current production deployment is suitable for synthetic, non-customer test packages.
- Real customer use requires agreed governance, security review, privacy review, and customer QA oversight.

## Readiness Verdict

Status: Prototype walkthrough-ready, not customer-production-ready.

Use now for:

- Internal walkthrough with Szilard.
- Walkthrough with externally generated synthetic adversarial test packages.
- Discussion of workflow, review queue, evidence map, and human workload reduction.

Do not use yet for:

- Real confidential customer documents.
- Unsupervised customer upload.
- External LLM processing of customer data.
- Any regulated decision or approval workflow.
