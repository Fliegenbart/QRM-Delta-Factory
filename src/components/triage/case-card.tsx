import Link from "next/link";
import { ArrowRight, Check, Clock } from "lucide-react";

export type Severity = "critical" | "major" | "minor" | "ready";

export type TriageCase = {
  id: string;
  severity: Severity;
  severityLabel: string;
  area: string;
  title: string;
  noteLabel: string;
  criticNote: string;
  ageLabel: string;
  sources: string;
  regulation: string;
  primaryAction: "open" | "approve";
  href: string;
  nextStep?: string;
};

const severityClass: Record<Severity, { text: string; bg: string; rail: string }> = {
  critical: {
    text: "text-[var(--severity-critical)]",
    bg: "bg-[var(--severity-critical-soft)]",
    rail: "bg-[var(--severity-critical)]",
  },
  major: {
    text: "text-[var(--severity-major)]",
    bg: "bg-[var(--severity-major-soft)]",
    rail: "bg-[var(--severity-major)]",
  },
  minor: {
    text: "text-[var(--severity-minor)]",
    bg: "bg-[var(--severity-minor-soft)]",
    rail: "bg-[var(--severity-minor)]",
  },
  ready: {
    text: "text-[var(--severity-ready)]",
    bg: "bg-[var(--severity-ready-soft)]",
    rail: "bg-[var(--severity-ready)]",
  },
};

export function CaseCard({ data }: { data: TriageCase }) {
  const {
    id,
    severity,
    severityLabel,
    area,
    title,
    noteLabel,
    criticNote,
    ageLabel,
    sources,
    regulation,
    primaryAction,
    href,
    nextStep,
  } = data;
  const tone = severityClass[severity];

  return (
    <article className="group relative border-t border-[var(--border-default)] py-4 first:border-t-0 md:grid md:grid-cols-[156px_minmax(0,1fr)_112px] md:gap-5">
      <div className={`absolute left-[-16px] top-4 hidden h-[calc(100%-2rem)] w-1 rounded-full ${tone.rail} md:block`} aria-hidden />

      <div className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1 md:mb-0 md:block">
        <div className="mono text-[12px] text-[var(--text-tertiary)]">{id}</div>
        <div className={`mt-0 inline-flex rounded-full border border-transparent px-2 py-0.5 text-[11px] font-medium md:mt-2 ${tone.bg} ${tone.text}`}>
          {severityLabel}
        </div>
      </div>

      <div className="min-w-0">
        <div className="text-[12px] font-medium text-[var(--text-tertiary)]">{area}</div>
        <h3 className="mt-1 text-[16px] font-medium leading-snug text-[var(--text-primary)]">
          {title}
        </h3>
        <p className="mt-2 max-w-4xl text-[13px] leading-[1.6] text-[var(--text-secondary)]">
          <span className="text-[var(--text-tertiary)]">{noteLabel}:</span> {criticNote}
        </p>

        {nextStep ? (
          <div className="mt-3 rounded-md border border-[var(--border-muted)] bg-[var(--surface-secondary)] px-3 py-2 text-[12px] leading-5 text-[var(--text-secondary)]">
            <span className="font-medium text-[var(--text-primary)]">Nächster Schritt:</span>{" "}
            {nextStep}
          </div>
        ) : null}

        <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-[11px] text-[var(--text-tertiary)]">
          <span className="inline-flex items-center gap-1">
            <Clock className="h-3 w-3" aria-hidden /> {ageLabel}
          </span>
          <span>{sources}</span>
          <span className="mono">{regulation}</span>
        </div>
      </div>

      <Link
        href={href}
        className="mt-3 inline-flex h-9 items-center justify-center gap-1 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-[13px] font-medium text-[var(--brand)] hover:border-[var(--brand)] hover:bg-[var(--brand-soft)] hover:text-[var(--brand-strong)] md:mt-0 md:justify-self-end"
      >
        {primaryAction === "approve" ? "Freigeben" : "Öffnen"}
        {primaryAction === "approve" ? (
          <Check className="h-3.5 w-3.5" aria-hidden />
        ) : (
          <ArrowRight className="h-3.5 w-3.5" aria-hidden />
        )}
      </Link>
    </article>
  );
}
