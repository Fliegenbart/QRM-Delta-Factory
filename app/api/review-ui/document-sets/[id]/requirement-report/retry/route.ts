import { NextResponse } from "next/server";
import {
  getRequirementReportRetry,
  retryFailedRequirements,
  ReviewApiError
} from "@/src/lib/review-api";
import { authorizeReviewApiRequest } from "@/utils/supabase/actor";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function GET(_request: Request, context: RouteContext) {
  const { id } = await context.params;
  const authorization = await authorizeReviewApiRequest("read");
  if ("response" in authorization) return authorization.response;
  try {
    const retry = await getRequirementReportRetry(id);
    return NextResponse.json({ retry }, { headers: { "cache-control": "no-store" } });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Status der erneuten Prüfung konnte nicht geladen werden.";
    const responseStatus = error instanceof ReviewApiError && error.status ? error.status : 502;
    return NextResponse.json({ error: message }, { status: responseStatus });
  }
}

export async function POST(_request: Request, context: RouteContext) {
  const { id } = await context.params;
  // Re-judging rows is the same kind of action as running the pipeline.
  const authorization = await authorizeReviewApiRequest("run-pipeline");
  if ("response" in authorization) return authorization.response;
  try {
    const retry = await retryFailedRequirements(id);
    return NextResponse.json({ retry }, { status: 202 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Erneute Prüfung konnte nicht gestartet werden.";
    const responseStatus = error instanceof ReviewApiError && error.status ? error.status : 502;
    return NextResponse.json({ error: message }, { status: responseStatus });
  }
}
