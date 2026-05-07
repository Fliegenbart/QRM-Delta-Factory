import { NextResponse } from "next/server";
import { buildDemoReviewPackages, generateRiskDeltaReviewPack, runPackagePlausibilityCheck } from "@/src/lib/risk-review-package-builder";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const packages = body.packages ?? buildDemoReviewPackages();
  const results = body.results ?? Object.fromEntries(
    await Promise.all(
      packages
        .filter((pkg: { package_status: string }) => pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK")
        .map(async (pkg: { id: string }) => [pkg.id, await runPackagePlausibilityCheck(pkg as never)] as const)
    )
  );

  return NextResponse.json(
    generateRiskDeltaReviewPack({
      packages,
      results,
      approvedExport: Boolean(body.approvedExport)
    })
  );
}
