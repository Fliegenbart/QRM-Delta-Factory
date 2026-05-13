import { NextResponse } from "next/server";
import { deleteDocumentSet } from "@/src/lib/review-api";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function DELETE(_request: Request, context: RouteContext) {
  const { id } = await context.params;

  try {
    await deleteDocumentSet(id);
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Prüffall konnte nicht gelöscht werden.";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
