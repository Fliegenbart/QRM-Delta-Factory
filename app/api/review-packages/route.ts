import { NextResponse } from "next/server";
import { buildDemoReviewPackages } from "@/src/lib/risk-review-package-builder";

export async function GET() {
  return NextResponse.json({ packages: buildDemoReviewPackages() });
}

export async function POST() {
  return NextResponse.json({
    disclosure: "Review packages are structured DRAFT inputs for plausibility review. They are not approvals.",
    packages: buildDemoReviewPackages()
  });
}
