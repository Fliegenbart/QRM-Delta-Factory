"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, FlaskConical, Loader2, RefreshCw } from "lucide-react";
import {
  displayCalibrationStatus,
  displayFeedbackOutcome,
  displayReviewValue,
  type CalibrationExample,
  type CalibrationRegressionGateReport,
  type ReviewCalibrationReport
} from "@/src/lib/review-ui";

type LoadState = "loading" | "ready" | "error";

export function ReviewCalibrationPanel() {
  const [report, setReport] = useState<ReviewCalibrationReport | null>(null);
  const [gate, setGate] = useState<CalibrationRegressionGateReport | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [reviewerId, setReviewerId] = useState("qa_lead");
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    void loadCalibration();
  }, []);

  async function loadCalibration() {
    setState("loading");
    setError(null);
    try {
      const response = await fetch("/api/review-ui/review-calibration", {
        cache: "no-store"
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.error || "Kalibrierung konnte nicht geladen werden.");
      }
      setReport(payload.calibration);
      setState("ready");
    } catch (caught) {
      setState("error");
      setError(caught instanceof Error ? caught.message : "Kalibrierung konnte nicht geladen werden.");
    }
  }

  async function runGate() {
    setBusyAction("gate");
    setNotice(null);
    setError(null);
    try {
      const response = await fetch("/api/review-ui/review-calibration/run-regression-gate", {
        method: "POST"
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.error || "Regressionstest konnte nicht gestartet werden.");
      }
      setGate(payload.gate);
      setNotice(
        payload.gate.passed
          ? "Regressionstest bestanden."
          : "Regressionstest nicht bestanden."
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Regressionstest konnte nicht gestartet werden.");
    } finally {
      setBusyAction(null);
    }
  }

  async function approve(example: CalibrationExample, activate: boolean) {
    const actionId = `${example.calibration_example_id}:${activate ? "activate" : "approve"}`;
    setBusyAction(actionId);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(
        `/api/review-ui/review-calibration/${encodeURIComponent(example.calibration_example_id)}/approve`,
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            approvedBy: reviewerId,
            activate,
            regressionGatePassed: Boolean(gate?.passed),
            regressionGateReportId: gate?.regression_gate_report_id ?? null
          })
        }
      );
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.error || "Kalibrierung konnte nicht gespeichert werden.");
      }
      setNotice(activate ? "Beispiel aktiviert." : "Gold-Beispiel freigegeben.");
      await loadCalibration();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Kalibrierung konnte nicht gespeichert werden.");
    } finally {
      setBusyAction(null);
    }
  }

  const examples = report?.examples ?? [];
  const latestExamples = useMemo(() => examples.slice(0, 6), [examples]);

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="text-sm font-semibold text-slate-950 dark:text-white">
            KI-Kalibrierung aus geprüften Fällen
          </div>
          <p className="mt-1 text-sm leading-6 text-slate-500 dark:text-slate-400">
            Rohfeedback wird gesammelt. Nur freigegebene Beispiele mit bestandenem Regressionstest werden aktiv.
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label className="text-xs font-semibold text-slate-500 dark:text-slate-400">
            Reviewer
            <input
              value={reviewerId}
              onChange={(event) => setReviewerId(event.target.value)}
              className="mt-1 h-9 w-full rounded-lg border border-black/10 bg-white px-3 text-sm text-slate-900 outline-none focus:border-teal dark:border-white/10 dark:bg-slate-900 dark:text-white sm:w-40"
            />
          </label>
          <button
            type="button"
            onClick={runGate}
            disabled={busyAction !== null}
            className="inline-flex h-9 items-center justify-center gap-2 rounded-lg border border-black/10 bg-white px-3 text-sm font-semibold text-slate-700 disabled:opacity-50 dark:border-white/10 dark:bg-slate-900 dark:text-slate-200"
          >
            {busyAction === "gate" ? <Loader2 className="h-4 w-4 animate-spin" /> : <FlaskConical className="h-4 w-4" />}
            Regressionstest
          </button>
          <button
            type="button"
            onClick={loadCalibration}
            disabled={busyAction !== null}
            className="inline-flex h-9 items-center justify-center gap-2 rounded-lg border border-black/10 bg-white px-3 text-sm font-semibold text-slate-700 disabled:opacity-50 dark:border-white/10 dark:bg-slate-900 dark:text-slate-200"
          >
            {state === "loading" ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            Aktualisieren
          </button>
        </div>
      </div>

      {error ? <Notice tone="red">{error}</Notice> : null}
      {notice ? <Notice tone={notice.includes("nicht") ? "red" : "green"}>{notice}</Notice> : null}

      <div className="grid gap-3 sm:grid-cols-4">
        <Metric label="Rohfeedback" value={String(report?.raw_feedback_count ?? 0)} />
        <Metric label="Gold" value={String(report?.approved_gold_count ?? 0)} />
        <Metric label="Aktiv" value={String(report?.active_count ?? 0)} />
        <Metric label="Gate" value={gate ? (gate.passed ? "Bestanden" : "Blockiert") : "Offen"} />
      </div>

      {gate ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 dark:border-white/10 dark:bg-slate-900/40 dark:text-slate-300">
          <span className="font-semibold text-slate-950 dark:text-white">
            {gate.regression_gate_report_id}
          </span>{" "}
          · {gate.eval_dataset_count} Benchmarks · {gate.failed_dataset_ids.length} Fehler
        </div>
      ) : null}

      {state === "loading" && !report ? (
        <div className="flex items-center gap-2 rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:bg-slate-900/50 dark:text-slate-300">
          <Loader2 className="h-4 w-4 animate-spin" />
          Lädt Kalibrierung...
        </div>
      ) : null}

      {latestExamples.length > 0 ? (
        <div className="space-y-2">
          {latestExamples.map((example) => (
            <CalibrationRow
              key={example.calibration_example_id}
              example={example}
              gate={gate}
              busyAction={busyAction}
              onApprove={() => approve(example, false)}
              onActivate={() => approve(example, true)}
            />
          ))}
        </div>
      ) : state === "ready" ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white/60 px-4 py-5 text-center text-sm text-slate-500 dark:border-white/10 dark:bg-slate-900/35 dark:text-slate-400">
          Noch keine Kalibrierungsbeispiele vorhanden.
        </div>
      ) : null}
    </div>
  );
}

