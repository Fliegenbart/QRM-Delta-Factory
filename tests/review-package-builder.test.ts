import { describe, expect, it } from "vitest";
import {
  buildDemoReviewPackages,
  buildEvidenceMap,
  buildReviewQueue,
  calculateReviewLevel,
  canRunPlausibilityCheck,
  generateRiskDeltaReviewPack,
  inputCompletenessGate,
  runPackagePlausibilityCheck,
  summarizeWorkload,
  type ReviewPackage
} from "@/src/lib/risk-review-package-builder";

describe("RiskReviewPackageBuilder", () => {
  it("creates demo review packages and gates at least three as ready", () => {
    const packages = buildDemoReviewPackages();

    expect(packages.length).toBeGreaterThanOrEqual(5);
    expect(packages.filter((pkg) => pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK").length).toBeGreaterThanOrEqual(3);
    expect(packages.some((pkg) => pkg.package_status === "INPUT_INCOMPLETE")).toBe(true);
  });

  it("package with no source snippets becomes INPUT_INCOMPLETE", () => {
    const pkg = { ...readyPackage(), linked_source_snippets: [] };

    const result = inputCompletenessGate(pkg);

    expect(result.package_status).toBe("INPUT_INCOMPLETE");
    expect(result.missing_inputs).toContain("linked_source_snippets");
  });

  it("package with evidence gap but no evidence link can still be complete", () => {
    const pkg = { ...readyPackage(), evidence_links: [], documented_gaps: [sampleGap()] };

    const result = inputCompletenessGate(pkg);

    expect(result.package_status).toBe("READY_FOR_PLAUSIBILITY_CHECK");
    expect(result.missing_inputs).toEqual([]);
  });

  it("package with no library match becomes complete only if explicit NO_APPROVED_LIBRARY_MATCH is set", () => {
    const explicitNoMatch = { ...readyPackage(), risk_library_reference: "NO_APPROVED_LIBRARY_MATCH" as const };
    const missingNoMatch = { ...readyPackage(), risk_library_reference: undefined };

    expect(inputCompletenessGate(explicitNoMatch).package_status).toBe("READY_FOR_PLAUSIBILITY_CHECK");
    expect(inputCompletenessGate(missingNoMatch as ReviewPackage).package_status).toBe("INPUT_INCOMPLETE");
  });

  it("package marked as delta/update requires baseline_risk_item", () => {
    const pkg = { ...readyPackage(), baseline_risk_item: undefined };

    const result = inputCompletenessGate(pkg as ReviewPackage);

    expect(result.package_status).toBe("INPUT_INCOMPLETE");
    expect(result.missing_inputs).toContain("baseline_risk_item");
  });

  it("READY_FOR_PLAUSIBILITY_CHECK packages can run Critic AI", async () => {
    const pkg = readyPackage();

    expect(canRunPlausibilityCheck(pkg)).toBe(true);

    const result = await runPackagePlausibilityCheck(pkg);

    expect(result.overall_result).not.toBe("NOT_RUN");
    expect(["PASS", "PARTIAL", "FAIL", "UNCLEAR"]).toContain(result.overall_result);
  });

  it("INPUT_INCOMPLETE packages cannot run Critic AI", async () => {
    const pkg = { ...readyPackage(), package_status: "INPUT_INCOMPLETE" as const };

    expect(canRunPlausibilityCheck(pkg)).toBe(false);

    const result = await runPackagePlausibilityCheck(pkg);

    expect(result.overall_result).toBe("NOT_RUN");
    expect(result.recommended_status).toBe("INPUT_INCOMPLETE");
  });

  it("routes input incomplete packages to Author/Ops action", () => {
    const incomplete = buildDemoReviewPackages().find((pkg) => pkg.package_status === "INPUT_INCOMPLETE");

    expect(incomplete).toBeDefined();
    expect(calculateReviewLevel(incomplete!)).toBe("INPUT_INCOMPLETE");

    const [queueItem] = buildReviewQueue([incomplete!]);
    expect(queueItem.next_action).toBe("complete input");
    expect(queueItem.badges).toContain("AUTHOR_OPS_ACTION");
  });

  it("routes high severity packages to LEVEL_3_FULL_SME_QA_REVIEW", async () => {
    const pkg = readyPackage();
    const result = await runPackagePlausibilityCheck(pkg);

    expect(calculateReviewLevel(pkg, result)).toBe("LEVEL_3_FULL_SME_QA_REVIEW");
  });

  it("routes partial evidence packages to LEVEL_2_TARGETED_SME_REVIEW", async () => {
    const pkg = buildDemoReviewPackages().find((candidate) => candidate.id === "pkg-particle");
    const result = await runPackagePlausibilityCheck(pkg!);

    expect(calculateReviewLevel(pkg!, result)).toBe("LEVEL_2_TARGETED_SME_REVIEW");
  });

  it("routes quick check packages to LEVEL_1_QUICK_CHECK", async () => {
    const pkg = buildDemoReviewPackages().find((candidate) => candidate.id === "pkg-data-integrity");
    const result = await runPackagePlausibilityCheck(pkg!);

    expect(result.overall_result).toBe("PASS");
    expect(calculateReviewLevel(pkg!, result)).toBe("LEVEL_1_QUICK_CHECK");
  });

  it("evidence map distinguishes SOP_ONLY from VALIDATION_REPORT", () => {
    const dataIntegrity = buildDemoReviewPackages().find((candidate) => candidate.id === "pkg-data-integrity")!;
    const falseAccept = buildDemoReviewPackages().find((candidate) => candidate.id === "pkg-false-accept")!;

    expect(buildEvidenceMap(dataIntegrity).some((row) => row.evidence_type === "SOP_ONLY" && row.evidence_quality === "WEAK")).toBe(true);
    expect(buildEvidenceMap(falseAccept).some((row) => row.evidence_type === "VALIDATION_REPORT")).toBe(true);
  });

  it("old validation evidence for changed threshold is PARTIAL or WEAK", () => {
    const pkg = buildDemoReviewPackages().find((candidate) => candidate.id === "pkg-particle")!;
    const oldValidation = pkg.evidence_links.find((link) => link.evidence_type === "VALIDATION_REPORT");

    expect(["PARTIAL", "WEAK"]).toContain(oldValidation?.quality_status);
  });

  it("export includes AI assistance disclosure and workload estimate", async () => {
    const packages = buildDemoReviewPackages();
    const results = await runAllReady(packages);
    const exportPack = generateRiskDeltaReviewPack({ packages, results, generatedAt: "2026-05-07T12:00:00.000Z" });

    expect(exportPack.markdown).toContain("This package contains AI-assisted draft content.");
    expect(exportPack.markdown).toContain("Estimated manual baseline");
    expect(exportPack.markdown).toContain("Estimated assisted review");
  });

  it("approved export is blocked if packages are not QA approved", () => {
    const exportPack = generateRiskDeltaReviewPack({ packages: buildDemoReviewPackages(), approvedExport: true });

    expect(exportPack.ok).toBe(false);
    expect(exportPack.errors[0]).toContain("Approved export is blocked");
  });

  it("draft export is allowed with DRAFT marking", () => {
    const exportPack = generateRiskDeltaReviewPack({ packages: buildDemoReviewPackages(), approvedExport: false });

    expect(exportPack.ok).toBe(true);
    expect(exportPack.markdown).toContain("DRAFT REVIEW PACKAGE");
  });

  it("workload summary includes review reduction estimates", async () => {
    const packages = buildDemoReviewPackages();
    const results = await runAllReady(packages);
    const summary = summarizeWorkload(packages, results);

    expect(summary.manual_baseline_hours).toBe(10);
    expect(summary.assisted_review_hours).toBeGreaterThan(0);
    expect(summary.estimated_reduction_percent).toBeGreaterThan(0);
  });
});

function readyPackage(): ReviewPackage {
  const [pkg] = buildDemoReviewPackages().filter((candidate) => candidate.package_status === "READY_FOR_PLAUSIBILITY_CHECK");
  return pkg;
}

function sampleGap() {
  return {
    id: "gap-test",
    riskItemId: "risk-test",
    priority: "HIGH" as const,
    status: "OPEN" as const,
    description: "Validation addendum for the new threshold is missing.",
    question: "Which executed validation evidence supports the new threshold?"
  };
}

async function runAllReady(packages: ReviewPackage[]) {
  const results: Awaited<ReturnType<typeof runPackagePlausibilityCheck>>[] = [];
  for (const pkg of packages) {
    if (pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK") {
      results.push(await runPackagePlausibilityCheck(pkg));
    }
  }

  return Object.fromEntries(packages.filter((pkg) => pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK").map((pkg, index) => [pkg.id, results[index]]));
}
