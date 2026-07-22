import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { ReviewPack } from "@/src/lib/review-ui";
import {
  buildReviewPackCsv,
  createReviewPackPdf,
  reviewPackExportFileName
} from "@/src/lib/review-pack-export";

const pack: ReviewPack = {
  review_pack_id: "rp_123",
  document_set_id: "ds_case_42",
  decision: {
    decision: "needs_human_review",
    max_severity: "high",
    auto_clear_allowed: false,
    required_human_review_reasons: ["high risk requires review"]
  },
  summary: "Eine menschliche Prüfung ist erforderlich.",
  review_progress_percent: 0,
  reviewed_finding_count: 0,
  total_finding_count: 1,
  top_risks: [
    {
      finding_id: "finding_1",
      risk_statement: "Die Chargenbewertung ist nicht belegt.",
      severity: "high",
      risk_category: "batch_impact_assessment",
      requirement_references: ["req_batch_impact"],
      evidence_quotes: [
        {
          document_id: "doc_1",
          chunk_id: "chunk_1",
          page: 3,
          quote: "Eine Entscheidung zur Charge liegt nicht vor.",
          support_type: "direct"
        }
      ],
      found_by_agents: ["BatchImpactReviewer"],
      contradicted_by_agents: [],
      no_issue_agents: [],
      verifier_status: "verified",
      human_review_reason: "Charge prüfen"
    }
  ],
  finding_clusters: [],
  evidence_table: [
    {
      finding_id: "finding_1",
      risk_statement: "Die Chargenbewertung ist nicht belegt.",
      document_id: "doc_1",
      page: 3,
      chunk_id: "chunk_1",
      quote: "Eine Entscheidung zur Charge liegt nicht vor.",
      requirement_references: ["req_batch_impact"],
      verifier_status: "verified"
    }
  ],
  model_positions: [],
  verifier_results: [],
  ood_reasons: [],
  coverage_gap_reasons: [],
  missing_information: [],
  recommended_reviewer_actions: [],
  audit_references: []
};

describe("review pack exports", () => {
  it("builds an Excel-compatible evidence export with stable, quoted columns", () => {
    const csv = buildReviewPackCsv(pack);

    expect(csv).toContain("Prüfpunkt-ID;Risikobeschreibung;Dokument;Seite;Chunk;Zitat;Anforderungen;Verifikationsstatus");
    expect(csv).toContain("finding_1;\"Die Chargenbewertung ist nicht belegt.\";doc_1;3;chunk_1");
    expect(csv).toContain("\"Eine Entscheidung zur Charge liegt nicht vor.\"");
  });

  it("creates a downloadable PDF with the case decision and source evidence", async () => {
    const pdf = createReviewPackPdf(pack);
    const content = await pdf.text();

    expect(pdf.type).toBe("application/pdf");
    expect(content.startsWith("%PDF-1.4")).toBe(true);
    expect(content).toContain("Pr");
    expect(content).toContain("Chargenbewertung");
  });

  it("uses a safe, case-specific filename", () => {
    expect(reviewPackExportFileName(pack, "pdf")).toBe("pruefmappe-ds_case_42.pdf");
    expect(reviewPackExportFileName(pack, "csv")).toBe("pruefmappe-ds_case_42-evidenz.csv");
  });

  it("offers both exports from the review pack interface", () => {
    const exportActions = readFileSync(
      join(process.cwd(), "src/components/review-ui/review-pack-export-actions.tsx"),
      "utf8"
    );

    expect(exportActions).toContain("Prüfmappe als PDF");
    expect(exportActions).toContain("Evidenz als Excel");
  });
});