function CalibrationRow({
  example,
  gate,
  busyAction,
  onApprove,
  onActivate
}: {
  example: CalibrationExample;
  gate: CalibrationRegressionGateReport | null;
  busyAction: string | null;
  onApprove: () => void;
  onActivate: () => void;
}) {
  const approveId = `${example.calibration_example_id}:approve`;
  const activateId = `${example.calibration_example_id}:activate`;
  const canActivate = example.status === "approved_gold" && Boolean(gate?.passed);

  return (
    <article className="grid gap-3 rounded-lg border border-slate-200 bg-white/70 px-4 py-3 text-sm dark:border-white/10 dark:bg-slate-900/35 xl:grid-cols-[1fr_auto] xl:items-center">
      <div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-semibold text-slate-950 dark:text-white">
            {example.agent_role}
          </span>
          <Pill>{displayCalibrationStatus(example.status)}</Pill>
          <Pill>{displayFeedbackOutcome(example.feedback_outcome)}</Pill>
        </div>
        <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          {displayReviewValue(example.risk_category)} · {displayReviewValue(example.original_severity)} · {example.calibration_example_id}
        </div>
        <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-700 dark:text-slate-300">
          {example.reviewer_rationale}
        </p>
      </div>
      <div className="flex flex-wrap gap-2 xl:justify-end">
        {example.status === "raw_feedback" ? (
          <ActionButton busy={busyAction === approveId} disabled={busyAction !== null} onClick={onApprove}>
            Gold freigeben
          </ActionButton>
        ) : null}
        {example.status === "approved_gold" ? (
          <ActionButton
            busy={busyAction === activateId}
            disabled={!canActivate || busyAction !== null}
            onClick={onActivate}
          >
            Aktivieren
          </ActionButton>
        ) : null}
        {example.status === "active" ? (
          <span className="inline-flex h-9 items-center gap-2 rounded-lg bg-teal-500/10 px-3 text-sm font-semibold text-teal-700 dark:text-teal-300">
            <CheckCircle2 className="h-4 w-4" />
            Aktiv
          </span>
        ) : null}
      </div>
    </article>
  );
}

function ActionButton({
  children,
  busy,
  disabled,
  onClick
}: {
  children: React.ReactNode;
  busy: boolean;
  disabled: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="inline-flex h-9 items-center justify-center gap-2 rounded-lg bg-slate-950 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-slate-950"
    >
      {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
      {children}
    </button>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-50 px-4 py-3 dark:bg-slate-900/50">
      <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500 dark:text-slate-400">
        {label}
      </div>
      <div className="mt-1 text-2xl font-semibold text-slate-950 dark:text-white">
        {value}
      </div>
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

function Notice({ children, tone }: { children: React.ReactNode; tone: "red" | "green" }) {
  const className = tone === "red"
    ? "border-red-200 bg-red-50 text-red-800 dark:border-red-500/30 dark:bg-red-950/30 dark:text-red-100"
    : "border-teal-200 bg-teal-50 text-teal-800 dark:border-teal-500/30 dark:bg-teal-950/30 dark:text-teal-100";

  return (
    <div className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-sm ${className}`}>
      {tone === "red" ? <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" /> : <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />}
      <span>{children}</span>
    </div>
  );
}
