# Pharma QRM Delta Engine

MVP/prototype web application for AI-assisted Quality Risk Management delta analysis in pharmaceutical GMP environments.

## Kurz erklärt für Consultants

Dieses Projekt ist ein Review-Cockpit für vorbereitende pharmazeutische Risikoarbeit. Es nimmt hochgeladene Change-/Deviation-/CAPA-Unterlagen, verknüpft sie mit Quellen und Anforderungen und baut daraus eine kurze, prüfbare Risikomappe für SME, QA oder Regulatory.

Das Tool entscheidet nicht selbst. Es spart vor allem Such- und Sortieraufwand: Welche Risiken sind betroffen? Welche Quelle stützt welche Aussage? Welche Evidenz fehlt? Was muss ein Mensch als Nächstes prüfen?

Der wichtigste Pfad ist:

1. Unterlagen bereitstellen.
2. Quellen, Anforderungen und Prüfpunkte erzeugen.
3. Unvollständige Pakete zurück an Author/Ops geben.
4. Vollständige Pakete plausibilisieren.
5. Prüfpaket mit Quellen, Lücken und Review-Fragen öffnen.
6. Menschliche Review-Entscheidung dokumentieren.

## What this MVP does

- Stores a Prisma/SQLite data model for users, projects, source documents, snippets, risk-library items, risk items, evidence, gaps, plausibility checks, red-team findings, approvals, audit logs, exports, and validation artifacts.
- **Backend-first orchestration direction**: A new Python/FastAPI backend foundation under `backend/` provides the clean service structure for future claim-ledger, verifier, risk, audit, storage, and reviewer-agent modules.
- **Document Upload**: Start on the home page by uploading customer-cleared GMP source documents.
- Marks AI-generated content as `DRAFT`.
- Produces source-based draft risk updates, evidence gaps, plausibility checks, red-team missing-risk findings, a review queue, audit trail view, export preview, and draft validation-pack templates.
- Builds Risk Review Packages before independent plausibility review, so the Critic is not called on empty or incomplete technical input.
- Shows a Risk Review Summary, Risk-Based Review Queue, Evidence Map, workload-reduction estimate, and Draft Risk Delta Review Pack export once backend data exists.

## Backend-first Orchestration Direction

The previous simple ensemble-analysis direction is retired. The new process is:

1. parse uploaded documents into controlled chunks
2. create a source-linked Claim Ledger
3. evaluate claims against a versioned Requirement Library
4. run reviewer providers in parallel without live internet access
5. verify every finding against document ID, page, chunk ID, and quote
6. conservatively aggregate risk without model-majority voting
7. generate draft Review Packs for qualified QA/Regulatory human review

The initial backend lives in `backend/`. It uses Python 3.12, FastAPI, Pydantic v2 settings, pytest, ruff, mypy, Docker Compose, PostgreSQL, and Redis. It does not use real API keys.

## Important limits

This is an MVP/prototype. It does not autonomously perform regulatory decisions, does not replace qualified human risk assessment, does not replace QA responsibility, and does not guarantee regulatory authority acceptance.

The application supports human-reviewed, source-based QRM drafting. AI output must be treated as draft until reviewed and handled by qualified personnel under the regulated company's quality system.

The design is anchored around ICH Q9(R1)-style QRM logic, GMP data integrity expectations, EU GMP Annex 11-style computerized-system controls, and 21 CFR Part 11-style electronic-record controls where applicable.

Production use would require formal validation, SOPs, supplier assessment, security review, privacy review, model governance, periodic review, infrastructure qualification, backup/restore testing, access management, and customer QA decisions.

## Tech stack

- Next.js, React, TypeScript
- Tailwind CSS
- SQLite with Prisma schema and Prisma Client
- Vitest automated tests
- Local role selector for MVP review-state testing
- Python 3.12 backend foundation in `backend/`
- FastAPI, Pydantic v2 settings
- Docker Compose services for PostgreSQL, Redis, and the app
- pytest, ruff, mypy configuration

## Run locally

