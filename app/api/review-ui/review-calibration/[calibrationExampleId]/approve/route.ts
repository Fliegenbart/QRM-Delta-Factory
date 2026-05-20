import { NextResponse } from "next/server";
import { approveReviewCalibrationExample, ReviewApiError } from "@/src/lib/review-api";

type RouteContext = {
  params: Promise<{ calibrationExampleId: string }>;
};

export async function POST(request: Request, context: RouteContext) {
  const { calibrationExampleId } = await context.params;
  const body = await request.json().catch(() => ({}));

  try {
    const example = await approveReviewCalibrationExample({
      calibrationExampleId,
      approvedBy: String(body.approvedBy || body.approved_by || "qa_lead"),
      activate: Boolean(body.activate),
      regressionGatePassed: Boolean(body.regressionGatePassed || body.regression_gate_passed),
      regressionGateReportId: body.regressionGateReportId || body.regression_gate_report_id
    });
    return NextResponse.json({ example });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Calibration approval failed";
    const status = error instanceof ReviewApiError && error.status ? error.status : 502;
    return NextResponse.json({ error: message }, { status });
  }
}
