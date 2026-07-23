import Link from "next/link";
import { AlertCircle, ArrowRight, CheckCircle2 } from "lucide-react";
import { getReviewPack } from "@/src/lib/review-api";
import { deriveReviewPackPublication } from "@/src/lib/review-pack-export";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import { ReviewPackExportActions } from "@/src/components/review-ui/review-pack-export-actions";
import {
  consultantReviewCopy,
  displayMissingInformationList,
  displayReviewReasons,
  displayRiskStatement,
  displayReviewValue,
  isHiddenDemoDocumentSetId,
  reviewPackRiskPresentation,
  reviewPackProgress,
  userFacingReviewLoadError
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
    const presentation = reviewPackRiskPresentation(pack);

    return (
      <ReviewShell>
        <div className="space-y-5">
          <ReviewPanel
            title={consultantReviewCopy.pack.title}
            action={
              <div className="flex flex-wrap items-center justify-end gap-2">
                <ReviewPackExportActions pack={pack} />
                <StatusBadge tone={pack.decision.auto_clear_allowed ? "green" : "amber"}>{displayReviewValue(pack.decision.decision)}</StatusBadge>
              </div>
            }
          >
            <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
              <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3">
                <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
                  Kurzantwort
                </div>
                <p className="mt-1 text-sm leading-6 text-[var(--text-primary)]">
                  {presentation.summary}
                </p>
              </div>
              <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3">
                <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
                  Kernrisiken
                </div>
                <p className="mt-1 text-sm leading-6 text-[var(--text-primary)]">
                  {presentation.rootRisks.length} Kernrisiko{presentation.rootRisks.length === 1 ? "" : "en"}
                  {presentation.supportingFindingCount > 0
                    ? ` · ${presentation.supportingFindingCount} unterstützende${presentation.supportingFindingCount === 1 ? "s" : ""} Signal${presentation.supportingFindingCount === 1 ? "" : "e"}`
                    : ""}
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

          <ReviewPanel title="Kanonische Risikobefunde und QA-Hinweise mit unvollständiger Evidenz">
            {presentation.rootRisks.length === 0 ? (
              <EmptyState message={consultantReviewCopy.pack.emptyFindings} />
            ) : (
              <div className="space-y-3">
                {presentation.rootRisks.map((risk) => (
                  <article key={risk.finding_id} className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                      <div>
                        <div className="flex flex-wrap gap-2">
                          <StatusBadge tone={risk.severity === "critical" || risk.severity === "high" ? "red" : "amber"}>
                            {displayReviewValue(risk.severity)}
                          </StatusBadge>
                          <StatusBadge>{displayReviewValue(risk.risk_category ?? "risk")}</StatusBadge>
                          <StatusBadge>{displayReviewValue(risk.verifier_status)}</StatusBadge>
                          <StatusBadge tone={deriveReviewPackPublication(risk.verifier_status).state === "canonical" ? "green" : "amber"}>
                            {deriveReviewPackPublication(risk.verifier_status).label}
                          </StatusBadge>
                          {risk.review_status === "reviewed" ? (
                            <StatusBadge tone="green">
                              {displayReviewValue(risk.latest_review_decision ?? "reviewed")}
                            </StatusBadge>
                          ) : null}
                        </div>
                        <h3 className="mt-3 text-lg font-semibold leading-snug text-[var(--text-primary)]">{displayRiskStatement(risk.risk_statement)}</h3>
                        {deriveReviewPackPublication(risk.verifier_status).state === "qa_hint_partial" ? (
                          <p className="mt-2 text-sm font-medium text-amber-700 dark:text-amber-300">
                            QA-Hinweis mit unvollständiger Evidenz — kein kanonischer Risikobefund.
                          </p>
                        ) : null}
                        <div className="mt-3 text-xs text-[var(--text-tertiary)]">
                          {consultantReviewCopy.pack.requirement}: {risk.requirement_references.join(", ") || consultantReviewCopy.pack.notLinked}
                        </div>
                        {risk.supporting_signals && risk.supporting_signals.length > 0 ? (
                          <details className="mt-3 text-sm text-[var(--text-secondary)]">
                            <summary className="cursor-pointer font-medium text-[var(--brand)]">
                              {risk.supporting_signals.length} unterstützende{risk.supporting_signals.length === 1 ? "s Signal" : " Signale"} anzeigen
                            </summary>
                            <ul className="mt-2 space-y-2 border-l border-[var(--border-default)] pl-3">
                              {risk.supporting_signals.map((signal) => (
                                <li key={signal.finding_id}>
                                  <p>{displayRiskStatement(signal.risk_statement)}</p>
                                  {signal.evidence_quotes[0] ? (
                                    <p className="mt-1 text-xs text-[var(--text-tertiary)]">
                                      Quelle, Seite {signal.evidence_quotes[0].page}: {signal.evidence_quotes[0].quote}
                                    </p>
                                  ) : null}
                                </li>
                              ))}
                            </ul>
                          </details>
                        ) : null}
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

          {presentation.operationalWarnings.length > 0 || presentation.modelCoverageStatus ? (
            <ReviewPanel title="Technische Hinweise">
              <p className="text-sm leading-6 text-[var(--text-secondary)]">
                Diese Hinweise betreffen die technische Abdeckung der Prüfung und ersetzen keine QA-Bewertung.
              </p>
              {presentation.modelCoverageStatus ? (
                <p className="mt-3 text-sm font-medium text-[var(--text-primary)]">
                  Technische Abdeckung: {presentation.modelCoverageStatus}
                </p>
              ) : null}
              {presentation.operationalWarnings.length > 0 ? (
                <ReasonList reasons={presentation.operationalWarnings} />
              ) : null}
            </ReviewPanel>
          ) : null}

          <div className="grid gap-4 lg:grid-cols-2">
            <ReviewPanel title={consultantReviewCopy.pack.humanReasons}>
              <ReasonList reasons={reviewReasons} />
            </ReviewPanel>
            <ReviewPanel title={consultantReviewCopy.pack.missingInformation}>
              <ReasonList reasons={pack.missing_information} kind="missing" />
            </ReviewPanel>
          </div>
        </div>
      </ReviewShell>
    );
  } catch (error) {
    return (
      <ReviewShell>
        <EmptyState message={userFacingReviewLoadError(error instanceof Error ? error.message : "").message} />
      </ReviewShell>
    );
  }
}

function ReasonList({ reasons, kind = "review" }: { reasons: string[]; kind?: "review" | "missing" }) {
  if (reasons.length === 0) {
    return (
      <p className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
        <CheckCircle2 className="h-4 w-4 text-[var(--brand)]" aria-hidden />
        {consultantReviewCopy.pack.noEntries}
      </p>
    );
  }

  const uniqueReasons =
    kind === "missing"
      ? displayMissingInformationList(reasons)
      : displayReviewReasons(reasons.join(";"));
  return (
    <div>
      {uniqueReasons.length === 0 ? (
        <p className="mt-1 text-sm text-[var(--text-secondary)]">{consultantReviewCopy.pack.noEntries}</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {uniqueReasons.map((reason) => (
            <li key={reason} className="flex items-start gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-3 py-2 text-sm text-[var(--text-secondary)]">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600 dark:text-amber-300" aria-hidden />
              {reason}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
