import { NextResponse } from "next/server";
import { llmAdapter } from "@/src/lib/llm-adapter";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({ projectId: "project-avi-threshold" }));
  const result = await llmAdapter.generateAuthorDelta(body.projectId ?? "project-avi-threshold");
  return NextResponse.json({
    status: "AI_DRAFT",
    disclosure: "Mock Author AI generated DRAFT suggestions only. Human review is required.",
    result
  });
}
