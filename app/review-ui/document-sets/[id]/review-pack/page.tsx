import Link from "next/link";
import { AlertCircle, ArrowRight, CheckCircle2 } from "lucide-react";
import { getReviewPack } from "@/src/lib/review-api";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import {
  consultantReviewCopy,
  displayReviewPackSummary,
  displayReviewReasons,
  displayRiskStatement,
  displayReviewValue,
  isHiddenDemoDocumentSetId,
  reviewPackProgress
} from "@/src/lib/review-ui";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function ReviewPackPage({ params }: PageProps) {
  const { id } = await params;

  if (isHiddenDemoDocumentSetId(id)) {
    return (
      <ReviewShell>
        <EmptyState message={consultantReviewCopy.list.empty} />
      </ReviewShell>
    );
  }

  try {
    const pack = await getReviewPack(id);
    const reviewReasons = [
      ...(pack.decision.required_human_review_reasons ?? []),
      ...pack.ood_reasons,
      ...pack.coverage_gap_reasons
    ];
    const progress = reviewPackProgress(pack);

    return (
      <ReviewShell>
        <div className="space-y-5">
          <ReviewPanel
            title={consultantReviewCopy.pack.title}
            action={<StatusBadge tone={pack.decision.auto_clear_allowed ? "green" : "amber"}>{displayReviewValue(pack.decision.decision)}</StatusBadge>}
          >
            <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
              <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3">
                <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
                  Kurzantwort
                </div>
                <p className="mt-1 text-sm leading-6 text-[var(--text-primary)]">
                  {displayReviewPackSummary({
                    decision: pack.decision.decision,
                    findingCount: pack.top_risks.length,
                    maxSeverity: pack.decision.max_severity
                  })}
                </p>
              </div>
              <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3">
                <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
                  QA-Ziel
                </div>
                <p className="mt-1 text-sm leading-6 text-[var(--text-primary)]">
                  Prüfpunkte bearbeiten, Lücken klären, Entscheidung dokumentieren.
                </p>
              </div>
            </div>
            <div className="mt-5">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-semibold text-[var(--text-primary)]">
                  {progress.label}
                </span>
                <span className="text-[var(--text-tertiary)]">
                  Menschliche Bearbeitung
                </span>
              </div>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-[var(--surface-secondary)]">
                <div
                  className="h-full rounded-full bg-[var(--brand)] transition-all"
                  style={{ width: `${progress.percent}%` }}
                />
              </div>
            </div>
          </ReviewPanel>

          <ReviewPanel title={consultantReviewCopy.pack.findingsTitle}>
            {pack.top_risks.length === 0 ? (
              <EmptyState message={consultantReviewCopy.pack.emptyFindings} />
            ) : (
              <div className="space-y-3">
                {pack.top_risks.map((risk) => (
                  <article key={risk.finding_id} className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                      <div>
                        <div className="flex flex-wrap gap-2">
                          <StatusBadge tone={risk.severity === "critical" || risk.severity === "high" ? "red" : "amber"}>
                            {displayReviewValue(risk.severity)}
                          </StatusBadge>
                          <StatusBadge>{displayReviewValue(risk.risk_category ?? "risk")}</StatusBadge>
                          <StatusBadge>{displayReviewValue(risk.verifier_status)}</StatusBadge>
                          {risk.review_status === "reviewed" ? (
                            <StatusBadge tone="green">
                              {displayReviewValue(risk.latest_review_decision ?? "reviewed")}
                            </StatusBadge>
                          ) : null}
                        </div>
                        <h3 className="mt-3 text-lg font-semibold leading-snug text-[var(--text-primary)]">{displayRiskStatement(risk.risk_statement)}</h3>
                        <div className="mt-3 text-xs text-[var(--text-tertiary)]">
                          {consultantReviewCopy.pack.requirement}: {risk.requirement_references.join(", ") || consultantReviewCopy.pack.notLinked}
                        </div>
                      </div>
                      <Link
                        className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-center text-sm font-semibold text-[var(--brand)] hover:border-[var(--brand)] hover:bg-[var(--brand-soft)]"
                        href={`/review-ui/document-sets/${id}/findings/${risk.finding_id}`}
                      >
                        {consultantReviewCopy.pack.openFinding}
                        <ArrowRight className="h-4 w-4" aria-hidden />
                      </Link>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </ReviewPanel>

          <div className="grid gap-4 lg:grid-cols-2">
            <ReviewPanel title={consultantReviewCopy.pack.humanReasons}>
              <ReasonList reasons={reviewReasons} />
            </ReviewPanel>
            <ReviewPanel title={consultantReviewCopy.pack.missingInformation}>
              <ReasonList reasons={pack.missing_information} />
            </ReviewPanel>
          </div>
        </div>
      </ReviewShell>
    );
  } catch (error) {
    return (
      <ReviewShell>
        <EmptyState message={`${consultantReviewCopy.pack.loadError} ${error instanceof Error ? error.message : ""}`} />
      </ReviewShell>
    );
  }
}

function ReasonList({ reasons }: { reasons: string[] }) {
  if (reasons.length === 0) {
    return (
      <p className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
        <CheckCircle2 className="h-4 w-4 text-[var(--brand)]" aria-hidden />
        {consultantReviewCopy.pack.noEntries}
      </p>
    );
  }

  const uniqueReasons = displayReviewReasons(reasons.join(";"));
  return (
    <div>
      {uniqueReasons.length === 0 ? (
        <p className="mt-1 text-sm text-[var(--text-secondary)]">{consultantReviewCopy.pack.noEntries}</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {uniqueReasons.map((reason) => (
            <li key={reason} className="flex items-start gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-3 py-2 text-sm text-[var(--text-secondary)]">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" aria-hidden />
              {reason}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
