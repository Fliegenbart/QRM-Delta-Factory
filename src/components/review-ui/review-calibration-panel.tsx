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
          <div className="text-sm font-semibold text-[var(--text-primary)]">
            Qualität der Prüfhinweise aus geprüften Fällen
          </div>
          <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
            Menschliche Entscheidungen verbessern die künftigen Prüfhinweise. Nur freigegebene Beispiele mit bestandenem Test werden aktiv.
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label className="text-xs font-semibold text-[var(--text-tertiary)]">
            Reviewer
            <input
              value={reviewerId}
              onChange={(event) => setReviewerId(event.target.value)}
              className="mt-1 h-9 w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-sm text-[var(--text-primary)] outline-none focus:ring-4 focus:ring-[var(--brand-ring)] sm:w-40"
            />
          </label>
          <button
            type="button"
            onClick={runGate}
            disabled={busyAction !== null}
            className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-sm font-semibold text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] disabled:opacity-50"
          >
            {busyAction === "gate" ? <Loader2 className="h-4 w-4 animate-spin" /> : <FlaskConical className="h-4 w-4" />}
            Regressionstest
          </button>
          <button
            type="button"
            onClick={loadCalibration}
            disabled={busyAction !== null}
            className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-sm font-semibold text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] disabled:opacity-50"
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
        <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3 text-sm text-[var(--text-secondary)]">
          <span className="font-semibold text-[var(--text-primary)]">
            {gate.regression_gate_report_id}
          </span>{" "}
          · {gate.eval_dataset_count} Benchmarks · {gate.failed_dataset_ids.length} Fehler
        </div>
      ) : null}

      {state === "loading" && !report ? (
        <div className="flex items-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3 text-sm text-[var(--text-secondary)]">
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
        <div className="rounded-md border border-dashed border-[var(--border-strong)] bg-[var(--surface-secondary)] px-4 py-5 text-center text-sm text-[var(--text-tertiary)]">
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
    <article className="grid gap-3 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-4 py-3 text-sm xl:grid-cols-[1fr_auto] xl:items-center">
      <div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-semibold text-[var(--text-primary)]">
            {example.agent_role}
          </span>
          <Pill>{displayCalibrationStatus(example.status)}</Pill>
          <Pill>{displayFeedbackOutcome(example.feedback_outcome)}</Pill>
        </div>
        <div className="mt-1 text-xs text-[var(--text-tertiary)]">
          {displayReviewValue(example.risk_category)} · {displayReviewValue(example.original_severity)} · {example.calibration_example_id}
        </div>
        <p className="mt-2 line-clamp-2 text-sm leading-6 text-[var(--text-secondary)]">
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
          <span className="inline-flex h-9 items-center gap-2 rounded-md bg-[var(--brand-soft)] px-3 text-sm font-semibold text-[var(--brand)]">
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
      className="inline-flex h-9 items-center justify-center gap-2 rounded-md bg-[var(--brand)] px-3 text-sm font-semibold text-white hover:bg-[var(--brand-strong)] disabled:cursor-not-allowed disabled:opacity-50"
    >
      {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
      {children}
    </button>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3">
      <div className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
        {label}
      </div>
      <div className="mt-1 text-2xl font-semibold text-[var(--text-primary)]">
        {value}
      </div>
    </div>
  );
}

function Pill({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex w-fit rounded-full border border-[var(--border-default)] bg-[var(--surface-secondary)] px-2.5 py-1 text-xs font-semibold text-[var(--text-secondary)]">
      {children}
    </span>
  );
}

function Notice({ children, tone }: { children: React.ReactNode; tone: "red" | "green" }) {
  const className = tone === "red"
    ? "border-red-200 bg-red-50 text-red-800 dark:border-red-500/30 dark:bg-red-950/30 dark:text-red-100"
    : "border-[var(--brand)] bg-[var(--brand-soft)] text-[var(--text-primary)]";

  return (
    <div className={`flex items-start gap-2 rounded-md border px-3 py-2 text-sm ${className}`}>
      {tone === "red" ? <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" /> : <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />}
      <span>{children}</span>
    </div>
  );
}
