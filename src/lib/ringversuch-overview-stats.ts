export type LiveStats = {
  sensitivityFound: number;
  sensitivityTotal: number;
  decoysPassed: number;
  decoysTotal: number;
  citationRate: number | null;
  standDate: string;
};

export type OverviewRingversuchStats = {
  latest: LiveStats;
  best: LiveStats;
  hasBetterBestRun: boolean;
};

type RingversuchRun = {
  id?: string;
  run?: {
    mode?: unknown;
  };
  aggregate?: {
    sensitivity?: {
      found?: unknown;
      total?: unknown;
    };
    specificity_decoys?: {
      passed?: unknown;
      total?: unknown;
    };
    citation_precision?: {
      rate?: unknown;
    };
  };
};

type RingversuchPayload = {
  runs?: RingversuchRun[];
};

export const OVERVIEW_FALLBACK_STATS: OverviewRingversuchStats = {
  latest: {
    sensitivityFound: 24,
    sensitivityTotal: 25,
    decoysPassed: 11,
    decoysTotal: 11,
    citationRate: 0.928,
    standDate: "13.06.2026",
  },
  best: {
    sensitivityFound: 25,
    sensitivityTotal: 25,
    decoysPassed: 11,
    decoysTotal: 11,
    citationRate: 0.91,
    standDate: "13.06.2026",
  },
  hasBetterBestRun: true,
};

const FULL_RINGVERSUCH_ERRORS = 25;
const FULL_RINGVERSUCH_DECOYS = 11;

export function selectOverviewRingversuchStats(
  payload: RingversuchPayload | null | undefined
): OverviewRingversuchStats {
  const completeRuns = (payload?.runs ?? [])
    .filter(isCompleteLiveRun)
    .sort((left, right) => (right.id ?? "").localeCompare(left.id ?? ""));

  const latestRun = completeRuns[0];
  if (!latestRun) return OVERVIEW_FALLBACK_STATS;

  const bestRun = [...completeRuns].sort(compareBestRun)[0] ?? latestRun;
  const latest = statsFromRun(latestRun);
  const best = statsFromRun(bestRun);

  return {
    latest,
    best,
    hasBetterBestRun: best.sensitivityFound > latest.sensitivityFound,
  };
}

function isCompleteLiveRun(run: RingversuchRun): boolean {
  const sensitivity = run.aggregate?.sensitivity;
  const decoys = run.aggregate?.specificity_decoys;

  return (
    run.run?.mode === "live" &&
    readNumber(sensitivity?.found) != null &&
    readNumber(sensitivity?.total) != null &&
    readNumber(sensitivity?.total)! >= FULL_RINGVERSUCH_ERRORS &&
    readNumber(decoys?.passed) != null &&
    readNumber(decoys?.total) != null &&
    readNumber(decoys?.total)! >= FULL_RINGVERSUCH_DECOYS
  );
}

function compareBestRun(left: RingversuchRun, right: RingversuchRun): number {
  const leftStats = statsFromRun(left);
  const rightStats = statsFromRun(right);
  const leftRate = leftStats.sensitivityFound / leftStats.sensitivityTotal;
  const rightRate = rightStats.sensitivityFound / rightStats.sensitivityTotal;

  return (
    rightRate - leftRate ||
    rightStats.sensitivityFound - leftStats.sensitivityFound ||
    falseAlarmCount(leftStats) - falseAlarmCount(rightStats) ||
    (rightStats.citationRate ?? -1) - (leftStats.citationRate ?? -1) ||
    (right.id ?? "").localeCompare(left.id ?? "")
  );
}

function statsFromRun(run: RingversuchRun): LiveStats {
  return {
    sensitivityFound: readNumber(run.aggregate?.sensitivity?.found) ?? 0,
    sensitivityTotal: readNumber(run.aggregate?.sensitivity?.total) ?? 0,
    decoysPassed: readNumber(run.aggregate?.specificity_decoys?.passed) ?? 0,
    decoysTotal: readNumber(run.aggregate?.specificity_decoys?.total) ?? 0,
    citationRate: readNumber(run.aggregate?.citation_precision?.rate),
    standDate: standDateFromRunId(run.id),
  };
}

function falseAlarmCount(stats: LiveStats): number {
  return stats.decoysTotal - stats.decoysPassed;
}

function readNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function standDateFromRunId(id: string | undefined): string {
  const match = id?.match(/^(\d{4})(\d{2})(\d{2})_/);
  if (!match) return OVERVIEW_FALLBACK_STATS.latest.standDate;
  return `${match[3]}.${match[2]}.${match[1]}`;
}
