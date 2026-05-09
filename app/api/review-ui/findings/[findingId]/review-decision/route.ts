import { NextResponse } from "next/server";
import { submitReviewDecision } from "@/src/lib/review-api";
import { decisionOptions, type ReviewDecisionValue } from "@/src/lib/review-ui";

type RouteContext = {
  params: Promise<{ findingId: string }>;
};

export async function POST(request: Request, context: RouteContext) {
  const { findingId } = await context.params;
  const body = await request.json().catch(() => ({}));
  const allowedDecisions = new Set(decisionOptions.map((option) => option.value));

  if (!allowedDecisions.has(body.decision)) {
    return NextResponse.json({ error: "Invalid review decision" }, { status: 422 });
  }

  if (!body.rationale || String(body.rationale).trim().length < 1) {
    return NextResponse.json({ error: "Rationale is required" }, { status: 422 });
  }

  try {
    const result = await submitReviewDecision({
      findingId,
      reviewerId: String(body.reviewerId || "reviewer_qa_1"),
      decision: body.decision as ReviewDecisionValue,
      rationale: String(body.rationale)
    });
    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Review decision failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
