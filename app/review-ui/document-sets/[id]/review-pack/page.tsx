import Link from "next/link";
import { getReviewPack } from "@/src/lib/review-api";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import { consultantReviewCopy } from "@/src/lib/review-ui";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function ReviewPackPage({ params }: PageProps) {
  const { id } = await params;

  try {
    const pack = await getReviewPack(id);
    const reviewReasons = [
      ...(pack.decision.required_human_review_reasons ?? []),
      ...pack.ood_reasons,
      ...pack.coverage_gap_reasons
    ];

    return (
      <ReviewShell>
        <div className="space-y-5">
          <ReviewPanel
            title={consultantReviewCopy.pack.title}
            action={<StatusBadge tone={pack.decision.auto_clear_allowed ? "green" : "amber"}>{pack.decision.decision}</StatusBadge>}
          >
            <div className="grid gap-4 lg:grid-cols-[1fr_0.7fr]">
              <div>
                <p className="text-sm leading-6 text-slate-700">{pack.summary}</p>
                <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900">
                  {consultantReviewCopy.pack.humanNotice}
                </div>
              </div>
              <div className="space-y-2">
                <ReasonList title={consultantReviewCopy.pack.humanReasons} reasons={reviewReasons} />
                <ReasonList title={consultantReviewCopy.pack.missingInformation} reasons={pack.missing_information} />
              </div>
            </div>
          </ReviewPanel>

          <ReviewPanel title={consultantReviewCopy.pack.findingsTitle}>
            {pack.top_risks.length === 0 ? (
              <EmptyState message={consultantReviewCopy.pack.emptyFindings} />
            ) : (
              <div className="space-y-3">
                {pack.top_risks.map((risk) => (
                  <article key={risk.finding_id} className="rounded-2xl border border-slate-200 p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                      <div>
                        <div className="flex flex-wrap gap-2">
                          <StatusBadge tone={risk.severity === "critical" || risk.severity === "high" ? "red" : "amber"}>
                            {risk.severity}
                          </StatusBadge>
                          <StatusBadge>{risk.risk_category ?? "risk"}</StatusBadge>
                          <StatusBadge>{risk.verifier_status}</StatusBadge>
                        </div>
                        <h3 className="mt-3 text-lg font-semibold tracking-[-0.02em]">{risk.risk_statement}</h3>
                        <p className="mt-2 text-sm leading-6 text-slate-600">{risk.human_review_reason}</p>
                        <div className="mt-3 text-xs text-slate-500">
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

function ReasonList({ title, reasons }: { title: string; reasons: string[] }) {
  const uniqueReasons = Array.from(new Set(reasons));
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{title}</h3>
      {uniqueReasons.length === 0 ? (
        <p className="mt-1 text-sm text-slate-500">{consultantReviewCopy.pack.noEntries}</p>
      ) : (
        <ul className="mt-2 space-y-1">
          {uniqueReasons.map((reason) => (
            <li key={reason} className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700">
              {reason}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