```bash
npm install
cp .env.example .env
npm run db:setup
npm test
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Minimal QA Review UI

The backend-first review workflow now has a minimal reviewer UI at:

```text
/review-ui
```

In the main product navigation, `Review Packs` is the entry point for the backend-first Risk Orchestration workflow. The previous frontend-only synthetic sample path has been removed from the visible tool.

Die Review-UI zeigt keine technische Modell-Spielerei, sondern vorbereitete Prüfpakete. Man sieht den Anlass, den Prozessbereich, die Quellen im Paket, die wichtigsten Prüfpunkte, die Zitate mit Seite/Chunk und den Grund, warum menschliche Prüfung erforderlich ist. Review-Entscheidungen werden über das FastAPI-Backend dokumentiert.

The browser never receives the backend API key. Configure the server-side proxy with:

```bash
QRM_BACKEND_URL="http://localhost:8000"
QRM_BACKEND_API_KEY=""
QRM_BACKEND_TENANT_ID="tenant_example_pharma"
QRM_DEFAULT_REQUIREMENT_SET_ID="rset_example_gmp_qrm_2026_1"
NEXT_PUBLIC_SUPABASE_URL=""
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=""
```

The start page can create a new review case, upload documents, and start the backend pipeline.
For adversarial internal test data, use the ready-to-copy briefing at:

```text
docs/adversarial-test-data-briefing.md
```

Supabase browser/server helpers live under `utils/supabase/`. The middleware refreshes Supabase
sessions when the public Supabase URL and publishable key are configured, and safely passes through
when they are missing.

## Environment Variables

The retired TypeScript frontend-agent layer has been removed. The new backend-first flow uses mock providers by default in tests and can use real configured providers in deployment. Backend configuration uses `QRM_*` variables. See:

```bash
backend/.env.example
```

No real secrets should be committed. Mock LLM providers are used for fixtures and tests.

For persistent backend state on Vercel, use Supabase Postgres by setting the backend environment:

```bash
QRM_PERSISTENCE_ENABLED=true
QRM_DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:PORT/postgres"
```

Use the Supabase pooler connection string for serverless deployments and store it only as a
deployment secret.

## Python backend quick start

```bash
cd backend
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
mypy app
```

Infrastructure:

```bash
docker compose up --build
```

The frontend role selector is an MVP convenience only. It is not authentication.

## Notes on database setup

The Prisma schema is the source for the SQLite structure. In this local environment, `prisma db push` returned a schema-engine error without diagnostic detail, so `npm run db:setup` uses Prisma to generate SQL from the schema and then applies that SQL with `sqlite3` before running the seed script.

## Key safety rules covered by tests

- Risk item cannot be approved without source link.
- `AI_DRAFT` cannot directly move to `QA_APPROVED`.
- Editing a QA workflow item version creates a superseded old version and a new version.
- Status changes create audit-log entries.
- Export is blocked if unresolved high-priority gaps exist.
- User without QA Approver role cannot perform QA workflow step.
- Source snippet hash is stored.
- Unapproved risk-library item cannot be used as approved basis.
- High-severity item requires SME review.
- Critic result `FAIL` blocks QA workflow step.
- Missing evidence blocks approved-style export.
- Deleting or superseding a source snippet flags linked risk items for review.
- Risk Review Package Builder creates gated review packages.
- Packages without source snippets become `INPUT_INCOMPLETE`.
- Evidence gaps can satisfy completeness when evidence links are missing.
- `NO_APPROVED_LIBRARY_MATCH` must be explicit when no approved library basis exists.
- Incomplete packages cannot run the Independent Plausibility Reviewer.
- Review-level calculation routes incomplete, quick-check, targeted-SME, and full-SME/QA items.
- Draft Risk Delta Review Pack export includes AI disclosure, workload estimate, evidence map, blocking issues, and limitations.

## MVP ingestion scope

Supported MVP inputs:

- `.txt`
- `.md`
- `.csv`
- manually entered rows

Placeholders are included for PDF, DOCX, XLSX, OCR, SharePoint/Teams, Veeva, TrackWise, and Documentum integrations.

## Validation pack

The System Validation Pack section generates draft templates for URS, FS, GxP Impact Assessment, System Risk Assessment, Data Integrity Assessment, Annex 11 checklist, Part 11 checklist, test planning, RTM, summary report template, and SOP drafts.

These are draft templates only and must be reviewed, completed, executed, and accepted under the regulated company's quality system before production use.
