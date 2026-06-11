"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  CheckCircle2,
  Crosshair,
  FileSearch,
  ShieldCheck,
  XCircle,
} from "lucide-react";

/* ----- Datentypen (Spiegel von results.json des Eval-Harness) ----- */

type TokenUsage = {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  calls: number;
};

type MatchedError = {
  error_id: string;
  severity: string;
  error_type?: string;
  expected_reviewer_finding?: string;
  match: {
    score: number;
    method: string;
    risk_statement?: string;
  } | null;
};

type CaseResult = {
  case_id: string;
  pipeline_status: string;
  claim_count: number;
  finding_count: number;
  citation_verified_finding_count: number;
  risk_decision: string | null;
  gold_error_count: number;
  matched_errors: MatchedError[];
  missed_errors: MatchedError[];
  decoy_count: number;
  decoy_false_alarms: Array<Record<string, unknown>>;
  tokens_by_provider?: Record<string, TokenUsage>;
};

type RunMeta = {
  mode?: string;
  stack?: string | null;
  started_at?: string;
  anthropic_model?: string | null;
  openai_model?: string | null;
  mistral_model?: string | null;
};

type Aggregate = {
  sensitivity?: { found: number; total: number; rate: number | null };
  specificity_decoys?: { passed: number; total: number; rate: number | null };
  citation_precision?: { verified: number; total_findings: number; rate: number | null };
  tokens_by_provider?: Record<string, TokenUsage>;
};

type RingversuchRun = {
  id: string;
  run: RunMeta;
  aggregate: Aggregate;
  cases: CaseResult[];
};

/* ----- Hilfsfunktionen ----- */

const stackLabels: Record<string, string> = {
  frontier: "Frontier-Stack (Claude + GPT)",
  eu: "EU-Stack (nur Mistral)",
  hybrid: "Hybrid-Stack (Mistral + KI-Kritiker)",
};

function stackLabel(run: RunMeta): string {
  if (run.mode === "mock") return "Baseline ohne KI (Regex)";
  return stackLabels[run.stack ?? ""] ?? run.stack ?? "Früher KI-Lauf";
}

function percent(rate: number | null | undefined): string {
  if (rate == null) return "–";
  return `${(Math.round(rate * 1000) / 10).toLocaleString("de-DE")} %`;
}

function severityClasses(severity: string): string {
  switch (severity) {
    case "critical":
      return "bg-danger-50 text-danger-700 border-danger-200 dark:bg-danger-900/30 dark:text-danger-300 dark:border-danger-800";
    case "high":
      return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800";
    default:
      return "bg-[var(--surface-secondary)] text-[var(--text-secondary)] border-[var(--border-default)]";
  }
}

