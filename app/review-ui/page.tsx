import Link from "next/link";
import { listDocumentSets, ReviewApiError } from "@/src/lib/review-api";
import { DeleteDocumentSetButton } from "@/src/components/review-ui/delete-document-set-button";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import { ReviewCalibrationPanel } from "@/src/components/review-ui/review-calibration-panel";
import {
  consultantReviewCopy,
  demoReviewCases,
  displayReviewValue,
  isVisibleReviewDocumentSet,
  userFacingReviewLoadError,
  type DocumentSet
} from "@/src/lib/review-ui";

export const dynamic = "force-dynamic";

export default async function ReviewUiDocumentSetsPage() {
  let documentSets: DocumentSet[] = [];
  let error: string | null = null;
  let loadState: ReturnType<typeof userFacingReviewLoadError> | null = null;

  try {
    documentSets = (await listDocumentSets()).filter(isVisibleReviewDocumentSet);
  } catch (caught) {
    if (caught instanceof ReviewApiError && caught.status === 404) {
      documentSets = [];
    } else {
      error = caught instanceof Error ? caught.message : "Prüfpakete konnten nicht geladen werden.";
      loadState = userFacingReviewLoadError(error);
    }
  }

  return (
    <ReviewShell>
      <ReviewPanel title={consultantReviewCopy.list.title}>
        {error ? (
          <EmptyState
            title={loadState?.title ?? consultantReviewCopy.list.loadErrorPrefix}
            message={loadState?.message ?? error}
            action={
              <>
                <Link
                  className="rounded-md bg-slate-950 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200"
                  href="/"
                >
                  Neuen Prüffall vorbereiten
                </Link>
                <Link
                  className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-50 dark:border-white/10 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-800"
                  href={demoReviewCases[0].href}
                >
                  Demo-Fall ansehen
                </Link>
              </>
            }
          />
        ) : documentSets.length === 0 ? (
          <EmptyState
            title="Noch kein echter Prüffall"
            message={consultantReviewCopy.list.empty}
            action={
              <Link
                className="rounded-md bg-slate-950 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200"
                href="/"
              >
                Prüffall anlegen
              </Link>
            }
          />
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
                    <td className="px-4 py-4">{displayReviewValue(documentSet.declared_document_type)}</td>
                    <td className="px-4 py-4">{displayReviewValue(documentSet.declared_process_area)}</td>
                    <td className="px-4 py-4">
                      <StatusBadge tone={statusTone(documentSet.status)}>
                        {displayReviewValue(documentSet.status)}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-4">{documentSet.document_ids.length}</td>
                    <td className="px-4 py-4">
                      <div className="flex items-start justify-end gap-2">
                        <Link
                          className="rounded-xl bg-slate-950 px-3 py-2 text-xs font-semibold text-white"
                          href={`/review-ui/document-sets/${documentSet.document_set_id}`}
                        >
                          {consultantReviewCopy.list.open}
                        </Link>
                        <DeleteDocumentSetButton documentSetId={documentSet.document_set_id} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </ReviewPanel>
      {!error ? (
        <ReviewPanel title="Setup: KI-Kalibrierung">
          <ReviewCalibrationPanel />
        </ReviewPanel>
      ) : null}
    </ReviewShell>
  );
}

function statusTone(status: string): "green" | "amber" | "red" | "slate" {
  if (status.includes("failed") || status.includes("blocked") || status.includes("error")) return "red";
  if (status.includes("review") || status.includes("pending") || status.includes("incomplete")) return "amber";
  if (status.includes("ready") || status.includes("completed")) return "green";
  return "slate";
}
