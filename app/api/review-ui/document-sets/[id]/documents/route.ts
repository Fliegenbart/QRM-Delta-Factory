import { NextResponse } from "next/server";
import { ReviewApiError, uploadDocumentToDocumentSet } from "@/src/lib/review-api";
import { authorizeReviewApiRequest } from "@/utils/supabase/actor";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function POST(request: Request, context: RouteContext) {
  const { id } = await context.params;
  const authorization = await authorizeReviewApiRequest("upload-document");
  if ("response" in authorization) return authorization.response;
  const formData = await request.formData();
  const file = formData.get("file");

  if (!(file instanceof File)) {
    return NextResponse.json({ error: "Keine Datei erhalten." }, { status: 422 });
  }

  try {
    const upload = await uploadDocumentToDocumentSet({
      documentSetId: id,
      uploadedBy: authorization.actor.userId,
      file
    });
    return NextResponse.json({ upload }, { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Dokument konnte nicht hochgeladen werden.";
    const status = error instanceof ReviewApiError && error.status ? error.status : 502;
    return NextResponse.json({ error: message }, { status });
  }
}
