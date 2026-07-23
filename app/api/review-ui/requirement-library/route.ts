import { NextResponse } from "next/server";
import {
  getRequirementLibraryOverview,
  importRequirementLibrary
} from "@/src/lib/review-api";
import { authorizeReviewApiRequest } from "@/utils/supabase/actor";

export async function GET() {
  const authorization = await authorizeReviewApiRequest("read");
  if ("response" in authorization) return authorization.response;
  try {
    const overview = await getRequirementLibraryOverview();
    return NextResponse.json({ overview });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Risikobibliothek konnte nicht geladen werden.";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}

export async function POST(request: Request) {
  const authorization = await authorizeReviewApiRequest("import-requirements");
  if ("response" in authorization) return authorization.response;
  try {
    const formData = await request.formData();
    const file = formData.get("file");
    const importedBy = authorization.actor.userId;

    if (!(file instanceof File)) {
      return NextResponse.json({ error: "Bitte eine JSON- oder YAML-Datei auswählen." }, { status: 400 });
    }

    const overview = await importRequirementLibrary({ file, importedBy });
    return NextResponse.json({ overview }, { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Risikobibliothek konnte nicht importiert werden.";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
