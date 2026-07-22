export type LandingProofStats = {
  foundValue: string;
  falseAlarmValue: string;
  falseAlarmLabel: string;
  citationValue: string;
  standLabel: string;
};

type RingversuchRun = {
  id: string;
  run: { mode?: string };
  aggregate: {
    sensitivity?: { found: number; total: number; rate: number | null };
    specificity_decoys?: { passed: number; total: number; rate: number | null };
    citation_precision?: { verified: number; total_findings: number; rate: number | null };
  };
};

export function deriveLandingProofStats(runs?: RingversuchRun[]): LandingProofStats | undefined {
  const latestLive = runs?.find((run) => run.run.mode === "live");
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
      : "Jüngster veröffentlichter Lauf"
  };
}
