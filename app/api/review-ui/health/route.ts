import { NextResponse } from "next/server";
import { getBackendHealth } from "@/src/lib/review-api";
import { authorizeReviewApiRequest } from "@/utils/supabase/actor";

export async function GET() {
  const authorization = await authorizeReviewApiRequest("read");
  if ("response" in authorization) return authorization.response;
  try {
    const health = await getBackendHealth();
    return NextResponse.json({ health });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Backend-Status konnte nicht geladen werden.";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
