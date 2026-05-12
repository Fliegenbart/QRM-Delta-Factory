import Link from "next/link";
import type { ReactNode } from "react";
import { consultantReviewCopy } from "@/src/lib/review-ui";

export function ReviewShell({ children }: { children: ReactNode }) {
  return (
    <main className="min-h-screen bg-[#f7f8f6] px-5 py-6 text-slate-950 md:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 flex flex-col gap-4 border-b border-slate-200 pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <Link href="/" className="text-xs font-semibold uppercase tracking-[0.22em] text-teal-700">
              {consultantReviewCopy.productName}
            </Link>
            <h1 className="mt-2 text-3xl font-semibold tracking-[-0.04em] md:text-4xl">
              {consultantReviewCopy.workspaceTitle}
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
              {consultantReviewCopy.workspaceDescription}
            </p>
          </div>
          <nav className="flex flex-wrap gap-2 text-sm">
            <Link className="rounded-xl border border-slate-200 bg-white px-4 py-2" href="/case-workspace">
              {consultantReviewCopy.nav.cockpit}
            </Link>
            <Link className="rounded-xl border border-slate-200 bg-white px-4 py-2" href="/review-ui">
              {consultantReviewCopy.nav.packages}
            </Link>
          </nav>
        </header>
        {children}
      </div>
    </main>
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
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 md:flex-row md:items-center md:justify-between">
        <h2 className="text-base font-semibold tracking-[-0.02em]">{title}</h2>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}

export function StatusBadge({ children, tone = "slate" }: { children: ReactNode; tone?: "slate" | "green" | "amber" | "red" }) {
  const toneClass = {
    slate: "border-slate-200 bg-slate-50 text-slate-700",
    green: "border-emerald-200 bg-emerald-50 text-emerald-800",
    amber: "border-amber-200 bg-amber-50 text-amber-800",
    red: "border-red-200 bg-red-50 text-red-800"
  }[tone];

  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${toneClass}`}>
      {children}
    </span>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-white/70 p-8 text-center text-sm text-slate-600">
      {message}
    </div>
  );
}
