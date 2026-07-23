import { NextResponse } from "next/server";
import { approveReviewCalibrationExample, ReviewApiError } from "@/src/lib/review-api";
import { authorizeReviewApiRequest } from "@/utils/supabase/actor";

type RouteContext = {
  params: Promise<{ calibrationExampleId: string }>;
};

export async function POST(request: Request, context: RouteContext) {
  const { calibrationExampleId } = await context.params;
  const authorization = await authorizeReviewApiRequest("approve-calibration");
  if ("response" in authorization) return authorization.response;
  const body = await request.json().catch(() => ({}));

  try {
    const example = await approveReviewCalibrationExample({
      calibrationExampleId,
      approvedBy: authorization.actor.userId,
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
