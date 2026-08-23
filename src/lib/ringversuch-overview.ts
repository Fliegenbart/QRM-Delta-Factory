export type LandingProofStats = {
  foundValue: string;
  falseAlarmValue: string;
  falseAlarmLabel: string;
  citationValue: string;
  standLabel: string;
  /**
   * True when the run behind these figures used a model stack the product no
   * longer ships. The numbers were really measured, so hiding them would be
   * its own distortion -- but presenting them unqualified would claim current
   * performance for a build that has not been measured. The landing page must
   * say which of the two it is.
   */
  measuredOnFormerStack: boolean;
};

/** Stacks the shipped system can still run. Mirrors the Ringversuch dashboard. */
const CURRENT_STACKS = new Set(["mixed", "anthropic", "openai", "hetzner", "hetzner-cascade"]);

/**
 * The stack customers actually get. Ablation runs (one provider only, Qwen on
 * Hetzner, ...) are published alongside it so the comparison is inspectable,
 * but the headline figure must never be one of them: on 2026-08-23 the newest
 * live run was a Qwen ablation at 12/25, while the production stack stood at
 * 22/25 on the same corpus.
 */
export const PRODUCTION_STACK = "mixed";

export function isProductionRun(run: { run: { mode?: string; stack?: string | null } }): boolean {
  return run.run.mode === "live" && (run.run.stack ?? "") === PRODUCTION_STACK;
}

/** Newest production run; failing that, the newest live run of any stack. */
export function pickHeadlineRun<T extends { run: { mode?: string; stack?: string | null } }>(
  runs: T[] | null | undefined
): T | undefined {
  if (!runs?.length) return undefined;
  return runs.find(isProductionRun) ?? runs.find((run) => run.run.mode === "live");
}

type RingversuchRun = {
  id: string;
  run: { mode?: string; stack?: string | null };
  aggregate: {
    sensitivity?: { found: number; total: number; rate: number | null };
    specificity_decoys?: { passed: number; total: number; rate: number | null };
    citation_precision?: { verified: number; total_findings: number; rate: number | null };
  };
};

export function deriveLandingProofStats(runs?: RingversuchRun[]): LandingProofStats | undefined {
  const latestLive = pickHeadlineRun(runs);
  const sensitivity = latestLive?.aggregate.sensitivity;
  const specificity = latestLive?.aggregate.specificity_decoys;
  const citation = latestLive?.aggregate.citation_precision;
  if (!latestLive || !sensitivity || !specificity || !citation) return undefined;

  const dateMatch = latestLive.id.match(/^(\d{4})(\d{2})(\d{2})_/);
  return {
    foundValue: `${sensitivity.found} / ${sensitivity.total}`,
    falseAlarmValue: `${Math.max(specificity.total - specificity.passed, 0)}`,
    falseAlarmLabel: `Fehlalarme bei ${specificity.total} harmlosen Kontrollstellen`,
    citationValue: citation.rate == null ? "–" : `${Math.round(citation.rate * 100)} %`,
    standLabel: dateMatch
      ? `Stand ${dateMatch[3]}.${dateMatch[2]}.${dateMatch[1]}`
      : "Jüngster veröffentlichter Lauf",
    measuredOnFormerStack: !CURRENT_STACKS.has(latestLive.run.stack ?? "")
  };
}
