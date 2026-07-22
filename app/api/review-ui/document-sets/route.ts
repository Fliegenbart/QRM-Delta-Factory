import { NextResponse } from "next/server";
import { createDocumentSet, ReviewApiError } from "@/src/lib/review-api";
import { resolveReviewActor } from "@/utils/supabase/actor";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const declaredDocumentType = String(body.declaredDocumentType || "").trim();
  const declaredProcessArea = String(body.declaredProcessArea || "").trim();
  const uploadedBy = await resolveReviewActor(String(body.uploadedBy || "qrm_author").trim());

  if (!declaredDocumentType || !declaredProcessArea) {
    return NextResponse.json(
      { error: "Anlass und Prozessbereich sind erforderlich." },
      { status: 422 }
    );
  }

  try {
    const documentSet = await createDocumentSet({
      declaredDocumentType,
      declaredProcessArea,
      uploadedBy
    });
    return NextResponse.json({ documentSet }, { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Fall konnte nicht angelegt werden.";
    const status = error instanceof ReviewApiError && error.status ? error.status : 502;
    return NextResponse.json({ error: message }, { status });
  }
}
