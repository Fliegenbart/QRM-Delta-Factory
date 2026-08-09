import { describe, expect, it } from "vitest";
import {
  buildRequirementReportCsv,
  createRequirementReportPdf,
  requirementReportFileName
} from "@/src/lib/requirement-report-export";
import {
  requirementConfidenceNotes,
  requirementCoverageProgress,
  type RequirementCoverageReport,
  type RequirementVerdictRow
} from "@/src/lib/review-ui";

function row(overrides: Partial<RequirementVerdictRow> = {}): RequirementVerdictRow {
  return {
    requirement_id: "req_threshold",
    requirement_title: "Validierung bei Schwellwertänderung",
    requirement_text: "Schwellwertänderungen erfordern aktuelle Validierungsevidenz.",
    source_name: "SOP-CC-AVI-001",
    section: "8.4",
    model_status: "violated",
    published_status: "violated",
    severity: "high",
    rationale: "Der Schwellwert wird geändert, ohne dass ein Nachweis beiliegt.",
    evidence: [
      {
        document_id: "doc_change",
        chunk_id: "chunk_change_p1",
        page: 1,
        quote: "Die QA-Freigabe ist als pending markiert."
      }
    ],
    dropped_evidence_count: 0,
    dropped_evidence_reasons: [],
    provenance_ok: true,
    entailment: "supports",
    entailment_reason: "Belege tragen die Aussage.",
    evidence_type: null,
    evidence_reference: null,
    evidence_sufficiency: null,
    independent_support: null,
    challenge_sustained: null,
    challenge_reason: null,
    sample_disagreement: false,
    validator_flags: [],
    validator_statements: [],
    server_authored: false,
    ...overrides
  };
}

function report(rows: RequirementVerdictRow[]): RequirementCoverageReport {
  return {
    document_set_id: "ds_demo",
    engine_version: "requirement-review-v0.1",
    created_at: "2026-08-06T10:00:00Z",
    verdicts: rows,
    status_counts: {},
    model_calls: [],
    failed_model_call_count: 0,
    validator_findings: []
  };
}

describe("requirement coverage export", () => {
  it("names files after the coverage report, not the finding pack", () => {
    const built = report([row()]);
    expect(requirementReportFileName(built, "pdf")).toBe(
      "anforderungsabdeckung-ds_demo.pdf"
    );
    expect(requirementReportFileName(built, "csv")).toBe(
      "anforderungsabdeckung-ds_demo.csv"
    );
  });

  it("writes one CSV line per quote and keeps the obligation's provenance", () => {
    const csv = buildRequirementReportCsv(
      report([
        row({
          evidence: [
            { document_id: "doc_a", chunk_id: "c1", page: 2, quote: "Erster Beleg." },
            { document_id: "doc_b", chunk_id: "c2", page: 5, quote: "Zweiter Beleg." }
          ]
        })
      ])
    );

    const lines = csv.trim().split("\r\n");
    expect(lines).toHaveLength(3); // header plus one row per quote
    expect(lines[0]).toContain("Anforderung");
    expect(lines[0]).toContain("Sicherheitsvermerke");
    expect(lines[1]).toContain("SOP-CC-AVI-001");
    expect(lines[1]).toContain("Erster Beleg.");
    expect(lines[2]).toContain("Zweiter Beleg.");
    expect(csv.startsWith("﻿")).toBe(true);
  });

  it("keeps a requirement without evidence in the export", () => {
    // A row the engine could not settle must not silently vanish from the
    // file that goes into the audit trail -- its absence is the finding.
    const csv = buildRequirementReportCsv(
      report([row({ published_status: "unclear", evidence: [] })])
    );

    const lines = csv.trim().split("\r\n");
    expect(lines).toHaveLength(2);
    expect(lines[1]).toContain("Unklar");
  });

  it("groups the PDF by what the reviewer must act on", () => {
    const pdf = createRequirementReportPdf(
      report([
        row({ requirement_id: "req_a", published_status: "fulfilled" }),
        row({ requirement_id: "req_b", published_status: "violated" }),
        row({
          requirement_id: "req_c",
          published_status: "not_applicable",
          server_authored: true,
          evidence: []
        })
      ])
    );

    expect(pdf.type).toBe("application/pdf");
    expect(pdf.size).toBeGreaterThan(0);
  });

  it("reports coverage as answered against needing attention", () => {
    const progress = requirementCoverageProgress(
      report([
        row({ requirement_id: "a", published_status: "violated" }),
        row({ requirement_id: "b", published_status: "unclear" }),
        row({ requirement_id: "c", published_status: "fulfilled" }),
        row({ requirement_id: "d", published_status: "not_applicable" })
      ])
    );

    expect(progress.total).toBe(4);
    expect(progress.needsAttention).toBe(2);
    expect(progress.answered).toBe(2);
    expect(progress.percent).toBe(50);
  });

  it("derives confidence notes only from recorded checks", () => {
    const notes = requirementConfidenceNotes(
      row({
        provenance_ok: false,
        dropped_evidence_count: 2,
        entailment: "partial",
        sample_disagreement: true,
        validator_statements: ["Angegebener Anteil widerspricht der Grundlage."]
      })
    );

    expect(notes).toContain("2 Zitat(e) nicht im Quelltext auffindbar");
    expect(notes.some((note) => note.includes("teilweise"))).toBe(true);
    expect(notes.some((note) => note.includes("uneins"))).toBe(true);
    expect(
      notes.some((note) => note.startsWith("Deterministische Prüfung:"))
    ).toBe(true);
  });

  it("says plainly when a row was answered without a model", () => {
    const notes = requirementConfidenceNotes(
      row({ server_authored: true, published_status: "not_applicable", evidence: [] })
    );

    expect(notes[0]).toBe("Vom Server beantwortet, ohne Modellaufruf");
  });
});
