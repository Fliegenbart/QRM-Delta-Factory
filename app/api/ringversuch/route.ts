import { promises as fs } from "fs";
import path from "path";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const RUNS_DIR = path.join(process.cwd(), "goldstandard_pharmaqrm", "runs");

type RunPayload = {
  id: string;
  run: Record<string, unknown>;
  aggregate: Record<string, unknown>;
  cases: Array<Record<string, unknown>>;
};

export async function GET() {
  let entries: string[] = [];
  try {
    entries = await fs.readdir(RUNS_DIR);
  } catch {
    return NextResponse.json({ runs: [] });
  }

  const runs: RunPayload[] = [];
  for (const entry of entries.sort().reverse()) {
    const resultsPath = path.join(RUNS_DIR, entry, "results.json");
    try {
      const raw = await fs.readFile(resultsPath, "utf-8");
      const parsed = JSON.parse(raw);
      runs.push({
        id: entry,
        run: parsed.run ?? {},
        aggregate: parsed.aggregate ?? {},
        cases: parsed.cases ?? [],
      });
    } catch {
      // Verzeichnisse ohne lesbares results.json werden übersprungen.
    }
  }

  return NextResponse.json({ runs });
}
