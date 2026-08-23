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
      measuredOnFormerStack: false,
      corpusKind: "regression",
      corpusLabel: "Goldstandard-Korpus, Regressionskorpus"
    });
  });

  it("headlines a blind-corpus production run over a newer regression run", () => {
    // The rule is about the kind of evidence: a sealed-envelope measurement
    // outranks a regression check on a corpus the team has looked at, even
    // when the regression run is newer -- and regardless of which scored
    // higher.
    const stats = deriveLandingProofStats([
      run("20260824_090000_live_mixed", "live", 24, 25, "mixed", { corpus: "goldstandard", case_count: 10 }),
      run("20260823_220000_live_mixed", "live", 11, 16, "mixed", { corpus: "blind3", case_count: 8 }),
      run("20260823_210000_live_hetzner", "live", 12, 16, "hetzner", { corpus: "blind3", case_count: 8 })
    ]);

    expect(stats?.foundValue).toBe("11 / 16");
    expect(stats?.corpusKind).toBe("blind");
    expect(stats?.corpusLabel).toBe("Blindkorpus 3, 8 Fälle, beim Bau der Engine nie gesehen");
    expect(stats?.standLabel).toBe("Stand 23.08.2026");
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

  it("headlines the production stack even when an ablation ran more recently", () => {
    // 2026-08-23: the newest live run was a Qwen-on-Hetzner ablation at 12/25,
    // the production two-provider stack stood at 22/25 on the same corpus.
    const stats = deriveLandingProofStats([
      run("20260823_005022_live_hetzner", "live", 12, 25, "hetzner"),
      run("20260822_204352_live_mixed", "live", 22, 25, "mixed"),
      run("20260725_194032_live_hybrid", "live", 25, 25, "hybrid")
    ]);

    expect(stats?.foundValue).toBe("22 / 25");
    expect(stats?.standLabel).toBe("Stand 22.08.2026");
    expect(stats?.measuredOnFormerStack).toBe(false);
  });

  it("does not manufacture proof stats when no live run was published", () => {
    expect(
      deriveLandingProofStats([run("20260721_120000_mock", "mock", 25, 25, "mixed")])
    ).toBeUndefined();
  });
});

function run(
  id: string,
  mode: string,
  found: number,
  total: number,
  stack: string,
  extra: { corpus?: string; case_count?: number } = {}
) {
  return {
    id,
    run: { mode, stack, ...extra },
    aggregate: {
      sensitivity: { found, total, rate: found / total },
      specificity_decoys: { passed: 11, total: 11, rate: 1 },
      citation_precision: { verified: 23, total_findings: 25, rate: 0.93 }
    }
  };
}
