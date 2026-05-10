import { describe, expect, it } from "vitest";
import {
  caseWorkspaceStructure,
  aiArchitectureConcept,
  consultantReviewCopy,
  decisionOptions,
  findTopRiskById,
  normalizeReviewDecisionPayload,
  reviewDecisionRequiresHumanRationale,
  supabasePublicEnvKeys,
  hasSupabasePublicConfig,
  riskOrchestrationEntry,
  type ReviewPack
} from "@/src/lib/review-ui";

describe("review UI helpers", () => {
  it("marks the backend review workbench as the replacement for legacy delta analysis", () => {
    expect(riskOrchestrationEntry.replacesLegacyDeltaAnalysis).toBe(true);
    expect(riskOrchestrationEntry.legacyDeltaRoute).toBe("/delta-analysis");
    expect(riskOrchestrationEntry.reviewWorkbenchRoute).toBe("/review-ui");
    expect(riskOrchestrationEntry.demoSeedRoute).toBe("/api/review-ui/demo-seed");
    expect(riskOrchestrationEntry.name).toBe("Prüfbare Risiko-Deltas");
    expect(riskOrchestrationEntry.shortDescription).toContain("Berater");
    expect(riskOrchestrationEntry.shortDescription).toContain("Quellen");
    expect(riskOrchestrationEntry.workflow).toContain(
      "1. Demo-Fall oder Kundendokumente bereitstellen"
    );
    expect(riskOrchestrationEntry.workflow).toContain(
      "3. Review Pack für SME/QA öffnen"
    );
  });

  it("uses consultant-friendly copy for the backend review UI", () => {
    expect(consultantReviewCopy.workspaceTitle).toBe("Prüfbare Risiko-Deltas");
    expect(consultantReviewCopy.workspaceDescription).toContain("Es entscheidet nicht selbst");
    expect(consultantReviewCopy.list.title).toBe("Vorbereitete Prüfpakete");
    expect(consultantReviewCopy.finding.title).toBe("Prüfpunkt mit Quelle");
    expect(consultantReviewCopy.decision.savedMessage).toContain("Audit Trail");
    expect(reviewDecisionRequiresHumanRationale).toBe(true);
    expect(consultantReviewCopy.decision.rationaleRequired).toContain("Begründung");
  });

  it("defines a simpler case workspace structure for consultants", () => {
    expect(caseWorkspaceStructure.route).toBe("/case-workspace");
    expect(caseWorkspaceStructure.primaryTabs.map((tab) => tab.label)).toEqual([
      "Übersicht",
      "Quellen & Anforderungen",
      "Risiko-Deltas",
      "Review Queue",
      "Export"
    ]);
    expect(caseWorkspaceStructure.hiddenTechnicalPages).toContain("source-snippets");
    expect(caseWorkspaceStructure.hiddenTechnicalPages).toContain("plausibility-checks");
    expect(caseWorkspaceStructure.hiddenTechnicalPages).toContain("red-team-findings");
  });

  it("documents the AI architecture as a controlled review chain, not model voting", () => {
    expect(aiArchitectureConcept.flow.map((step) => step.id)).toEqual([
      "source",
      "primary-reviewers",
      "evidence-verifier",
      "adversarial",
      "risk-fusion",
      "human-review"
    ]);
    expect(aiArchitectureConcept.nonNegotiables).toContain("Kein simples Modell-Mehrheitsvoting.");
    expect(aiArchitectureConcept.nonNegotiables).toContain("Menschliche QA-/SME-Entscheidung bleibt der letzte Schritt.");
    expect(aiArchitectureConcept.aiRoles.map((role) => role.role)).toContain("Evidence Verifier");
  });

  it("exposes the reviewer decisions required by the workflow", () => {
    expect(decisionOptions.map((option) => option.value)).toEqual([
      "confirm",
      "downgrade",
      "reject_false_positive",
      "request_more_information",
      "escalate_to_qa"
    ]);
    expect(decisionOptions.map((option) => option.label)).toEqual([
      "Befund bestätigen",
      "Bewertung herabstufen",
      "Als Fehlalarm markieren",
      "Weitere Unterlagen anfordern",
      "An QA eskalieren"
    ]);
  });

  it("finds a risk inside a review pack by finding id", () => {
    const pack: ReviewPack = {
      review_pack_id: "rpack_demo",
      document_set_id: "ds_demo",
      decision: { decision: "human_review_required" },
      summary: "Human review required.",
      top_risks: [
        {
          finding_id: "finding_demo",
          risk_statement: "Potential QA approval gap.",
          severity: "high",
          risk_category: "qa_approval",
          requirement_references: ["req_demo"],
          evidence_quotes: [],
          found_by_agents: [],
          contradicted_by_agents: [],
          no_issue_agents: [],
          verifier_status: "partial",
          human_review_reason: "High severity requires review."
        }
      ],
      finding_clusters: [],
      evidence_table: [],
      model_positions: [],
      verifier_results: [],
      ood_reasons: [],
      coverage_gap_reasons: [],
      missing_information: [],
      recommended_reviewer_actions: [],
      audit_references: []
    };

    expect(findTopRiskById(pack, "finding_demo")?.risk_statement).toContain("QA");
    expect(findTopRiskById(pack, "finding_missing")).toBeUndefined();
  });

  it("normalizes reviewer decision payloads for the backend", () => {
    expect(
      normalizeReviewDecisionPayload({
        reviewerId: "qa_1",
        decision: "confirm",
        rationale: " Evidence and requirement basis reviewed. "
      })
    ).toEqual({
      reviewer_id: "reviewer_qa_1",
      decision: "confirm",
      rationale: "Evidence and requirement basis reviewed."
    });
  });

  it("documents the public Supabase env names used by the frontend helpers", () => {
    expect(supabasePublicEnvKeys).toEqual({
      url: "NEXT_PUBLIC_SUPABASE_URL",
      publishableKey: "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"
    });
    expect(
      hasSupabasePublicConfig({
        NEXT_PUBLIC_SUPABASE_URL: "https://example.supabase.co",
        NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "sb_publishable_example"
      })
    ).toBe(true);
    expect(hasSupabasePublicConfig({ NEXT_PUBLIC_SUPABASE_URL: "" })).toBe(false);
  });
});
