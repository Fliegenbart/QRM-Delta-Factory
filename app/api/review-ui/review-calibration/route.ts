import { NextResponse } from "next/server";
import { getReviewCalibrationReport } from "@/src/lib/review-api";

export async function GET() {
  try {
    const calibration = await getReviewCalibrationReport();
    return NextResponse.json({ calibration });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Review calibration failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
