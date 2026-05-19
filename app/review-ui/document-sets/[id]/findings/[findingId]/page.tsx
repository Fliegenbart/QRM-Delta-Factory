import Link from "next/link";
import { getReviewPack } from "@/src/lib/review-api";
import {
  buildFindingReviewChecklist,
  cleanEvidenceQuote,
  consultantReviewCopy,
  displayRiskStatement,
  displayReviewValue,
  evidenceSourceLabel,
  evidenceRowsForFinding,
  findTopRiskById,
  isHiddenDemoDocumentSetId
} from "@/src/lib/review-ui";
import { ReviewDecisionForm } from "@/src/components/review-ui/review-decision-form";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string; findingId: string }>;
};

export default async function FindingDetailPage({ params }: PageProps) {
  const { id, findingId } = await params;

  if (isHiddenDemoDocumentSetId(id)) {
    return (
      <ReviewShell>
        <EmptyState message={consultantReviewCopy.list.empty} />
      </ReviewShell>
    );
  }

  try {
    const pack = await getReviewPack(id);
    const risk = findTopRiskById(pack, findingId);
    const evidenceRows = evidenceRowsForFinding(pack, findingId);

    if (!risk) {
      return (
        <ReviewShell>
          <EmptyState message={consultantReviewCopy.finding.notFound} />
        </ReviewShell>
      );
    }

    const uniqueEvidenceRows = Array.from(
      new Map(
        [
          ...evidenceRows,
          ...risk.evidence_quotes.map((quote) => ({
            finding_id: risk.finding_id,
            risk_statement: risk.risk_statement,
            document_id: quote.document_id,
            page: quote.page,
            chunk_id: quote.chunk_id,
            quote: quote.quote,
            requirement_references: risk.requirement_references,
            verifier_status: risk.verifier_status
          }))
        ].map((row) => [`${row.document_id}:${row.chunk_id}:${row.page}:${row.quote}`, row])
      ).values()
    );
    const reviewChecklist = buildFindingReviewChecklist({
      riskStatement: risk.risk_statement,
      requirementReferences: risk.requirement_references,
      verifierStatus: risk.verifier_status,
      evidenceRows: uniqueEvidenceRows,
      missingInformation: pack.missing_information
    });

    return (
      <ReviewShell>
        <div className="mb-4">
          <Link className="text-sm font-semibold text-teal-700" href={`/review-ui/document-sets/${id}/review-pack`}>
            {consultantReviewCopy.finding.backToPack}
          </Link>
        </div>

        <div className="grid gap-5 xl:grid-cols-[1fr_0.75fr]">
          <div className="space-y-5">
            <ReviewPanel title={consultantReviewCopy.finding.title}>
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

              <h2 className="mt-4 text-2xl font-semibold tracking-[-0.04em]">
                {displayRiskStatement(risk.risk_statement)}
              </h2>
              <dl className="mt-5 grid gap-4 md:grid-cols-2">
                <Detail label={consultantReviewCopy.finding.labels.findingId} value={risk.finding_id} mono />
                <Detail label={consultantReviewCopy.finding.labels.riskCategory} value={displayReviewValue(risk.risk_category)} />
                <Detail label={consultantReviewCopy.finding.labels.requirementReference} value={risk.requirement_references.join(", ") || "nicht verknüpft"} mono />
                <Detail label={consultantReviewCopy.finding.labels.verifierResult} value={displayReviewValue(risk.verifier_status)} />
              </dl>

              <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900">
                <strong>{consultantReviewCopy.finding.humanReason}:</strong>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  {reviewChecklist.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </ReviewPanel>

            <ReviewPanel title={consultantReviewCopy.finding.evidenceTitle}>
              {uniqueEvidenceRows.length === 0 ? (
                <EmptyState message={consultantReviewCopy.finding.noEvidence} />
              ) : (
                <div className="space-y-3">
                  {uniqueEvidenceRows.map((row, index) => (
                    <blockquote key={`${row.document_id}-${row.chunk_id}-${index}`} className="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-white/10 dark:bg-slate-900/50">
                      <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500 dark:text-slate-400">
                        Belegstelle {index + 1}
                      </div>
                      <div className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">
                        {evidenceSourceLabel(row)}
                      </div>
                      <p className="mt-3 text-sm leading-6 text-slate-800 dark:text-slate-200">"{cleanEvidenceQuote(row.quote)}"</p>
                      <footer className="mt-3 text-xs text-slate-500 dark:text-slate-400">
                        Interne Quellen-ID im Audit-Trail gespeichert.
                      </footer>
                    </blockquote>
                  ))}
                </div>
              )}
            </ReviewPanel>
          </div>

          <div className="space-y-5">
            <ReviewPanel title={consultantReviewCopy.finding.decisionForm}>
              <ReviewDecisionForm findingId={findingId} />
            </ReviewPanel>
          </div>
        </div>
      </ReviewShell>
    );
  } catch (error) {
    return (
      <ReviewShell>
        <EmptyState message={`${consultantReviewCopy.finding.loadErrorPrefix}: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`} />
      </ReviewShell>
    );
  }
}

function Detail({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500 dark:text-slate-400">{label}</dt>
      <dd className={`mt-1 text-sm text-slate-900 dark:text-slate-100 ${mono ? "font-mono text-xs" : ""}`}>{value}</dd>
    </div>
  );
}
