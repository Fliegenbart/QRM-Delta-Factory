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
};

const severityBadgeClass: Record<Severity, string> = {
  critical: "text-[var(--severity-critical)]",
  major: "text-[var(--severity-major)]",
  minor: "text-[var(--severity-minor)]",
  ready: "text-[var(--severity-ready)]",
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
  } = data;

  return (
    <article className="border-t border-[var(--border-default)] py-4 first:border-t-0 md:grid md:grid-cols-[150px_minmax(0,1fr)_104px] md:gap-5">
      <div className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1 md:mb-0 md:block">
        <div className="mono text-[12px] text-[var(--text-tertiary)]">{id}</div>
        <div className={`text-[12px] font-medium md:mt-2 ${severityBadgeClass[severity]}`}>
          {severityLabel}
        </div>
      </div>

      <div className="min-w-0">
        <div className="text-[12px] text-[var(--text-tertiary)]">{area}</div>
        <h3 className="mt-1 text-[16px] font-medium leading-snug text-[var(--text-primary)]">
          {title}
        </h3>
        <p className="mt-2 max-w-4xl text-[13px] leading-[1.6] text-[var(--text-secondary)]">
          <span className="text-[var(--text-tertiary)]">{noteLabel}:</span> {criticNote}
        </p>

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
        className="mt-3 inline-flex items-center gap-1 text-[13px] font-medium text-[var(--brand)] hover:text-[var(--brand-strong)] md:mt-0 md:justify-self-end"
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
