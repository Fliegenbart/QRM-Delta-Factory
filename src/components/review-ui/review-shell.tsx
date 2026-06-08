import type { ReactNode } from "react";
import { AppFrame } from "@/src/components/app-shell";

export function ReviewShell({ children }: { children: ReactNode }) {
  return (
    <AppFrame section="review-ui">
      <div className="space-y-5">
        {children}
      </div>
    </AppFrame>
  );
}

export function ReviewPanel({
  title,
  children,
  action
}: {
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <section className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] text-[var(--text-primary)]">
      <div className="flex flex-col gap-3 border-b border-[var(--border-default)] px-5 py-3 md:flex-row md:items-center md:justify-between">
        <h2 className="text-[14px] font-medium text-[var(--text-primary)]">{title}</h2>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}

export function StatusBadge({ children, tone = "slate" }: { children: ReactNode; tone?: "slate" | "green" | "amber" | "red" }) {
  const toneClass = {
    slate: "border-[var(--border-default)] bg-[var(--surface-secondary)] text-[var(--text-secondary)]",
    green: "border-transparent bg-[var(--severity-ready-soft)] text-[var(--severity-ready)]",
    amber: "border-transparent bg-[var(--severity-major-soft)] text-[var(--severity-major)]",
    red: "border-transparent bg-[var(--severity-critical-soft)] text-[var(--severity-critical)]"
  }[tone];

  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${toneClass}`}>
      {children}
    </span>
  );
}

export function EmptyState({
  message,
  title,
  action
}: {
  message: string;
  title?: string;
  action?: ReactNode;
}) {
  return (
    <div className="rounded-md border border-dashed border-[var(--border-strong)] bg-[var(--surface-secondary)] p-8 text-center text-sm text-[var(--text-secondary)]">
      {title ? (
        <h3 className="text-base font-semibold text-[var(--text-primary)]">{title}</h3>
      ) : null}
      <p className={title ? "mx-auto mt-2 max-w-2xl leading-6" : "leading-6"}>{message}</p>
      {action ? <div className="mt-5 flex flex-wrap justify-center gap-2">{action}</div> : null}
    </div>
  );
}
