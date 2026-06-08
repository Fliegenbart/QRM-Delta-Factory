import Link from "next/link";
import { ArrowRight, FileText } from "lucide-react";
import { getDocumentSet } from "@/src/lib/review-api";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import {
  consultantReviewCopy,
  displayReviewValue,
  isHiddenDemoDocumentSetId
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
    const documentSet = await getDocumentSet(id);

    return (
      <ReviewShell>
        <div className="grid gap-5 lg:grid-cols-[0.8fr_0.4fr]">
          <ReviewPanel
            title={consultantReviewCopy.detail.title}
            action={
              <Link
                className="inline-flex h-9 items-center gap-2 rounded-md bg-[var(--brand)] px-3 text-sm font-semibold text-white hover:bg-[var(--brand-strong)]"
                href={`/review-ui/document-sets/${id}/review-pack`}
              >
                {consultantReviewCopy.detail.openReviewPack}
                <ArrowRight className="h-4 w-4" aria-hidden />
              </Link>
            }
          >
            <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3">
              <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
                Kurzstatus
              </div>
              <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                Der Prüffall ist angelegt. Öffne die Prüfmappe, um Prüfpunkte, Quellen,
                fehlende Nachweise und die QA-Entscheidung zu bearbeiten.
              </p>
            </div>

            <dl className="mt-5 grid gap-4 md:grid-cols-2">
              <Detail label={consultantReviewCopy.detail.labels.documentType} value={displayReviewValue(documentSet.declared_document_type)} />
              <Detail label={consultantReviewCopy.detail.labels.processArea} value={displayReviewValue(documentSet.declared_process_area)} />
              <Detail label={consultantReviewCopy.detail.labels.uploadedBy} value={documentSet.uploaded_by} />
              <Detail label={consultantReviewCopy.detail.labels.uploaded} value={new Date(documentSet.upload_timestamp).toLocaleString()} />
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
                {documentSet.document_ids.map((documentId) => (
                  <li key={documentId} className="flex items-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-3 py-2 text-xs text-[var(--text-secondary)]">
                    <FileText className="h-4 w-4 shrink-0 text-[var(--brand)]" aria-hidden />
                    <span className="min-w-0 truncate font-mono">{documentId}</span>
                  </li>
                ))}
              </ul>
            )}
          </ReviewPanel>
        </div>
      </ReviewShell>
    );
  } catch (error) {
    return (
      <ReviewShell>
        <EmptyState message={`${consultantReviewCopy.detail.loadErrorPrefix}: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`} />
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
