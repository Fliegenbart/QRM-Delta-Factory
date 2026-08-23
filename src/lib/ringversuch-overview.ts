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
  /**
   * Whether the cases were unseen when the engine that ran them was built.
   * The default corpus has been looked at during development since the
   * August 2026 rebuild, so a run on it is a regression check and the
   * landing page must not describe it as a sealed envelope.
   */
  corpusKind: CorpusKind;
  corpusLabel: string;
};

export type CorpusKind = "blind" | "regression";

type RunRef = { run: { mode?: string; stack?: string | null; corpus?: string | null; case_count?: number } };

/**
 * Runs written before the corpus was recorded all came from the default
 * goldstandard directory.
 */
export function corpusOf(run: RunRef): string {
  return run.run.corpus ?? "goldstandard";
}

export function corpusKindOf(run: RunRef): CorpusKind {
  return corpusOf(run).startsWith("blind") ? "blind" : "regression";
}

const CORPUS_LABELS: Record<string, string> = {
  goldstandard: "Goldstandard-Korpus",
  blind3: "Blindkorpus 3"
};

export function corpusLabelOf(run: RunRef): string {
  const corpus = corpusOf(run);
  const base = CORPUS_LABELS[corpus] ?? corpus;
  const count = run.run.case_count;
  const cases = count ? `${count} Fälle` : null;
  const kind = corpusKindOf(run) === "blind" ? "beim Bau der Engine nie gesehen" : "Regressionskorpus";
  return [base, cases, kind].filter(Boolean).join(", ");
}

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

export function isProductionRun(run: RunRef): boolean {
  return run.run.mode === "live" && (run.run.stack ?? "") === PRODUCTION_STACK;
}

/**
 * Newest production run on a blind corpus; failing that, the newest
 * production run; failing that, the newest live run of any stack. A blind
 * measurement outranks a newer regression check because it is the stricter
 * one -- the rule is about the kind of evidence, never about the score.
 */
export function pickHeadlineRun<T extends RunRef>(runs: T[] | null | undefined): T | undefined {
  if (!runs?.length) return undefined;
  return (
    runs.find((run) => isProductionRun(run) && corpusKindOf(run) === "blind") ??
    runs.find(isProductionRun) ??
    runs.find((run) => run.run.mode === "live")
  );
}

type RingversuchRun = {
  id: string;
  run: { mode?: string; stack?: string | null; corpus?: string | null; case_count?: number };
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
    measuredOnFormerStack: !CURRENT_STACKS.has(latestLive.run.stack ?? ""),
    corpusKind: corpusKindOf(latestLive),
    corpusLabel: corpusLabelOf(latestLive)
  };
}
