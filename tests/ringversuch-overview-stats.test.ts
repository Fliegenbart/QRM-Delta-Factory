import { describe, expect, it } from "vitest";
import { selectOverviewRingversuchStats } from "@/src/lib/ringversuch-overview-stats";

describe("overview ringversuch stats", () => {
  it("shows the latest complete live run while also keeping the best confirmed complete run", () => {
    const stats = selectOverviewRingversuchStats({
      runs: [
        run("20260613_213023_live_hybrid", 24, 25, 11, 11, 0.928),
        run("20260613_210310_live_hybrid", 2, 2, 1, 1, 1),
        run("20260613_120754_live_hybrid", 25, 25, 11, 11, 0.91),
        run("20260610_065944_mock", 3, 25, 11, 11, 1, "mock"),
      ],
    });

    expect(stats.latest.sensitivityFound).toBe(24);
    expect(stats.latest.sensitivityTotal).toBe(25);
    expect(stats.latest.standDate).toBe("13.06.2026");
    expect(stats.best.sensitivityFound).toBe(25);
    expect(stats.best.sensitivityTotal).toBe(25);
    expect(stats.best.citationRate).toBe(0.91);
    expect(stats.hasBetterBestRun).toBe(true);
  });
});

function run(
  id: string,
  found: number,
  total: number,
  decoysPassed: number,
  decoysTotal: number,
  citationRate: number | null,
  mode = "live"
) {
  return {
    id,
    run: { mode },
    aggregate: {
      sensitivity: { found, total },
      specificity_decoys: { passed: decoysPassed, total: decoysTotal },
      citation_precision: { rate: citationRate },
    },
  };
}
