import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    markdown: "# No active review pack\n\nUpload a DocumentSet and run the backend pipeline first.",
    csv: "",
    blockedAsApprovedPackage: true
  });
}
