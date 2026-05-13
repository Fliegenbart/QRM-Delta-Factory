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
import { getReviewBackendConfig } from "@/src/lib/review-runtime-config";

describe("review UI helpers", () => {
  it("marks the backend review workbench as the replacement for legacy delta analysis", () => {
    expect(riskOrchestrationEntry.replacesLegacyDeltaAnalysis).toBe(true);
    expect(riskOrchestrationEntry.legacyDeltaRoute).toBe("/delta-analysis");
    expect(riskOrchestrationEntry.reviewWorkbenchRoute).toBe("/review-ui");
    expect(riskOrchestrationEntry.name).toBe("Risk Delta Review");
    expect(riskOrchestrationEntry.shortDescription).toContain("Review Pack");
    expect(riskOrchestrationEntry.shortDescription).toContain("Quellen");
    expect(riskOrchestrationEntry.workflow).toContain("Dokumente laden");
    expect(riskOrchestrationEntry.workflow).toContain("Review Pack öffnen");
  });

  it("uses consultant-friendly copy for the backend review UI", () => {
    expect(consultantReviewCopy.workspaceTitle).toBe("Risk Delta Review");
    expect(consultantReviewCopy.workspaceDescription).toBe("Quellen rein. Review Pack raus. QA entscheidet.");
    expect(consultantReviewCopy.list.title).toBe("Review Packs");
    expect(consultantReviewCopy.list.empty).toContain("Startseite");
    expect(consultantReviewCopy.finding.title).toBe("Finding");
    expect(consultantReviewCopy.decision.savedMessage).toBe("Entscheidung gespeichert.");
    expect(reviewDecisionRequiresHumanRationale).toBe(true);
    expect(consultantReviewCopy.decision.rationaleRequired).toContain("begründen");
  });

  it("trims backend runtime environment values", () => {
    const config = getReviewBackendConfig({
      QRM_BACKEND_URL: " https://backend.example.com \n",
      QRM_BACKEND_API_KEY: " key-123\n",
      QRM_BACKEND_TENANT_ID: "tenant_demo_pharma\n",
      QRM_DEFAULT_REQUIREMENT_SET_ID: "rset_demo_gmp_qrm_2026_1\n"
    });

    expect(config).toEqual({
      backendUrl: "https://backend.example.com",
      apiKey: "key-123",
      tenantId: "tenant_demo_pharma",
      requirementSetId: "rset_demo_gmp_qrm_2026_1"
    });
  });

  it("defines a simpler case workspace structure for consultants", () => {
    expect(caseWorkspaceStructure.route).toBe("/case-workspace");
    expect(caseWorkspaceStructure.primaryTabs.map((tab) => tab.label)).toEqual([
      "Status",
      "Quellen",
      "Deltas",
      "Review",
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
    expect(aiArchitectureConcept.nonNegotiables).toContain("Keine Mehrheitsabstimmung.");
    expect(aiArchitectureConcept.nonNegotiables).toContain("QA/SME bleibt letzter Schritt.");
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
      review_pack_id: "rpack_sample",
      document_set_id: "ds_sample",
      decision: { decision: "human_review_required" },
      summary: "Human review required.",
      top_risks: [
        {
          finding_id: "finding_sample",
          risk_statement: "Potential QA approval gap.",
          severity: "high",
          risk_category: "qa_approval",
          requirement_references: ["req_sample"],
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

    expect(findTopRiskById(pack, "finding_sample")?.risk_statement).toContain("QA");
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