function formatTimestamp(id: string): string {
  // Verzeichnisname: YYYYMMDD_HHMMSS_<label>
  const m = id.match(/^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})/);
  if (!m) return id;
  return `${m[3]}.${m[2]}.${m[1]}, ${m[4]}:${m[5]} Uhr`;
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toLocaleString("de-DE", { maximumFractionDigits: 2 })} Mio.`;
  if (n >= 1_000) return `${Math.round(n / 1_000).toLocaleString("de-DE")} Tsd.`;
  return n.toLocaleString("de-DE");
}

const severityLabels: Record<string, string> = {
  critical: "Kritisch",
  high: "Hoch",
  medium: "Mittel",
  low: "Niedrig",
};

const statusLabels: Record<string, string> = {
  completed: "Abgeschlossen",
  needs_human_review: "Zur QA-Prüfung",
  failed: "Fehlgeschlagen",
  harness_error: "Abbruch",
};

const providerLabels: Record<string, string> = {
  mistral: "Mistral – Fach-Reviewer",
  anthropic: "Claude – KI-Kritiker",
  openai: "GPT – KI-Kritiker",
  "extraction:mistral": "Mistral – Aussagen-Extraktion",
  "extraction:anthropic": "Claude – Aussagen-Extraktion",
};

/* ----- Hauptkomponente ----- */

export function RingversuchDashboard() {
  const [runs, setRuns] = useState<RingversuchRun[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/ringversuch")
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((payload: { runs: RingversuchRun[] }) => {
        if (cancelled) return;
        setRuns(payload.runs);
        const firstLive = payload.runs.find((run) => run.run.mode === "live");
        setSelectedId((firstLive ?? payload.runs[0])?.id ?? null);
      })
      .catch((cause: Error) => {
        if (!cancelled) setError(cause.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const selected = useMemo(
    () => runs?.find((run) => run.id === selectedId) ?? null,
    [runs, selectedId]
  );

  if (error) {
    return (
      <PanelMessage
        title="Ringversuchsdaten nicht verfügbar"
        body={`Die Ergebnisberichte konnten nicht geladen werden (${error}). Bitte Seite neu laden — falls das Problem bleibt, fehlt das Verzeichnis goldstandard_pharmaqrm/runs/.`}
      />
    );
  }
  if (runs == null) {
    return <PanelMessage title="Lade Ringversuchsdaten…" body="Die Ergebnisberichte der Testdurchläufe werden eingelesen." />;
  }
  if (runs.length === 0) {
    return (
      <PanelMessage
        title="Noch keine Testdurchläufe vorhanden"
        body="Sobald ein Ringversuch durchgeführt wurde, erscheinen die Ergebnisse hier automatisch. (Start über den Eval-Harness im Backend, siehe README.)"
      />
    );
  }

  return (
    <div className="space-y-10">
      <div>
        <h2 className="text-[18px] font-medium text-[var(--text-primary)]">
          Ringversuch — Qualifizierungsnachweis
        </h2>
        <p className="mt-1 max-w-3xl text-[13px] leading-6 text-[var(--text-secondary)]">
          Wie bei einem Laborringversuch wird das System mit Prüfaufgaben getestet, deren
          Lösungen vorab feststehen: zehn erfundene, aber realistische GMP-Fälle, in denen
          Fehler bewusst versteckt wurden — plus Kontrollstellen, die verdächtig aussehen,
          aber in Ordnung sind. So lässt sich schwarz auf weiß messen, was das System
          findet, was es übersieht und ob es falschen Alarm schlägt.
        </p>
      </div>

      {selected ? <KpiRow run={selected} /> : null}

      <section>
        <SectionHeading
          title="Lauf-Historie"
          description="Jede Zeile ist ein kompletter Testdurchlauf über alle zehn Fälle — von der ersten Baseline ohne KI bis zum aktuellen Stand. Zeile anklicken für die Details."
        />
        <RunHistoryTable runs={runs} selectedId={selectedId} onSelect={setSelectedId} />
      </section>

      {selected ? (
        <>
          <section>
            <SectionHeading
              title={`Fall-Matrix — ${stackLabel(selected.run)}`}
              description="Pro Prüffall: Welche versteckten Fehler wurden gefunden (✓) oder übersehen (✗)? Und hat das System die harmlosen Kontrollstellen in Ruhe gelassen?"
            />
            <CaseMatrix cases={selected.cases} />
            <ChipLegend />
          </section>

          {selected.aggregate.tokens_by_provider &&
          Object.keys(selected.aggregate.tokens_by_provider).length > 0 ? (
            <section>
              <SectionHeading
                title="Token-Verbrauch"
                description="Gemessener Verbrauch pro KI-Dienst für diesen Lauf. Zur Einordnung: Ein kompletter Durchlauf über zehn Fälle kostet wenige Euro."
              />
              <TokenTable tokens={selected.aggregate.tokens_by_provider} />
            </section>
          ) : null}
        </>
      ) : null}
    </div>
  );
}

/* ----- KPI-Kacheln ----- */

function KpiRow({ run }: { run: RingversuchRun }) {
  const sens = run.aggregate.sensitivity;
  const spec = run.aggregate.specificity_decoys;
  const cite = run.aggregate.citation_precision;
  return (
    <div className="grid gap-3 sm:grid-cols-3">
      <KpiCard
        icon={Crosshair}
        label="Sensitivität"
        question="Findet das System die versteckten Fehler?"
        value={percent(sens?.rate)}
        detail={sens ? `${sens.found} von ${sens.total} versteckten Fehlern gefunden` : "–"}
      />
      <KpiCard
        icon={ShieldCheck}
        label="Spezifität"
        question="Bleibt es bei Harmlosem ruhig?"
        value={percent(spec?.rate)}
        detail={
          spec
            ? `${spec.passed} von ${spec.total} Kontrollstellen korrekt nicht beanstandet`
            : "–"
        }
      />
      <KpiCard
        icon={FileSearch}
        label="Belegtreue"
        question="Ist jeder Befund mit Zitat belegt?"
        value={percent(cite?.rate)}
        detail={
          cite
            ? `${cite.verified} von ${cite.total_findings} Befunden mit wortwörtlich geprüftem Zitat`
            : "–"
        }
      />
    </div>
  );
}

function KpiCard({
  icon: Icon,
  label,
  question,
  value,
  detail,
}: {
  icon: typeof Crosshair;
  label: string;
  question: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4">
      <div className="flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
        <Icon className="h-3.5 w-3.5" aria-hidden />
        {label}
      </div>
      <div className="mt-1 text-[12px] text-[var(--text-secondary)]">{question}</div>
      <div className="mt-2 text-[28px] font-semibold leading-none text-[var(--text-primary)]">
        {value}
      </div>
      <div className="mt-2 text-[12px] leading-5 text-[var(--text-tertiary)]">{detail}</div>
    </div>
  );
}

/* ----- Lauf-Historie ----- */

function RunHistoryTable({
  runs,
  selectedId,
  onSelect,
}: {
  runs: RingversuchRun[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="overflow-x-auto rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)]">
      <table className="w-full min-w-[760px] text-left text-[13px]">
        <thead>
          <tr className="border-b border-[var(--border-default)] text-[11px] uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            <th className="px-4 py-2.5 font-medium">Zeitpunkt</th>
            <th className="px-4 py-2.5 font-medium">System-Aufbau</th>
            <th className="px-4 py-2.5 font-medium">Sensitivität</th>
            <th className="px-4 py-2.5 font-medium">Spezifität</th>
            <th className="px-4 py-2.5 font-medium">Belegtreue</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => {
            const sens = run.aggregate.sensitivity;
            const spec = run.aggregate.specificity_decoys;
            const cite = run.aggregate.citation_precision;
            const isSelected = run.id === selectedId;
            return (
              <tr
                key={run.id}
                onClick={() => onSelect(run.id)}
                aria-selected={isSelected}
                className={`cursor-pointer border-b border-[var(--border-default)] last:border-b-0 transition-colors ${
                  isSelected
                    ? "bg-[var(--brand-soft)]"
                    : "hover:bg-[var(--surface-secondary)]"
                }`}
              >
                <td className="px-4 py-2.5 text-[var(--text-secondary)]">
                  <span className="mono">{formatTimestamp(run.id)}</span>
                </td>
                <td className="px-4 py-2.5">
                  <span
                    className={`font-medium ${
                      isSelected ? "text-[var(--brand-strong)]" : "text-[var(--text-primary)]"
                    }`}
                  >
                    {stackLabel(run.run)}
                  </span>
                </td>
                <td className="px-4 py-2.5">
                  {sens ? (
                    <span className="text-[var(--text-primary)]">
                      {sens.found}/{sens.total}{" "}
                      <span className="text-[var(--text-tertiary)]">({percent(sens.rate)})</span>
                    </span>
                  ) : (
                    "–"
                  )}
                </td>
                <td className="px-4 py-2.5">
                  {spec ? `${spec.passed}/${spec.total}` : "–"}
                </td>
                <td className="px-4 py-2.5">{percent(cite?.rate)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/* ----- Fall-Matrix ----- */

function CaseMatrix({ cases }: { cases: CaseResult[] }) {
  return (
    <div className="overflow-x-auto rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)]">
      <table className="w-full min-w-[860px] text-left text-[13px]">
        <thead>
          <tr className="border-b border-[var(--border-default)] text-[11px] uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            <th className="px-4 py-2.5 font-medium">Fall</th>
            <th className="px-4 py-2.5 font-medium">Ergebnis</th>
            <th className="px-4 py-2.5 font-medium">Aussagen</th>
            <th className="px-4 py-2.5 font-medium">Befunde</th>
            <th className="px-4 py-2.5 font-medium">Versteckte Fehler</th>
            <th className="px-4 py-2.5 font-medium">Kontrollstellen</th>
          </tr>
        </thead>
        <tbody>
          {cases.map((caseResult) => (
            <tr
              key={caseResult.case_id}
              className="border-b border-[var(--border-default)] align-top last:border-b-0"
            >
              <td className="px-4 py-2.5 font-medium text-[var(--text-primary)]">
                <span className="mono">{caseResult.case_id}</span>
              </td>
              <td className="px-4 py-2.5">
                <StatusBadge status={caseResult.pipeline_status} />
              </td>
              <td className="px-4 py-2.5 text-[var(--text-secondary)]">{caseResult.claim_count}</td>
              <td className="px-4 py-2.5 text-[var(--text-secondary)]">
                {caseResult.finding_count}
                <span className="text-[var(--text-tertiary)]">
                  {" "}
                  · {caseResult.citation_verified_finding_count} mit Zitat belegt
                </span>
              </td>
              <td className="px-4 py-2.5">
                <div className="flex flex-wrap gap-1.5">
                  {caseResult.matched_errors.map((matched) => (
                    <ErrorChip key={matched.error_id} error={matched} found />
                  ))}
                  {caseResult.missed_errors.map((missed) => (
                    <ErrorChip key={missed.error_id} error={missed} found={false} />
                  ))}
                </div>
              </td>
              <td className="px-4 py-2.5">
                {caseResult.decoy_false_alarms.length === 0 ? (
                  <span className="inline-flex items-center gap-1 text-success-600 dark:text-success-400">
                    <CheckCircle2 className="h-3.5 w-3.5" aria-hidden />
                    {caseResult.decoy_count}/{caseResult.decoy_count} bestanden
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-danger-600">
                    <XCircle className="h-3.5 w-3.5" aria-hidden />
                    {caseResult.decoy_false_alarms.length} Fehlalarm(e)
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ErrorChip({ error, found }: { error: MatchedError; found: boolean }) {
  const title = error.expected_reviewer_finding ?? error.error_id;
  return (
    <span
      title={`${title}${found ? " — gefunden" : " — übersehen"}`}
      className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[11px] ${
        found
          ? severityClasses(error.severity)
          : "border-danger-300 bg-danger-50 text-danger-700 line-through dark:border-danger-800 dark:bg-danger-900/30 dark:text-danger-300"
      }`}
    >
      {found ? (
        <CheckCircle2 className="h-3 w-3 shrink-0" aria-hidden />
      ) : (
        <XCircle className="h-3 w-3 shrink-0" aria-hidden />
      )}
      <span className="mono">{error.error_id.replace("ERR_", "Nr. ")}</span>
      <span>{severityLabels[error.severity] ?? error.severity}</span>
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const isHealthy = status === "completed" || status === "needs_human_review";
  return (
    <span
      className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[11px] ${
        isHealthy
          ? "border-[var(--border-default)] bg-[var(--surface-secondary)] text-[var(--text-secondary)]"
          : "border-danger-300 bg-danger-50 text-danger-700"
      }`}
    >
      <Activity className="h-3 w-3" aria-hidden />
      {statusLabels[status] ?? status}
    </span>
  );
}

/* ----- Token-Tabelle ----- */

function TokenTable({ tokens }: { tokens: Record<string, TokenUsage> }) {
  const entries = Object.entries(tokens).sort(
    (a, b) => b[1].total_tokens - a[1].total_tokens
  );
  return (
    <div className="overflow-x-auto rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)]">
      <table className="w-full min-w-[560px] text-left text-[13px]">
        <thead>
          <tr className="border-b border-[var(--border-default)] text-[11px] uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            <th className="px-4 py-2.5 font-medium">KI-Dienst</th>
            <th className="px-4 py-2.5 font-medium">Aufrufe</th>
            <th className="px-4 py-2.5 font-medium">Input</th>
            <th className="px-4 py-2.5 font-medium">Output</th>
            <th className="px-4 py-2.5 font-medium">Gesamt</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([provider, usage]) => (
            <tr
              key={provider}
              className="border-b border-[var(--border-default)] last:border-b-0"
            >
              <td className="px-4 py-2.5 font-medium text-[var(--text-primary)]">
                {providerLabels[provider] ?? provider}
              </td>
              <td className="px-4 py-2.5 text-[var(--text-secondary)]">{usage.calls}</td>
              <td className="px-4 py-2.5 text-[var(--text-secondary)]">
                {formatTokens(usage.input_tokens)}
              </td>
              <td className="px-4 py-2.5 text-[var(--text-secondary)]">
                {formatTokens(usage.output_tokens)}
              </td>
              <td className="px-4 py-2.5 text-[var(--text-primary)]">
                {formatTokens(usage.total_tokens)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ChipLegend() {
  return (
    <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-[var(--text-tertiary)]">
      <span className="inline-flex items-center gap-1">
        <CheckCircle2 className="h-3 w-3 text-success-600" aria-hidden />
        versteckter Fehler gefunden
      </span>
      <span className="inline-flex items-center gap-1">
        <XCircle className="h-3 w-3 text-danger-600" aria-hidden />
        versteckter Fehler übersehen
      </span>
      <span>Farbe = Schweregrad des Fehlers (rot kritisch, gelb hoch, grau mittel/niedrig)</span>
      <span>„Aussagen" = aus den Dokumenten extrahierte, zitierfähige Einzelaussagen</span>
    </div>
  );
}

/* ----- Sonstiges ----- */

function SectionHeading({ title, description }: { title: string; description: string }) {
  return (
    <div className="mb-3">
      <h3 className="text-[15px] font-medium text-[var(--text-primary)]">{title}</h3>
      <p className="mt-0.5 max-w-2xl text-[12px] leading-5 text-[var(--text-secondary)]">
        {description}
      </p>
    </div>
  );
}

function PanelMessage({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-6">
      <div className="text-[14px] font-medium text-[var(--text-primary)]">{title}</div>
      <p className="mt-1 text-[13px] leading-6 text-[var(--text-secondary)]">{body}</p>
    </div>
  );
}
