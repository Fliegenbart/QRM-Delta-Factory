import { NextResponse } from "next/server";
import { ReviewApiError, runPipeline } from "@/src/lib/review-api";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function POST(_request: Request, context: RouteContext) {
  const { id } = await context.params;

  try {
    const pipelineRun = await runPipeline(id);
    return NextResponse.json({ pipelineRun }, { status: 202 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Analyse konnte nicht gestartet werden.";
    const responseStatus = error instanceof ReviewApiError && error.status ? error.status : 502;
    return NextResponse.json({ error: message }, { status: responseStatus });
  }
}
