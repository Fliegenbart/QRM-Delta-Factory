import { promises as fs } from "fs";
import path from "path";
import {
  toPublicRingversuchRun,
  type PublicRingversuchRun,
} from "@/src/lib/ringversuch-public";

const RUNS_DIR = path.join(process.cwd(), "goldstandard_pharmaqrm", "runs");

/**
 * Reads the published Ringversuch runs from disk. Server-only —
 * used by the /api/ringversuch route and for server-rendering the
 * dashboard without a client-side fetch waterfall.
 */
export async function loadPublicRingversuchRuns(): Promise<PublicRingversuchRun[]> {
  let entries: string[] = [];
  try {
    entries = await fs.readdir(RUNS_DIR);
  } catch {
    return [];
  }

  const runs: PublicRingversuchRun[] = [];
  for (const entry of entries.sort().reverse()) {
    const resultsPath = path.join(RUNS_DIR, entry, "results.json");
    try {
      const raw = await fs.readFile(resultsPath, "utf-8");
      const parsed = JSON.parse(raw);
      runs.push(
        toPublicRingversuchRun({
          id: entry,
          run: parsed.run ?? {},
          aggregate: parsed.aggregate ?? {},
          cases: parsed.cases ?? [],
        })
      );
    } catch {
      // Verzeichnisse ohne lesbares results.json werden übersprungen.
    }
  }

  return runs;
}
