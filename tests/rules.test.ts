import { describe, expect, it } from "vitest";
import {
  approveRiskItem,
  canUseLibraryItemAsApprovedBasis,
  classifyReviewLevel,
  createSourceSnippet,
  deleteSourceSnippet,
  editApprovedRiskItem,
  exportPackage,
  transitionRiskStatus
} from "@/src/lib/qrm-engine";

describe("Pharma QRM Delta Engine safety rules", () => {
  it("risk item cannot be approved without a source link", () => {
    const result = approveRiskItem({
      item: {
        ...sampleRiskItem(),
        sourceLinks: [],
        status: "QA_APPROVAL_REQUIRED"
      },
      user: qaApprover()
    });

    expect(result.ok).toBe(false);
    expect(result.errors).toContain("At least one source link is required.");
  });

  it("AI_DRAFT cannot be directly QA_APPROVED", () => {
    const result = transitionRiskStatus({
      item: sampleRiskItem({ status: "AI_DRAFT" }),
      to: "QA_APPROVED",
      user: qaApprover(),
      reason: "attempted shortcut"
    });

    expect(result.ok).toBe(false);
    expect(result.errors).toContain("AI_DRAFT cannot move directly to QA_APPROVED.");
  });

  it("approved item edit creates a new version", () => {
    const edited = editApprovedRiskItem(sampleRiskItem({ status: "QA_APPROVED", version: 3 }), {
      potentialCause: "Threshold configuration changed"
    });

    expect(edited.oldItem.status).toBe("SUPERSEDED");
    expect(edited.newItem.version).toBe(4);
    expect(edited.newItem.status).toBe("AUTHOR_REVIEWED");
  });

  it("audit log entry is created for status change", () => {
    const result = transitionRiskStatus({
      item: sampleRiskItem({ status: "AUTHOR_REVIEWED" }),
      to: "SME_REVIEW_REQUIRED",
      user: author(),
      reason: "high severity needs SME"
    });

    expect(result.ok).toBe(true);
    expect(result.auditLog?.action).toBe("STATUS_CHANGED");
    expect(result.auditLog?.previousEventHash).toBeDefined();
  });

  it("export is blocked if unresolved high-priority gaps exist", () => {
    const result = exportPackage({
      project: sampleProject(),
      riskItems: [sampleRiskItem()],
      gaps: [{ id: "gap-1", priority: "HIGH", status: "OPEN", description: "Training record missing" }],
      approvedPackage: true
    });

    expect(result.ok).toBe(false);
    expect(result.errors).toContain("Approved-style export is blocked while CRITICAL or HIGH gaps remain open.");
  });

  it("user without QA Approver role cannot approve", () => {
    const result = approveRiskItem({
      item: sampleRiskItem({ status: "QA_APPROVAL_REQUIRED" }),
      user: author()
    });

    expect(result.ok).toBe(false);
    expect(result.errors).toContain("Only a QA Approver can perform this approval step.");
  });

  it("source snippet hash is stored", () => {
    const snippet = createSourceSnippet({
      id: "snip-1",
      documentId: "doc-1",
      documentType: "SOP",
      sectionTitle: "AVI rejection threshold",
      lineReference: "lines 1-4",
      text: "Reject threshold must be verified before batch use."
    });

    expect(snippet.snippetHash).toMatch(/^[a-f0-9]{64}$/);
  });

  it("risk library unapproved item cannot be used as approved basis", () => {
    expect(
      canUseLibraryItemAsApprovedBasis({
        id: "lib-1",
        approvalStatus: "DRAFT",
        retired: false
      })
    ).toBe(false);
  });

  it("high-severity item requires SME review", () => {
    expect(classifyReviewLevel(sampleRiskItem({ severity: 5, sourceLinks: ["snip-1"] }))).toBe(3);
  });

  it("item with critic result FAIL cannot be approved", () => {
    const result = approveRiskItem({
      item: sampleRiskItem({ plausibilityResult: "FAIL", status: "QA_APPROVAL_REQUIRED" }),
      user: qaApprover()
    });

    expect(result.ok).toBe(false);
    expect(result.errors).toContain("Plausibility check must not be FAIL or UNCLEAR.");
  });

  it("item with missing evidence cannot be exported as approved", () => {
    const result = exportPackage({
      project: sampleProject(),
      riskItems: [sampleRiskItem({ evidenceStatus: "MISSING" })],
      gaps: [],
      approvedPackage: true
    });

    expect(result.ok).toBe(false);
    expect(result.errors).toContain("Approved-style export is blocked while risk items have missing evidence.");
  });

  it("source deletion flags linked risk items for review", () => {
    const result = deleteSourceSnippet("snip-1", [sampleRiskItem({ sourceLinks: ["snip-1"] })]);

    expect(result.flaggedRiskItems[0].reviewStatus).toBe("SME_REVIEW_REQUIRED");
    expect(result.flaggedRiskItems[0].deterministicGateResult).toBe("SOURCE_SUPERSEDED_REVIEW_REQUIRED");
  });
});

function sampleProject() {
  return {
    id: "project-1",
    name: "AVI threshold change QRM",
    scopeStatement: "Sterile injectable AVI threshold change",
    outOfScopeStatement: "Manual visual inspection program",
    methodology: "FMEA"
  };
}

function sampleRiskItem(overrides = {}) {
  return {
    id: "risk-1",
    projectId: "project-1",
    processStep: "Automated visual inspection",
    gmpArea: "sterile manufacturing",
    failureMode: "False accept of defective container",
    potentialCause: "Modified rejection threshold not fully verified",
    potentialEffect: "Defective unit could remain in accepted population",
    impactCategories: ["PATIENT_SAFETY", "PRODUCT_QUALITY"],
    existingControls: ["AVI recipe verification"],
    sourceLinks: ["snip-1"],
    libraryItemId: "lib-1",
    severity: 4,
    occurrence: 2,
    detectability: 3,
    humanSeverity: 4,
    humanOccurrence: 2,
    humanDetectability: 3,
    residualRiskRationale: "Human draft rationale entered for QA review.",
    proposedControls: ["Threshold verification challenge set"],
    requiredEvidence: ["Validation report covering new threshold"],
    evidenceStatus: "SUFFICIENT_FOR_DRAFT",
    confidence: "MEDIUM",
    priority: "HIGH",
    deterministicGateResult: "PASS",
    plausibilityResult: "PASS",
    redTeamResult: "NO_ADDITIONAL_RISK_IDENTIFIED",
    reviewLevel: 2,
    reviewStatus: "QA_APPROVAL_REQUIRED",
    status: "QA_APPROVAL_REQUIRED",
    version: 1,
    ...overrides
  } as const;
}

function qaApprover() {
  return { id: "user-qa", name: "QA Approver", role: "QA_APPROVER" } as const;
}

function author() {
  return { id: "user-author", name: "QRM Author", role: "QRM_AUTHOR" } as const;
}
