import { NextResponse } from "next/server";
import { buildDemoReviewPackages, runPackagePlausibilityCheck } from "@/src/lib/risk-review-package-builder";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const packages = buildDemoReviewPackages();
  const reviewPackage = packages.find((pkg) => pkg.id === body.packageId) ?? body.package;

  if (!reviewPackage) {
    return NextResponse.json({
      input_status: "INPUT_INCOMPLETE",
      missing_inputs: ["review_package"],
      overall_result: "NOT_RUN",
      recommended_status: "INPUT_INCOMPLETE"
    });
  }

  const result = await runPackagePlausibilityCheck(reviewPackage);
  return NextResponse.json(result);
}
