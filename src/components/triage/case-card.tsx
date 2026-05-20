import Link from "next/link";
import { ArrowRight, Check, Clock } from "lucide-react";

export type Severity = "critical" | "major" | "minor" | "ready";

export type TriageCase = {
  id: string;
  severity: Severity;
  severityLabel: string;
  area: string;
  title: string;
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

const severityBadgeBg: Record<Severity, string> = {
  critical: "bg-[var(--severity-critical-soft)]",
  major: "bg-[var(--severity-major-soft)]",
  minor: "bg-[var(--severity-minor-soft)]",
  ready: "bg-[var(--severity-ready-soft)]",
};

export function CaseCard({ data }: { data: TriageCase }) {
  const {
    id,
    severity,
    severityLabel,
    area,
    title,
    criticNote,
    ageLabel,
    sources,
    regulation,
    primaryAction,
    href,
  } = data;

  return (
    <article className="flex overflow-hidden rounded-[10px] border border-[var(--border-default)] bg-[var(--surface-primary)]">
      <div className={`severity-band ${severity}`} aria-hidden />
      <div className="flex-1 p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="mono text-[12px] text-[var(--text-secondary)]">{id}</span>
              <span
                className={`rounded-full px-2 py-[2px] text-[11px] font-medium ${severityBadgeBg[severity]} ${severityBadgeClass[severity]}`}
              >
                {severityLabel}
              </span>
              <span className="text-[11px] text-[var(--text-secondary)]">{area}</span>
            </div>
            <h3 className="mt-1.5 text-[15px] font-medium leading-snug text-[var(--text-primary)]">
              {title}
            </h3>
          </div>
          <Link
            href={href}
            className="inline-flex shrink-0 items-center gap-1 text-[13px] text-[var(--brand)] hover:text-[var(--brand-strong)]"
          >
            {primaryAction === "approve" ? "Freigeben" : "Öffnen"}
            {primaryAction === "approve" ? (
              <Check className="h-3.5 w-3.5" aria-hidden />
            ) : (
              <ArrowRight className="h-3.5 w-3.5" aria-hidden />
            )}
          </Link>
        </div>

        <p className="mt-2 text-[13px] leading-[1.55] text-[var(--text-secondary)]">
          <span className="text-[var(--text-tertiary)]">Critic:</span> „{criticNote}"
        </p>

        <div className="mt-2.5 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-[var(--text-tertiary)]">
          <span className="inline-flex items-center gap-1">
            <Clock className="h-3 w-3" aria-hidden /> {ageLabel}
          </span>
          <span>{sources}</span>
          <span className="mono">{regulation}</span>
        </div>
      </div>
    </article>
  );
}
