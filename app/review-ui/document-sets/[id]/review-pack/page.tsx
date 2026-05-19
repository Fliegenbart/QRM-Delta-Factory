import Link from "next/link";
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
            <p className="text-sm leading-6 text-slate-700 dark:text-slate-300">
              {displayReviewPackSummary({
                decision: pack.decision.decision,
                findingCount: pack.top_risks.length,
                maxSeverity: pack.decision.max_severity
              })}
            </p>
            <div className="mt-4">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-semibold text-slate-900 dark:text-white">
                  {progress.label}
                </span>
                <span className="text-slate-500 dark:text-slate-400">
                  Menschliche Bearbeitung
                </span>
              </div>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-900">
                <div
                  className="h-full rounded-full bg-teal-600 transition-all"
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
                  <article key={risk.finding_id} className="rounded-2xl border border-slate-200 p-4 dark:border-white/10 dark:bg-slate-900/35">
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
                        <h3 className="mt-3 text-lg font-semibold tracking-[-0.02em] text-slate-950 dark:text-white">{displayRiskStatement(risk.risk_statement)}</h3>
                        <div className="mt-3 text-xs text-slate-500 dark:text-slate-400">
                          {consultantReviewCopy.pack.requirement}: {risk.requirement_references.join(", ") || consultantReviewCopy.pack.notLinked}
                        </div>
                      </div>
                      <Link
                        className="rounded-xl bg-slate-950 px-4 py-2 text-center text-sm font-semibold text-white"
                        href={`/review-ui/document-sets/${id}/findings/${risk.finding_id}`}
                      >
                        {consultantReviewCopy.pack.openFinding}
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
    return <p className="text-sm text-slate-500">{consultantReviewCopy.pack.noEntries}</p>;
  }

  const uniqueReasons = displayReviewReasons(reasons.join(";"));
  return (
    <div>
      {uniqueReasons.length === 0 ? (
        <p className="mt-1 text-sm text-slate-500">{consultantReviewCopy.pack.noEntries}</p>
      ) : (
        <ul className="mt-2 space-y-1">
          {uniqueReasons.map((reason) => (
            <li key={reason} className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700 dark:bg-slate-900/70 dark:text-slate-200">
              {reason}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
