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
  it("keeps five verified PKG-001 risks in Kernbefunde with German text intact", async () => {
    const pkg001Pack = {
      ...pack,
      review_pack_id: "rp_pkg_001",
      document_set_id: "PKG-001",
      decision_summary:
        "Vor einer GMP-Nutzung müssen die fünf offenen Punkte durch QA bewertet werden.",
      top_risks: [
        {
          ...pack.top_risks[0],
          finding_id: "pkg001-method-limit",
          risk_statement:
            "Die Methodenvalidierung belegt die Plattform- und Methodengrenzen nicht ausreichend.",
          verifier_status: "verified"
        },
        {
          ...pack.top_risks[0],
          finding_id: "pkg001-site-equipment",
          risk_statement:
            "Die Übertragung von Standort und Equipment in den GMP-Prozess ist nicht belegt.",
          verifier_status: "strong"
        },
        {
          ...pack.top_risks[0],
          finding_id: "pkg001-qa-pending",
          risk_statement:
            "Die QA-Freigabe steht vor der GMP-Nutzung noch aus.",
          verifier_status: "verified"
        },
        {
          ...pack.top_risks[0],
          finding_id: "pkg001-sop-training",
          risk_statement:
            "Die verpflichtende Schulung zur SOP v4 ist nicht nachgewiesen.",
          verifier_status: "strong"
        },
        {
          ...pack.top_risks[0],
          finding_id: "pkg001-batch-scope",
          risk_statement:
            "A17-26044 liegt außerhalb des deklarierten Chargenumfangs.",
          verifier_status: "verified"
        }
      ],
      evidence_table: [
        {
          ...pack.evidence_table[0],
          finding_id: "pkg001-method-limit",
          risk_statement:
            "Die Methodenvalidierung belegt die Plattform- und Methodengrenzen nicht ausreichend.",
          document_id: "doc_opaque_method",
          quote: "Die Validierung gilt nur für die geprüfte Plattform.",
          verifier_status: "verified"
        },
        {
          ...pack.evidence_table[0],
          finding_id: "pkg001-site-equipment",
          risk_statement:
            "Die Übertragung von Standort und Equipment in den GMP-Prozess ist nicht belegt.",
          document_id: "doc_opaque_bridge",
          quote: "Eine dokumentierte Brücke zum GMP-Equipment fehlt.",
          verifier_status: "strong"
        },
        {
          ...pack.evidence_table[0],
          finding_id: "pkg001-qa-pending",
          risk_statement: "Die QA-Freigabe steht vor der GMP-Nutzung noch aus.",
          document_id: "doc_opaque_qa",
          quote: "Die QA-Freigabe ist noch offen.",
          verifier_status: "verified"
        },
        {
          ...pack.evidence_table[0],
          finding_id: "pkg001-sop-training",
          risk_statement: "Die verpflichtende Schulung zur SOP v4 ist nicht nachgewiesen.",
          document_id: "doc_opaque_training",
          quote: "Die verpflichtende SOP-v4-Schulung fehlt.",
          verifier_status: "strong"
        },
        {
          ...pack.evidence_table[0],
          finding_id: "pkg001-batch-scope",
          risk_statement: "A17-26044 liegt außerhalb des deklarierten Chargenumfangs.",
          document_id: "doc_opaque_batch",
          quote: "A17-26044 ist nicht im deklarierten Umfang enthalten.",
          verifier_status: "verified"
        }
      ]
    } as ReviewPack;
    const content = String.fromCharCode(
      ...new Uint8Array(await createReviewPackPdf(pkg001Pack).arrayBuffer())
    );
    const canonicalSection = content.slice(
      content.indexOf("Kernbefunde"),
      content.indexOf("Hinweise zur QA-Prüfung")
    );
    const qaHintSection = content.slice(
      content.indexOf("Hinweise zur QA-Prüfung"),
      content.indexOf("Evidenzanhang")
    );

    expect(canonicalSection).toContain("Methodenvalidierung belegt die Plattform- und Methodengrenzen");
    expect(canonicalSection).toContain("Übertragung von Standort und Equipment in den GMP-Prozess");
    expect(canonicalSection).toContain("QA-Freigabe steht vor der GMP-Nutzung noch aus");
    expect(canonicalSection).toContain("verpflichtende Schulung zur SOP v4 ist nicht nachgewiesen");
    expect(canonicalSection).toContain("A17-26044 liegt außerhalb des deklarierten Chargenumfangs");
    expect(canonicalSection.match(/Verifier-Status: (?:verified|strong)/g)).toHaveLength(5);
    expect(qaHintSection).toContain("Keine nicht-kanonischen QA-Hinweise vorhanden.");
    expect(content).toContain("Quelle doc_opaque_method, Seite 3");
    expect(content).toContain("Quelle doc_opaque_bridge, Seite 3");
    expect(content).toContain("Quelle doc_opaque_qa, Seite 3");
    expect(content).toContain("Quelle doc_opaque_training, Seite 3");
    expect(content).toContain("Quelle doc_opaque_batch, Seite 3");
  });

  it("builds an Excel-compatible evidence export with stable, quoted columns", () => {
    const csv = buildReviewPackCsv(pack);

    expect(csv).toContain("Prüfpunkt-ID;Risikobeschreibung;Dokument;Seite;Chunk;Zitat;Anforderungen;Verifikationsstatus");
    expect(csv).toContain("finding_1;\"Die Chargenbewertung ist nicht belegt.\";doc_1;3;chunk_1");
    expect(csv).toContain("\"Eine Entscheidung zur Charge liegt nicht vor.\"");
  });

  it("prefers human-readable document names in CSV and PDF, with ID fallback", async () => {
    const namedPack: ReviewPack = {
      ...pack,
      evidence_table: [
        {
          ...pack.evidence_table[0],
          document_name: "Änderungskontrolle Prüfung.pdf"
        }
      ]
    };

    const namedCsv = buildReviewPackCsv(namedPack);
    const namedPdf = String.fromCharCode(
      ...new Uint8Array(await createReviewPackPdf(namedPack).arrayBuffer())
    );
    const fallbackPdf = String.fromCharCode(
      ...new Uint8Array(await createReviewPackPdf(pack).arrayBuffer())
    );

    expect(namedCsv).toContain("Änderungskontrolle Prüfung.pdf");
    expect(namedPdf).toContain("Quelle Änderungskontrolle Prüfung.pdf, Seite 3");
    expect(buildReviewPackCsv(pack)).toContain(";doc_1;3;");
    expect(fallbackPdf).toContain("Quelle doc_1, Seite 3");
  });

  it("creates a downloadable PDF with the case decision and source evidence", async () => {
    const pdf = createReviewPackPdf(pack);
    const content = await pdf.text();

    expect(pdf.type).toBe("application/pdf");
    expect(content.startsWith("%PDF-1.4")).toBe(true);
    expect(content).toContain("Pr");
    expect(content).toContain("Chargenbewertung");
  });

  it("separates canonical risks from non-canonical QA hints and keeps evidence in an appendix", async () => {
    const pdf = createReviewPackPdf({
      ...pack,
      decision: {
        ...pack.decision
      },
      decision_summary: "QA muss die Chargenauswirkung vor der Freigabe bewerten.",
      raw_finding_count: 2,
      operational_warnings: ["Ein Prüfschritt konnte technisch nicht vollständig abgedeckt werden."],
      top_risks: [
        {
          ...pack.top_risks[0],
          supporting_finding_ids: ["finding_support"],
          supporting_finding_count: 1
        },
        {
          ...pack.top_risks[0],
          finding_id: "finding_support",
          risk_statement: "Unterstützendes Teilsignal zur Chargenbewertung.",
          severity: "medium"
        }
      ]
    });
    const content = String.fromCharCode(...new Uint8Array(await pdf.arrayBuffer()));

    expect(content).toContain("Prüfmappe");
    expect(content).toContain("QA-Entscheidung");
    expect(content).toContain("Kernbefunde");
    expect(content).toContain("Hinweise zur QA-Prüfung");
    expect(content).not.toContain("NICHT KANONISCH");
    expect(content).toContain("Evidenzanhang");
    expect(content).toContain("QA muss die Chargenauswirkung vor der Freigabe bewerten.");
    expect(content).toContain("Technische Hinweise");
    expect(content).toContain("Verifier-Status: verified");
    expect(content.split("Die Chargenbewertung ist nicht belegt.")).toHaveLength(2);
    expect(content).toContain("Unterstützendes Teilsignal zur Chargenbewertung.");
  });

  it("exports German text with PDF font encoding and hides raw machine phrasing", async () => {
    const pdf = createReviewPackPdf({
      ...pack,
      decision_summary: "QA-Prüfung erforderlich: Spezifikation, Geräteäquivalenz und Schulung prüfen.",
      top_risks: [
        {
          ...pack.top_risks[0],
          verifier_status: "partial",
          risk_statement: "Geräteäquivalenz, Präzision und Rückstellmuster müssen geprüft werden.",
          human_review_reason: "single high/critical finding is sufficient for human review"
        }
      ],
      evidence_table: []
    });
    const content = String.fromCharCode(...new Uint8Array(await pdf.arrayBuffer()));

    expect(content).toContain("/Encoding /WinAnsiEncoding");
    expect(content).toContain("QA-Prüfung erforderlich");
    expect(content).toContain("Geräteäquivalenz, Präzision und Rückstellmuster");
    expect(content).not.toContain("single high/critical finding");
    expect(content).not.toContain("NICHT KANONISCH");
  });

  it("wraps combined QA-step reasons and cleans evidence markdown artifacts", async () => {
    const pdf = createReviewPackPdf({
      ...pack,
      top_risks: [
        {
          ...pack.top_risks[0],
          verifier_status: "partial",
          human_review_reason:
            "single high/critical finding is sufficient for human review; adversarial challenge involves possible high/critical risk; required knowledge pack not retrieved: contradiction_patterns; verifier did not pass all deterministic checks"
        }
      ],
      evidence_table: [
        {
          ...pack.evidence_table[0],
          quote: "?**Datum:** 2026-03-21 ?**Dokumenttyp:** Batch Record mit **A17-26044** Retest."
        }
      ]
    });
    const content = String.fromCharCode(...new Uint8Array(await pdf.arrayBuffer()));
    const qaStepLines = content.split("\n").filter((line) => line.includes("QA-Schritt:"));

    expect(content).not.toContain("single high/critical finding");
    expect(content).not.toContain("adversarial challenge involves");
    expect(content).not.toContain("?**");
    expect(content).not.toContain("**A17-26044**");
    expect(content).toContain("Datum: 2026-03-21");
    expect(content).toContain("A17-26044 Retest");
    expect(qaStepLines.length).toBeGreaterThan(0);
    expect(Math.max(...qaStepLines.map((line) => line.length))).toBeLessThan(150);
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
