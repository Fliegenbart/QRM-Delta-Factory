import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    markdown: "# Keine aktive Prüfmappe\n\nLade zuerst Unterlagen hoch und starte die Prüfung.",
    csv: "",
    blockedAsApprovedPackage: true
  });
}
