import { NextResponse } from "next/server";
import { createDocumentSet } from "@/src/lib/review-api";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const declaredDocumentType = String(body.declaredDocumentType || "").trim();
  const declaredProcessArea = String(body.declaredProcessArea || "").trim();
  const uploadedBy = String(body.uploadedBy || "qrm_author").trim();

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
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
