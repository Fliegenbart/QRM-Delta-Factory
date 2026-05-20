import { NextResponse } from "next/server";
import { runReviewCalibrationRegressionGate } from "@/src/lib/review-api";

export async function POST() {
  try {
    const gate = await runReviewCalibrationRegressionGate();
    return NextResponse.json({ gate });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Regression gate failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
