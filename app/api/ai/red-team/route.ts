import { NextResponse } from "next/server";
import { llmAdapter } from "@/src/lib/llm-adapter";

export async function POST() {
  const result = await llmAdapter.runRedTeam("project-avi-threshold");
  return NextResponse.json({
    disclosure: "Red-team findings become draft gaps or SME questions, never automatic risk-item decisions.",
    result
  });
}
