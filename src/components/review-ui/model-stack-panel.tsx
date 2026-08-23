"use client";

import { useEffect, useState } from "react";
import { Cpu } from "lucide-react";
import { describeModelStack, type BackendHealth } from "@/src/lib/review-ui";

type LoadState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; health: BackendHealth };

/**
 * Which models are working on the customer's documents right now, read from
 * the backend's /health. The page text describes the chain; this panel says
 * who is standing at each link today -- the one fact a QA lead asks first
 * when "lokal" is on the table.
 */
export function ModelStackPanel() {
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    fetch("/api/review-ui/health", { cache: "no-store" })
      .then(async (response) => {
        const payload = (await response.json()) as { health?: BackendHealth; error?: string };
        if (!response.ok || !payload.health) {
          throw new Error(payload.error ?? "Backend-Status konnte nicht geladen werden.");
        }
        if (!cancelled) setState({ status: "ready", health: payload.health });
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setState({
            status: "error",
            message: error instanceof Error ? error.message : "Backend-Status konnte nicht geladen werden."
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="surface overflow-hidden rise-in">
      <div className="flex items-center justify-between border-b border-[var(--border-default)] px-5 py-3">
        <h2 className="ui-title flex items-center gap-2 text-[14px] font-medium text-[var(--text-primary)]">
          <Cpu className="h-4 w-4 text-[var(--brand)]" aria-hidden />
          Welche Modelle gerade prüfen
        </h2>
        {state.status === "ready" && state.health.model_roles ? (
          <span className="rounded-full border border-[var(--border-default)] bg-[var(--surface-secondary)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--text-secondary)]">
            {describeModelStack(state.health.model_roles).label}
          </span>
        ) : null}
      </div>
      <div className="p-5">
        {state.status === "loading" ? (
          <p className="text-[12px] text-[var(--text-tertiary)]">Backend-Status wird geladen…</p>
        ) : state.status === "error" ? (
          <p className="text-[12px] text-[var(--text-secondary)]">{state.message}</p>
        ) : !state.health.model_roles ? (
          <p className="text-[12px] text-[var(--text-secondary)]">
            Dieses Backend meldet seine Modellrollen noch nicht (Version {state.health.app_version}).
          </p>
        ) : (
          <ModelStackRows health={state.health} />
        )}
      </div>
    </section>
  );
}

function ModelStackRows({ health }: { health: BackendHealth }) {
  const described = describeModelStack(health.model_roles!);
  return (
    <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
      <p className="max-w-md text-[13px] leading-relaxed text-[var(--text-secondary)]">{described.summary}</p>
      <dl className="divide-y divide-[var(--border-muted)] rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)]">
        {described.rows.map((row) => (
          <div key={row.label} className="grid gap-1 px-3 py-2 text-[12px] md:grid-cols-[200px_1fr]">
            <dt className="text-[var(--text-tertiary)]">{row.label}</dt>
            <dd className="text-[var(--text-primary)]">{row.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
