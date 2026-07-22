import { describe, expect, it } from "vitest";
import { deriveLandingProofStats } from "@/src/lib/ringversuch-overview";

describe("landing Ringversuch stats", () => {
  it("uses the first server-ordered live run and derives its date", () => {
    expect(
      deriveLandingProofStats([
        run("20260721_120000_mock", "mock", 25, 25),
        run("20260720_120000_live", "live", 24, 25),
        run("20260719_120000_live", "live", 25, 25)
      ])
    ).toEqual({
      foundValue: "24 / 25",
      falseAlarmValue: "0",
      falseAlarmLabel: "Fehlalarme bei 11 harmlosen Kontrollstellen",
      citationValue: "93 %",
      standLabel: "Stand 20.07.2026"
    });
  });

  it("does not manufacture proof stats when no live run was published", () => {
    expect(deriveLandingProofStats([run("20260721_120000_mock", "mock", 25, 25)])).toBeUndefined();
  });
});

function run(id: string, mode: string, found: number, total: number) {
  return {
    id,
    run: { mode },
    aggregate: {
      sensitivity: { found, total, rate: found / total },
      specificity_decoys: { passed: 11, total: 11, rate: 1 },
      citation_precision: { verified: 23, total_findings: 25, rate: 0.93 }
    }
  };
}
