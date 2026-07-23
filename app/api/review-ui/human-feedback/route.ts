import { NextResponse } from "next/server";
import { getHumanFeedbackRegistry } from "@/src/lib/review-api";
import { authorizeReviewApiRequest } from "@/utils/supabase/actor";

export async function GET() {
  const authorization = await authorizeReviewApiRequest("read");
  if ("response" in authorization) return authorization.response;
  try {
    const registry = await getHumanFeedbackRegistry();
    return NextResponse.json({ registry });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Human feedback registry failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
