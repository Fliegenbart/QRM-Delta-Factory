import { NextResponse } from "next/server";
import { getLatestPipelineRun, ReviewApiError, runPipeline } from "@/src/lib/review-api";
import { authorizeReviewApiRequest } from "@/utils/supabase/actor";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function GET(_request: Request, context: RouteContext) {
  const { id } = await context.params;
  const authorization = await authorizeReviewApiRequest("read");
  if ("response" in authorization) return authorization.response;

  try {
    const pipelineRun = await getLatestPipelineRun(id);
    return NextResponse.json({ pipelineRun }, { headers: { "cache-control": "no-store" } });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Analyse-Status konnte nicht geladen werden.";
    const responseStatus = error instanceof ReviewApiError && error.status ? error.status : 502;
    return NextResponse.json({ error: message }, { status: responseStatus });
  }
}

export async function POST(_request: Request, context: RouteContext) {
  const { id } = await context.params;
  const authorization = await authorizeReviewApiRequest("run-pipeline");
  if ("response" in authorization) return authorization.response;

  try {
    const pipelineRun = await runPipeline(id);
    return NextResponse.json({ pipelineRun }, { status: 202 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Analyse konnte nicht gestartet werden.";
    const responseStatus = error instanceof ReviewApiError && error.status ? error.status : 502;
    return NextResponse.json({ error: message }, { status: responseStatus });
  }
}
