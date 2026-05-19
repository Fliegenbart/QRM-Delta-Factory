"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Loader2, RefreshCw } from "lucide-react";
import {
  displayFeedbackCount,
  displayFeedbackOutcome,
  displayReviewValue,
  type HumanFeedbackRegistryReport
} from "@/src/lib/review-ui";

type LoadState = "loading" | "ready" | "error";

export function HumanFeedbackRegistryPanel() {
  const [registry, setRegistry] = useState<HumanFeedbackRegistryReport | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadRegistry();
  }, []);

  async function loadRegistry() {
    setState("loading");
    setError(null);
    try {
      const response = await fetch("/api/review-ui/human-feedback", {
        cache: "no-store"
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.error || "Feedbackdaten konnten nicht geladen werden.");
      }
      setRegistry(payload.registry);
      setState("ready");
    } catch (caught) {
      setState("error");
      setError(caught instanceof Error ? caught.message : "Feedbackdaten konnten nicht geladen werden.");
    }
  }

  const modelCards = registry?.model_cards ?? [];
  const records = registry?.records ?? [];

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="text-sm font-semibold text-slate-950 dark:text-white">
            Modell-Performance aus menschlichen Entscheidungen
          </div>
          <p className="mt-1 text-sm leading-6 text-slate-500 dark:text-slate-400">
            Jede Bestätigung, Korrektur, Fehlalarm-Markierung und jeder fehlende Befund wird als Feedback-Datenpunkt gespeichert.
          </p>
        </div>
        <button
          type="button"
          onClick={loadRegistry}
          className="inline-flex h-9 items-center justify-center gap-2 rounded-xl border border-black/10 bg-white px-3 text-sm font-semibold text-slate-700 dark:border-white/10 dark:bg-slate-900 dark:text-slate-200"
        >
          {state === "loading" ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          Aktualisieren
        </button>
      </div>

      {state === "error" ? (
        <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-500/30 dark:bg-red-950/30 dark:text-red-100">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      ) : null}

      <div className="grid gap-3 sm:grid-cols-3">
        <Metric label="Datenpunkte" value={String(registry?.total_feedback_records ?? 0)} />
        <Metric label="Modellkarten" value={String(registry?.model_card_count ?? 0)} />
        <Metric label="Letzte Updates" value={records.length > 0 ? String(records.slice(0, 5).length) : "0"} />
      </div>

      {state === "loading" && !registry ? (
        <div className="flex items-center gap-2 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:bg-slate-900/50 dark:text-slate-300">
          <Loader2 className="h-4 w-4 animate-spin" />
          Lädt Feedbackdaten...
        </div>
      ) : null}

      <div className="grid gap-3 xl:grid-cols-2">
        {modelCards.slice(0, 4).map((card) => (
          <article key={`${card.agent_role}:${card.model_name}:${card.prompt_version}`} className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-white/10 dark:bg-slate-900/45">
            <div className="flex flex-col gap-1 md:flex-row md:items-start md:justify-between">
              <div>
                <div className="text-sm font-semibold text-slate-950 dark:text-white">
                  {card.agent_role}
                </div>
                <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  {card.model_provider} · {card.model_name} · {card.prompt_version}
                </div>
              </div>
              <Pill>{card.total_human_decisions} Entscheide</Pill>
            </div>
            <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
              <MiniMetric label="Bestätigt" value={formatRate(card.confirmation_rate)} />
              <MiniMetric label="Herabgestuft" value={formatRate(card.downgrade_rate)} />
              <MiniMetric label="Fehlalarm" value={formatRate(card.false_positive_rate)} />
            </div>
            <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
              <MiniMetric label="Quelle falsch" value={displayFeedbackCount(card.evidence_issue_count)} />
              <MiniMetric label="Regelwerk falsch" value={displayFeedbackCount(card.requirement_issue_count)} />
              <MiniMetric label="Fehlt" value={displayFeedbackCount(card.missed_finding_count)} />
            </div>
          </article>
        ))}
      </div>

      {records.length > 0 ? (
        <div className="space-y-2">
          {records.slice(0, 5).map((record) => (
            <div key={record.feedback_id} className="grid gap-2 rounded-xl border border-slate-200 bg-white/70 px-4 py-3 text-sm dark:border-white/10 dark:bg-slate-900/35 md:grid-cols-[1fr_auto_auto] md:items-center">
              <div>
                <div className="font-semibold text-slate-900 dark:text-white">
                  {record.agent_role} · {record.model_name}
                </div>
                <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  {displayReviewValue(record.risk_category)} · {displayReviewValue(record.original_severity)}
                </div>
              </div>
              <Pill>{displayFeedbackOutcome(record.feedback_outcome)}</Pill>
              <span className="text-xs text-slate-500 dark:text-slate-400">
                {new Date(record.created_at).toLocaleDateString("de-DE")}
              </span>
            </div>
          ))}
        </div>
      ) : state === "ready" ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white/60 px-4 py-5 text-center text-sm text-slate-500 dark:border-white/10 dark:bg-slate-900/35 dark:text-slate-400">
          Noch keine menschlichen Entscheidungen gespeichert.
        </div>
      ) : null}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-900/50">
      <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500 dark:text-slate-400">
        {label}
      </div>
      <div className="mt-1 text-2xl font-semibold tracking-[-0.04em] text-slate-950 dark:text-white">
        {value}
      </div>
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-slate-500 dark:text-slate-400">{label}</div>
      <div className="mt-1 font-semibold text-slate-950 dark:text-white">{value}</div>
    </div>
  );
}

function Pill({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex w-fit rounded-full border border-teal-500/20 bg-teal-500/10 px-2.5 py-1 text-xs font-semibold text-teal-700 dark:text-teal-300">
      {children}
    </span>
  );
}

function formatRate(value: number) {
  return `${Math.round(value * 100)}%`;
}
