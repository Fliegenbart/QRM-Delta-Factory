# Pharma QRM Delta Engine

MVP/prototype web application for AI-assisted Quality Risk Management delta analysis in pharmaceutical GMP environments.

## What this MVP does

- Creates and displays a QRM project for a synthetic sterile injectable / automated visual inspection change-control scenario.
- Stores a Prisma/SQLite data model for users, projects, source documents, snippets, risk-library items, risk items, evidence, gaps, plausibility checks, red-team findings, approvals, audit logs, exports, and validation artifacts.
- Uses `MockLLMAdapter` only. No external AI API is called.
- Marks AI-generated content as `DRAFT`.
- Produces source-based draft risk updates, evidence gaps, plausibility checks, red-team missing-risk findings, a review queue, audit trail view, export preview, and draft validation-pack templates.
- Builds Risk Review Packages before independent plausibility review, so the Critic is not called on empty or incomplete technical input.
- Shows a customer-demo-ready Risk Review Summary, Risk-Based Review Queue, Evidence Map, workload-reduction estimate, and Draft Risk Delta Review Pack export.

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
- Simple local demo authentication data

## Run locally

```bash
npm install
cp .env.example .env
npm run db:setup
npm test
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Demo local users use password:

```text
demo123
```

Example users:

- `author@demo.local` as QRM Author
- `sme@demo.local` as SME Reviewer
- `qa@demo.local` as QA Approver
- `audit@demo.local` as Auditor/Read-only Inspector
- `admin@demo.local` as Admin

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

Supported demo/MVP inputs:

- `.txt`
- `.md`
- `.csv`
- manually entered rows

Placeholders are included for PDF, DOCX, XLSX, OCR, SharePoint/Teams, Veeva, TrackWise, and Documentum integrations.

## Validation pack

The System Validation Pack section generates draft templates for URS, FS, GxP Impact Assessment, System Risk Assessment, Data Integrity Assessment, Annex 11 checklist, Part 11 checklist, test planning, RTM, summary report template, and SOP drafts.

These are draft templates only and must be reviewed, completed, executed, and accepted under the regulated company's quality system before production use.
