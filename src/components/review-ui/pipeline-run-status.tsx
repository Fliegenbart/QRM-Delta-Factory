"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, Clock3, Loader2 } from "lucide-react";
import { pipelineStepLabel, type PipelineRun } from "@/src/lib/review-ui";

const TYPICAL_DURATION_SECONDS = 5 * 60;
const LONGER_THAN_USUAL_SECONDS = 6 * 60;

export function PipelineRunStatus({
  documentSetId,
  initialPipelineRun
}: {
  documentSetId: string;
  initialPipelineRun: PipelineRun;
}) {
  const [pipelineRun, setPipelineRun] = useState(initialPipelineRun);
  const [now, setNow] = useState(() => Date.now());
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const isRunning = pipelineRun.status === "running";

  useEffect(() => {
    setPipelineRun(initialPipelineRun);
    setRefreshError(null);
  }, [initialPipelineRun]);

  useEffect(() => {
    if (!isRunning) return;

    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [isRunning]);

  useEffect(() => {
    if (!isRunning) return;

    let cancelled = false;
    async function refreshStatus() {
      try {
        const response = await fetch(
          `/api/review-ui/document-sets/${encodeURIComponent(documentSetId)}/pipeline-runs`,
          { cache: "no-store" }
        );
        const payload = await response.json().catch(() => ({}));
        if (!response.ok || !payload.pipelineRun) {
          throw new Error(
            typeof payload.error === "string"
              ? payload.error
              : "Analyse-Status konnte nicht aktualisiert werden."
          );
        }
        if (!cancelled) {
          setPipelineRun(payload.pipelineRun as PipelineRun);
          setRefreshError(null);
        }
      } catch (error) {
        if (!cancelled) {
          setRefreshError(
            error instanceof Error
              ? error.message
              : "Analyse-Status konnte nicht aktualisiert werden."
          );
        }
      }
    }

    void refreshStatus();
    const timer = window.setInterval(() => void refreshStatus(), 5000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [documentSetId, isRunning, pipelineRun.pipeline_run_id]);

  const timing = useMemo(
    () => describePipelineTiming(pipelineRun.started_at, now),
    [now, pipelineRun.started_at]
  );
  const copy = statusCopy(pipelineRun);

  return (
    <section
      className={`rounded-md border px-4 py-3 ${copy.tone === "warning"
        ? "border-amber-400/45 bg-amber-50"
        : copy.tone === "error"
          ? "border-red-300 bg-red-50"
          : "border-[var(--brand)] bg-[var(--brand-soft)]"
        }`}
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5 text-[var(--brand)]">
          {isRunning ? <Loader2 className="h-5 w-5 animate-spin" /> : copy.tone === "error" ? <AlertCircle className="h-5 w-5 text-red-600" /> : <CheckCircle2 className="h-5 w-5" />}
        </div>
        <div className="min-w-0 flex-1">
          <div className="font-semibold text-[var(--text-primary)]">{copy.title}</div>
          <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{copy.description}</p>

          {isRunning && pipelineRun.progress ? (
            <StepProgress
              progress={pipelineRun.progress}
              elapsedSeconds={timing?.elapsedSeconds ?? 0}
            />
          ) : isRunning && timing ? (
            <div className="mt-3">
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[var(--text-secondary)]">
                <span className="inline-flex items-center gap-1.5">
                  <Clock3 className="h-3.5 w-3.5" aria-hidden />
                  Läuft seit {formatDuration(timing.elapsedSeconds)}
                </span>
                <span>{timing.waitingCopy}</span>
              </div>
              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/70" aria-label="Zeitlicher Richtwert für die Analyse">
                <div
                  className="h-full rounded-full bg-[var(--brand)] transition-[width] duration-1000"
                  style={{ width: `${timing.progressPercent}%` }}
                />
              </div>
              <p className="mt-2 text-xs leading-5 text-[var(--text-secondary)]">
                Richtwert: Für vergleichbare Prüffälle dauert die Analyse meist 4–6 Minuten.
              </p>
            </div>
          ) : null}

          {isRunning && refreshError ? (
            <p className="mt-2 text-xs leading-5 text-amber-800">
              Status wird erneut abgefragt. Die Analyse läuft auf dem Server weiter.
            </p>
          ) : null}

          {!isRunning && (pipelineRun.status === "completed" || pipelineRun.status === "needs_human_review") ? (
            <Link
              className="mt-3 inline-flex rounded-md bg-[var(--brand)] px-3 py-2 text-sm font-semibold text-white hover:bg-[var(--brand-strong)]"
              href={`/review-ui/document-sets/${documentSetId}/review-pack`}
            >
              Prüfmappe öffnen
            </Link>
          ) : null}
        </div>
      </div>
    </section>
  );
}

/**
 * Real progress from the server: which of the steps the run is on and, inside
 * the long one, how many requirements are judged. No time estimate -- on a
 * local model a run takes 20-30 minutes and a guess would be wrong for most
 * of them; the step count is something the reviewer can trust.
 */
function StepProgress({
  progress,
  elapsedSeconds
}: {
  progress: NonNullable<PipelineRun["progress"]>;
  elapsedSeconds: number;
}) {
  const percent = describeStepProgress(progress).percent;
  return (
    <div className="mt-3">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[var(--text-secondary)]">
        <span className="inline-flex items-center gap-1.5">
          <Clock3 className="h-3.5 w-3.5" aria-hidden />
          Läuft seit {formatDuration(elapsedSeconds)}
        </span>
        <span>
          Schritt {progress.step_index} von {progress.step_count}:{" "}
          <span className="font-medium text-[var(--text-primary)]">{pipelineStepLabel(progress.step)}</span>
        </span>
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/70" aria-label="Fortschritt der Analyse nach Schritten">
        <div
          className="h-full rounded-full bg-[var(--brand)] transition-[width] duration-1000"
          style={{ width: `${percent}%` }}
        />
      </div>
      {progress.detail ? (
        <p className="mt-2 text-xs leading-5 text-[var(--text-secondary)]" aria-live="polite">
          {progress.detail}
        </p>
      ) : null}
    </div>
  );
}

/**
 * Steps are not equal in length -- the requirement review is most of a run --
 * so the bar reads the detail's "n von m" when there is one and spreads the
 * remaining steps evenly otherwise. Never 100 % while the run is running.
 */
export function describeStepProgress(progress: {
  step_index: number;
  step_count: number;
  detail?: string | null;
}): { percent: number } {
  const perStep = 100 / progress.step_count;
  let percent = (progress.step_index - 1) * perStep;
  const fraction = progress.detail?.match(/(\d+) von (\d+)/);
  if (fraction) {
    const done = Number(fraction[1]);
    const total = Number(fraction[2]);
    if (total > 0) percent += perStep * Math.min(done / total, 1);
  }
  return { percent: Math.min(97, Math.max(3, Math.round(percent))) };
}

export function describePipelineTiming(startedAt: string, now: number) {
  const startedAtMs = Date.parse(startedAt);
  if (Number.isNaN(startedAtMs)) return null;

  const elapsedSeconds = Math.max(0, Math.floor((now - startedAtMs) / 1000));
  const remainingSeconds = Math.max(0, TYPICAL_DURATION_SECONDS - elapsedSeconds);
  return {
    elapsedSeconds,
    progressPercent: Math.min(94, Math.max(8, 8 + (elapsedSeconds / TYPICAL_DURATION_SECONDS) * 80)),
    waitingCopy:
      elapsedSeconds >= LONGER_THAN_USUAL_SECONDS
        ? "Dauert länger als üblich – wird weiter verarbeitet."
        : `Voraussichtlich noch ca. ${formatDuration(remainingSeconds)}.`
  };
}

function statusCopy(pipelineRun: PipelineRun) {
  if (pipelineRun.status === "failed") {
    return {
      title: "Analyse konnte nicht abgeschlossen werden.",
      description: pipelineRun.failed_step
        ? `Die Verarbeitung ist bei „${pipelineRun.failed_step}“ stehen geblieben.`
        : "Der Prüffall bleibt erhalten. Die Prüfmappe wurde noch nicht ergänzt.",
      tone: "error" as const
    };
  }
  if (pipelineRun.status === "needs_human_review") {
    return {
      title: "Analyse abgeschlossen – fachliche Prüfung erforderlich.",
      description: "Die Prüfmappe ist vorbereitet und kann jetzt in QA geprüft werden.",
      tone: "warning" as const
    };
  }
  if (pipelineRun.status === "completed") {
    return {
      title: "Analyse abgeschlossen.",
      description: "Die Prüfmappe ist jetzt bereit.",
      tone: "success" as const
    };
  }
  return {
    title: "Analyse läuft.",
    description: "Die Prüfmappe wird nach Abschluss automatisch ergänzt.",
    tone: "success" as const
  };
}

function formatDuration(seconds: number) {
  if (seconds < 60) return "unter 1 Minute";
  return `${Math.ceil(seconds / 60)} ${Math.ceil(seconds / 60) === 1 ? "Minute" : "Minuten"}`;
}
