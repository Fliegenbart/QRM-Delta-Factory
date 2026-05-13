import { NextResponse } from "next/server";
import { runPipeline } from "@/src/lib/review-api";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function POST(_request: Request, context: RouteContext) {
  const { id } = await context.params;

  try {
    const pipelineRun = await runPipeline(id);
    return NextResponse.json({ pipelineRun }, { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Analyse konnte nicht gestartet werden.";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
