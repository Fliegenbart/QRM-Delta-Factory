import { NextResponse } from "next/server";
import { demoGaps, demoProject, demoRiskItems } from "@/src/lib/demo-data";
import { exportPackage } from "@/src/lib/qrm-engine";

export async function GET() {
  const result = exportPackage({
    project: demoProject,
    riskItems: demoRiskItems,
    gaps: demoGaps,
    approvedPackage: false
  });

  const csv = [
    "Risk ID,Process Step,Failure Mode,Status,Evidence Quality,Plausibility",
    ...demoRiskItems.map((item) =>
      [item.id, item.processStep, item.failureMode, item.status, item.evidenceStatus, item.plausibilityResult]
        .map((value) => `"${String(value).replaceAll("\"", "\"\"")}"`)
        .join(",")
    )
  ].join("\n");

  return NextResponse.json({
    markdown: result.markdown,
    csv,
    blockedAsApprovedPackage: !exportPackage({ project: demoProject, riskItems: demoRiskItems, gaps: demoGaps, approvedPackage: true }).ok
  });
}
