import Link from "next/link";
import { ArrowRight, FileText, FileWarning } from "lucide-react";
import { PipelineRunStatus } from "@/src/components/review-ui/pipeline-run-status";
import {
  getDocumentSet,
  getLatestPipelineRun,
  listDocumentSetDocuments,
  ReviewApiError
} from "@/src/lib/review-api";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import {
  consultantReviewCopy,
  displayReviewValue,
  isHiddenDemoDocumentSetId,
  unreadableDocuments,
  userFacingReviewLoadError,
  type DocumentSummary
} from "@/src/lib/review-ui";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function DocumentSetDetailPage({ params }: PageProps) {
  const { id } = await params;

  if (isHiddenDemoDocumentSetId(id)) {
    return (
      <ReviewShell>
        <EmptyState message={consultantReviewCopy.list.empty} />
      </ReviewShell>
    );
  }

  try {
    const [documentSet, pipelineRun, documents] = await Promise.all([
      getDocumentSet(id),
      getLatestPipelineRun(id).catch((error) => {
        if (error instanceof ReviewApiError && error.status === 404) return null;
        throw error;
      }),
      // The listing is additive: an older backend without this endpoint should
      // cost the reviewer the filenames, not the whole case view.
      listDocumentSetDocuments(id).catch(() => [] as DocumentSummary[])
    ]);
    const reviewPackReady = !pipelineRun || ["completed", "needs_human_review"].includes(pipelineRun.status);
    const unreadable = unreadableDocuments(documents);

    return (
      <ReviewShell>
        <div className="grid gap-5 lg:grid-cols-[0.8fr_0.4fr]">
          <ReviewPanel
            title={consultantReviewCopy.detail.title}
            action={reviewPackReady ? (
              <div className="flex flex-wrap items-center justify-end gap-2">
                {/* The coverage report leads: it answers the question a QA
                    reviewer actually asks -- is every obligation met, and where
                    is the proof -- while the pack lists what was noticed. */}
                <Link
                  className="inline-flex h-9 items-center gap-2 rounded-md bg-[var(--brand)] px-3 text-sm font-semibold text-white hover:bg-[var(--brand-strong)]"
                  href={`/review-ui/document-sets/${id}/anforderungen`}
                >
                  Anforderungsabdeckung öffnen
                  <ArrowRight className="h-4 w-4" aria-hidden />
                </Link>
                <Link
                  className="inline-flex h-9 items-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-sm font-semibold text-[var(--text-primary)] hover:border-[var(--brand)] hover:bg-[var(--brand-soft)]"
                  href={`/review-ui/document-sets/${id}/review-pack`}
                >
                  {consultantReviewCopy.detail.openReviewPack}
                </Link>
              </div>
            ) : undefined}
          >
            {unreadable.length > 0 ? (
              <div className="mb-4 rounded-md border border-[#b42318] bg-[#fef3f2] px-4 py-3">
                <div className="flex items-center gap-2">
                  <FileWarning className="h-4 w-4 shrink-0 text-[#b42318]" aria-hidden />
                  <p className="text-sm font-semibold text-[#912018]">
                    {unreadable.length === documents.length
                      ? "Keine der hochgeladenen Unterlagen konnte gelesen werden."
                      : `${unreadable.length} von ${documents.length} Unterlagen konnten nicht gelesen werden.`}
                  </p>
                </div>
                <p className="mt-1 text-sm leading-6 text-[#912018]">
                  {unreadable.length === documents.length
                    ? "Diese Prüfmappe stützt sich auf keinen einzigen gelesenen Text. Ihr Ergebnis ist kein Prüfergebnis. Bitte laden Sie die Unterlagen als PDF, Word oder Text erneut hoch."
                    : "Die betroffenen Dokumente sind nicht in die Prüfung eingegangen. Was in der Prüfmappe fehlt, kann daran liegen — nicht am Inhalt der Unterlagen."}
                </p>
              </div>
            ) : null}

            {pipelineRun ? (
              <PipelineRunStatus documentSetId={id} initialPipelineRun={pipelineRun} />
            ) : (
              <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3">
                <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
                  Kurzstatus
                </div>
                <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                  Der Prüffall ist angelegt. Öffne die Prüfmappe, um Prüfpunkte, Quellen,
                  fehlende Nachweise und die QA-Entscheidung zu bearbeiten.
                </p>
              </div>
            )}

            <dl className="mt-5 grid gap-4 md:grid-cols-2">
              <Detail label={consultantReviewCopy.detail.labels.documentType} value={displayReviewValue(documentSet.declared_document_type)} />
              <Detail label={consultantReviewCopy.detail.labels.processArea} value={displayReviewValue(documentSet.declared_process_area)} />
              <Detail label={consultantReviewCopy.detail.labels.uploadedBy} value={documentSet.uploaded_by} />
              <Detail label={consultantReviewCopy.detail.labels.uploaded} value={`${new Date(documentSet.upload_timestamp).toLocaleString("de-DE", { dateStyle: "medium", timeStyle: "short", timeZone: "Europe/Berlin" })} Uhr`} />
              <div>
                <dt className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">{consultantReviewCopy.detail.labels.status}</dt>
                <dd className="mt-2">
                  <StatusBadge tone={documentSet.status.includes("review") ? "amber" : "green"}>
                    {displayReviewValue(documentSet.status)}
                  </StatusBadge>
                </dd>
              </div>
              <Detail label={consultantReviewCopy.detail.labels.requirementSet} value={documentSet.requirement_set_id} mono />
              <Detail label={consultantReviewCopy.detail.labels.packageId} value={documentSet.document_set_id} mono />
            </dl>
          </ReviewPanel>

          <ReviewPanel title={consultantReviewCopy.detail.sourcesTitle}>
            {documentSet.document_ids.length === 0 ? (
              <EmptyState message={consultantReviewCopy.detail.noSources} />
            ) : (
              <ul className="space-y-2">
                {/* Fall back to the ids only if the listing was unavailable --
                    a hash is still better than an empty panel. */}
                {(documents.length > 0
                  ? documents
                  : documentSet.document_ids.map((documentId) => ({
                      document_id: documentId,
                      filename: documentId,
                      parsing_status: "unknown",
                      page_count: 0
                    }))
                ).map((document) => {
                  const readable = document.parsing_status === "parsed";
                  return (
                    <li
                      key={document.document_id}
                      className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-3 py-2"
                    >
                      <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
                        {readable ? (
                          <FileText className="h-4 w-4 shrink-0 text-[var(--brand)]" aria-hidden />
                        ) : (
                          <FileWarning className="h-4 w-4 shrink-0 text-[var(--danger, #b42318)]" aria-hidden />
                        )}
                        <span className="min-w-0 truncate" title={document.filename}>
                          {document.filename}
                        </span>
                      </div>
                      {readable ? null : (
                        <p className="mt-1 pl-6 text-[11px] leading-5 text-[var(--text-tertiary)]">
                          Text konnte nicht gelesen werden — dieses Dokument ist
                          nicht in die Prüfung eingegangen.
                        </p>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </ReviewPanel>
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

function Detail({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">{label}</dt>
      <dd className={`mt-1 text-sm text-[var(--text-primary)] ${mono ? "font-mono text-xs" : ""}`}>{value}</dd>
    </div>
  );
}
