"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, RotateCcw } from "lucide-react";
import type { RequirementReportRetry } from "@/src/lib/review-ui";

type State =
  | { status: "idle" }
  | { status: "starting" }
  | { status: "running"; detail: string | null }
  | { status: "error"; message: string };

/**
 * Re-judge only the rows a failed model call left behind. The report's
 * other rows stay; when the retry finishes the page reloads its data.
 */
export function RetryFailedRequirements({
  documentSetId,
  retryable
}: {
  documentSetId: string;
  retryable: number;
}) {
  const router = useRouter();
  const [state, setState] = useState<State>({ status: "idle" });
  const endpoint = `/api/review-ui/document-sets/${encodeURIComponent(documentSetId)}/requirement-report/retry`;

  useEffect(() => {
    if (state.status !== "running") return;
    let cancelled = false;
    const timer = window.setInterval(async () => {
      try {
        const response = await fetch(endpoint, { cache: "no-store" });
        const payload = (await response.json()) as { retry?: RequirementReportRetry; error?: string };
        if (!response.ok || !payload.retry) throw new Error(payload.error ?? "Status nicht abrufbar.");
        if (cancelled) return;
        if (payload.retry.active) {
          setState({ status: "running", detail: payload.retry.detail ?? null });
        } else {
          setState({ status: "idle" });
          router.refresh();
        }
      } catch (error) {
        if (!cancelled) {
          setState({ status: "error", message: error instanceof Error ? error.message : "Status nicht abrufbar." });
        }
      }
    }, 4000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [endpoint, router, state.status]);

  async function start() {
    setState({ status: "starting" });
    try {
      const response = await fetch(endpoint, { method: "POST" });
      const payload = (await response.json()) as { retry?: RequirementReportRetry; error?: string };
      if (!response.ok || !payload.retry) throw new Error(payload.error ?? "Erneute Prüfung konnte nicht gestartet werden.");
      if (payload.retry.active) {
        setState({ status: "running", detail: payload.retry.detail ?? null });
      } else {
        setState({ status: "idle" });
        router.refresh();
      }
    } catch (error) {
      setState({
        status: "error",
        message: error instanceof Error ? error.message : "Erneute Prüfung konnte nicht gestartet werden."
      });
    }
  }

  const busy = state.status === "starting" || state.status === "running";

  return (
    <div className="mt-4 rounded-md border border-amber-400/45 bg-amber-50 px-4 py-3 text-sm leading-6 text-[var(--text-primary)]">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <span className="font-semibold">
            {retryable === 1
              ? "Eine Anforderung konnte nicht beurteilt werden,"
              : `${retryable} Anforderungen konnten nicht beurteilt werden,`}
          </span>{" "}
          weil ein Modellaufruf fehlschlug. Die übrigen Zeilen sind davon nicht berührt; nur
          diese werden erneut geprüft.
        </div>
        <button
          type="button"
          onClick={start}
          disabled={busy}
          className="inline-flex h-9 items-center gap-2 rounded-md bg-[var(--brand)] px-3 text-sm font-semibold text-white hover:bg-[var(--brand-strong)] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {busy ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : <RotateCcw className="h-4 w-4" aria-hidden />}
          {busy ? "Wird erneut geprüft…" : "Erneut prüfen"}
        </button>
      </div>
      {state.status === "running" && state.detail ? (
        <p className="mt-2 text-xs text-[var(--text-secondary)]" aria-live="polite">
          {state.detail}
        </p>
      ) : null}
      {state.status === "error" ? (
        <p className="mt-2 text-xs text-red-700" role="alert">
          {state.message}
        </p>
      ) : null}
    </div>
  );
}
