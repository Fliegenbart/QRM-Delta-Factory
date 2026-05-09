import { describe, expect, it } from "vitest";
import {
  decisionOptions,
  findTopRiskById,
  normalizeReviewDecisionPayload,
  riskOrchestrationEntry,
  type ReviewPack
} from "@/src/lib/review-ui";

describe("review UI helpers", () => {
  it("marks the backend review workbench as the replacement for legacy delta analysis", () => {
    expect(riskOrchestrationEntry.replacesLegacyDeltaAnalysis).toBe(true);
    expect(riskOrchestrationEntry.legacyDeltaRoute).toBe("/delta-analysis");
    expect(riskOrchestrationEntry.reviewWorkbenchRoute).toBe("/review-ui");
    expect(riskOrchestrationEntry.demoSeedRoute).toBe("/api/review-ui/demo-seed");
    expect(riskOrchestrationEntry.workflow).toContain("Build cited claim ledger");
    expect(riskOrchestrationEntry.workflow).toContain("Fuse risk conservatively");
  });

  it("exposes the reviewer decisions required by the workflow", () => {
    expect(decisionOptions.map((option) => option.value)).toEqual([
      "confirm",
      "downgrade",
      "reject_false_positive",
      "request_more_information",
      "escalate_to_qa"
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
});
