type TokenUsage = {
  input_tokens?: unknown;
  output_tokens?: unknown;
  total_tokens?: unknown;
  calls?: unknown;
};

type RawRingversuchRun = {
  id: string;
  run?: {
    mode?: unknown;
    stack?: unknown;
    started_at?: unknown;
    anthropic_model?: unknown;
    openai_model?: unknown;
    mistral_model?: unknown;
  };
  aggregate?: {
    sensitivity?: {
      found?: unknown;
      total?: unknown;
      rate?: unknown;
    };
    specificity_decoys?: {
      passed?: unknown;
      total?: unknown;
      rate?: unknown;
    };
    citation_precision?: {
      verified?: unknown;
      total_findings?: unknown;
      rate?: unknown;
    };
    tokens_by_provider?: Record<string, TokenUsage>;
  };
  cases?: unknown;
};

type RawAggregate = NonNullable<RawRingversuchRun["aggregate"]>;

export type PublicRingversuchRun = {
  id: string;
  run: {
    mode?: string;
    stack?: string | null;
    started_at?: string;
  };
  aggregate: {
    sensitivity?: { found: number; total: number; rate: number | null };
    specificity_decoys?: { passed: number; total: number; rate: number | null };
    citation_precision?: { verified: number; total_findings: number; rate: number | null };
  };
};

export function toPublicRingversuchRun(run: RawRingversuchRun): PublicRingversuchRun {
  return {
    id: run.id,
    run: {
      mode: readString(run.run?.mode),
      stack: readNullableString(run.run?.stack),
      started_at: readString(run.run?.started_at),
    },
    aggregate: {
      sensitivity: readSensitivity(run.aggregate?.sensitivity),
      specificity_decoys: readSpecificity(run.aggregate?.specificity_decoys),
      citation_precision: readCitationPrecision(run.aggregate?.citation_precision),
    },
  };
}

function readSensitivity(value: RawAggregate["sensitivity"]) {
  if (!value) return undefined;
  return {
    found: readNumber(value.found) ?? 0,
    total: readNumber(value.total) ?? 0,
    rate: readNumber(value.rate),
  };
}

function readSpecificity(value: RawAggregate["specificity_decoys"]) {
  if (!value) return undefined;
  return {
    passed: readNumber(value.passed) ?? 0,
    total: readNumber(value.total) ?? 0,
    rate: readNumber(value.rate),
  };
}

function readCitationPrecision(value: RawAggregate["citation_precision"]) {
  if (!value) return undefined;
  return {
    verified: readNumber(value.verified) ?? 0,
    total_findings: readNumber(value.total_findings) ?? 0,
    rate: readNumber(value.rate),
  };
}

function readNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function readString(value: unknown): string | undefined {
  return typeof value === "string" ? value : undefined;
}

function readNullableString(value: unknown): string | null | undefined {
  if (value == null) return null;
  return readString(value);
}
