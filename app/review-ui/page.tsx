import Link from "next/link";
import { listDocumentSets, ReviewApiError } from "@/src/lib/review-api";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import { consultantReviewCopy, type DocumentSet } from "@/src/lib/review-ui";

export const dynamic = "force-dynamic";

export default async function ReviewUiDocumentSetsPage() {
  let documentSets: DocumentSet[] = [];
  let error: string | null = null;

  try {
    documentSets = await listDocumentSets();
  } catch (caught) {
    if (caught instanceof ReviewApiError && caught.status === 404) {
      documentSets = [];
    } else {
      error = caught instanceof Error ? caught.message : "Prüfpakete konnten nicht geladen werden.";
    }
  }

  return (
    <ReviewShell>
      <ReviewPanel title={consultantReviewCopy.list.title}>
        {error ? (
          <EmptyState message={`${consultantReviewCopy.list.loadErrorPrefix}: ${error}`} />
        ) : documentSets.length === 0 ? (
          <EmptyState message={consultantReviewCopy.list.empty} />
        ) : (
          <div className="overflow-hidden rounded-2xl border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-[0.16em] text-slate-500">
                <tr>
                  <th className="px-4 py-3">{consultantReviewCopy.list.columns.package}</th>
                  <th className="px-4 py-3">{consultantReviewCopy.list.columns.trigger}</th>
                  <th className="px-4 py-3">{consultantReviewCopy.list.columns.area}</th>
                  <th className="px-4 py-3">{consultantReviewCopy.list.columns.status}</th>
                  <th className="px-4 py-3">{consultantReviewCopy.list.columns.sources}</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {documentSets.map((documentSet) => (
                  <tr key={documentSet.document_set_id} className="bg-white">
                    <td className="px-4 py-4 font-mono text-xs">{documentSet.document_set_id}</td>
                    <td className="px-4 py-4">{documentSet.declared_document_type}</td>
                    <td className="px-4 py-4">{documentSet.declared_process_area}</td>
                    <td className="px-4 py-4">
                      <StatusBadge tone={statusTone(documentSet.status)}>
                        {documentSet.status}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-4">{documentSet.document_ids.length}</td>
                    <td className="px-4 py-4 text-right">
                      <Link
                        className="rounded-xl bg-slate-950 px-3 py-2 text-xs font-semibold text-white"
                        href={`/review-ui/document-sets/${documentSet.document_set_id}`}
                      >
                        {consultantReviewCopy.list.open}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </ReviewPanel>
    </ReviewShell>
  );
}

function statusTone(status: string): "green" | "amber" | "red" | "slate" {
  if (status.includes("failed") || status.includes("blocked") || status.includes("error")) return "red";
  if (status.includes("review") || status.includes("pending") || status.includes("incomplete")) return "amber";
  if (status.includes("ready") || status.includes("completed")) return "green";
  return "slate";
}
