import { NextResponse } from "next/server";
import { loadPublicRingversuchRuns } from "@/src/lib/ringversuch-server";

export const dynamic = "force-dynamic";

export async function GET() {
  const runs = await loadPublicRingversuchRuns();

  if (runs.length === 0) {
    return NextResponse.json({ runs: [] });
  }

  return NextResponse.json(
    {
      accessLevel: "public-summary",
      detailPolicy:
        "Public qualification route exposes aggregate metrics only. Case-level evaluation details stay internal.",
      runs,
    },
    {
      headers: {
        "cache-control": "public, max-age=60, stale-while-revalidate=300",
      },
    }
  );
}
