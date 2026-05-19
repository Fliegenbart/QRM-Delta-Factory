import { NextResponse } from "next/server";
import { getHumanFeedbackRegistry } from "@/src/lib/review-api";

export async function GET() {
  try {
    const registry = await getHumanFeedbackRegistry();
    return NextResponse.json({ registry });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Human feedback registry failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
