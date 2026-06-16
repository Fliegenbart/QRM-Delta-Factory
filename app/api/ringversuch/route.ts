import { promises as fs } from "fs";
import path from "path";
import { NextResponse } from "next/server";
import {
  toPublicRingversuchRun,
  type PublicRingversuchRun,
} from "@/src/lib/ringversuch-public";

export const dynamic = "force-dynamic";

const RUNS_DIR = path.join(process.cwd(), "goldstandard_pharmaqrm", "runs");

export async function GET() {
  let entries: string[] = [];
  try {
    entries = await fs.readdir(RUNS_DIR);
  } catch {
    return NextResponse.json({ runs: [] });
  }

  const runs: PublicRingversuchRun[] = [];
  for (const entry of entries.sort().reverse()) {
    const resultsPath = path.join(RUNS_DIR, entry, "results.json");
    try {
      const raw = await fs.readFile(resultsPath, "utf-8");
      const parsed = JSON.parse(raw);
      runs.push(toPublicRingversuchRun({
        id: entry,
        run: parsed.run ?? {},
        aggregate: parsed.aggregate ?? {},
        cases: parsed.cases ?? [],
      }));
    } catch {
      // Verzeichnisse ohne lesbares results.json werden übersprungen.
    }
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
