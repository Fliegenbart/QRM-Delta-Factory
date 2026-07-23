import { NextResponse } from "next/server";
import { runReviewCalibrationRegressionGate } from "@/src/lib/review-api";
import { authorizeReviewApiRequest } from "@/utils/supabase/actor";

export async function POST() {
  const authorization = await authorizeReviewApiRequest("run-regression");
  if ("response" in authorization) return authorization.response;
  try {
    const gate = await runReviewCalibrationRegressionGate();
    return NextResponse.json({ gate });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Regression gate failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
