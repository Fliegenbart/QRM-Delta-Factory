import { NextResponse } from "next/server";
import { buildDemoReviewPackages, runPackagePlausibilityCheck } from "@/src/lib/risk-review-package-builder";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  if (!body.packageId && !body.package) {
    return NextResponse.json({
      input_status: "INPUT_INCOMPLETE",
      missing_inputs: ["review_package"],
      overall_result: "NOT_RUN",
      source_support: "NOT_RUN",
      risk_logic: "NOT_RUN",
      control_logic: "NOT_RUN",
      evidence_quality: "NOT_RUN",
      scoring_plausibility: "NOT_RUN",
      residual_risk_rationale: "NOT_RUN",
      contradictions_found: false,
      hallucination_risk: "NOT_ASSESSED",
      required_human_review: false,
      required_reviewer_type: [],
      blocking_issues: [
        {
          issue: "Critic AI was called without a ReviewPackage.",
          reason: "The Risk Review Package Builder and Input Completeness Gate must run before independent plausibility review.",
          source_reference: "Critic API input"
        }
      ],
      non_blocking_comments: [],
      recommended_status: "INPUT_INCOMPLETE"
    });
  }

  const packages = buildDemoReviewPackages();
  const reviewPackage = body.package ?? packages.find((pkg) => pkg.id === body.packageId);
  const result = reviewPackage
    ? await runPackagePlausibilityCheck(reviewPackage)
    : {
        input_status: "INPUT_INCOMPLETE",
        missing_inputs: ["review_package"],
        overall_result: "NOT_RUN",
        recommended_status: "INPUT_INCOMPLETE"
      };

  return NextResponse.json(result);
}
