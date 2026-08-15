import { describe, expect, it } from "vitest";
import { deriveLandingProofStats } from "@/src/lib/ringversuch-overview";

describe("landing Ringversuch stats", () => {
  it("uses the first server-ordered live run and derives its date", () => {
    expect(
      deriveLandingProofStats([
        run("20260721_120000_mock", "mock", 25, 25, "mixed"),
        run("20260720_120000_live", "live", 24, 25, "mixed"),
        run("20260719_120000_live", "live", 25, 25, "mixed")
      ])
    ).toEqual({
      foundValue: "24 / 25",
      falseAlarmValue: "0",
      falseAlarmLabel: "Fehlalarme bei 11 harmlosen Kontrollstellen",
      citationValue: "93 %",
      standLabel: "Stand 20.07.2026",
      measuredOnFormerStack: false
    });
  });

  it("flags figures measured on a stack the product no longer ships", () => {
    // Every published run predates the August 2026 provider change. Serving
    // those numbers to a prospect without saying so would claim current
    // performance for a build that has not been measured -- on the one page
    // whose entire argument is that nothing is claimed without evidence.
    const stats = deriveLandingProofStats([
      run("20260725_194000_live", "live", 25, 25, "hybrid")
    ]);

    expect(stats?.measuredOnFormerStack).toBe(true);
    expect(stats?.foundValue).toBe("25 / 25");
  });

  it("does not manufacture proof stats when no live run was published", () => {
    expect(
      deriveLandingProofStats([run("20260721_120000_mock", "mock", 25, 25, "mixed")])
    ).toBeUndefined();
  });
});

function run(id: string, mode: string, found: number, total: number, stack: string) {
  return {
    id,
    run: { mode, stack },
    aggregate: {
      sensitivity: { found, total, rate: found / total },
      specificity_decoys: { passed: 11, total: 11, rate: 1 },
      citation_precision: { verified: 23, total_findings: 25, rate: 0.93 }
    }
  };
}
