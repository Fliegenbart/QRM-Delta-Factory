import { NextResponse } from "next/server";
import { uploadDocumentToDocumentSet } from "@/src/lib/review-api";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function POST(request: Request, context: RouteContext) {
  const { id } = await context.params;
  const formData = await request.formData();
  const uploadedBy = String(formData.get("uploadedBy") || "qrm_author").trim();
  const file = formData.get("file");

  if (!(file instanceof File)) {
    return NextResponse.json({ error: "Keine Datei erhalten." }, { status: 422 });
  }

  try {
    const upload = await uploadDocumentToDocumentSet({
      documentSetId: id,
      uploadedBy,
      file
    });
    return NextResponse.json({ upload }, { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Dokument konnte nicht hochgeladen werden.";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
