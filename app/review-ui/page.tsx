import Link from "next/link";
import { listDocumentSets } from "@/src/lib/review-api";
import { DemoSeedButton } from "@/src/components/review-ui/demo-seed-button";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import type { DocumentSet } from "@/src/lib/review-ui";

export const dynamic = "force-dynamic";

export default async function ReviewUiDocumentSetsPage() {
  let documentSets: DocumentSet[] = [];
  let error: string | null = null;

  try {
    documentSets = await listDocumentSets();
  } catch (caught) {
    error = caught instanceof Error ? caught.message : "Could not load DocumentSets.";
  }

  return (
    <ReviewShell>
      <ReviewPanel title="DocumentSet Liste" action={<DemoSeedButton />}>
        {error ? (
          <EmptyState message={`Backend nicht erreichbar oder nicht konfiguriert: ${error}`} />
        ) : documentSets.length === 0 ? (
          <EmptyState message="Keine DocumentSets gefunden. Klicke auf Demo-Daten erzeugen, um einen synthetischen AVI-Threshold-Change mit Pipeline und Review Pack anzulegen." />
        ) : (
          <div className="overflow-hidden rounded-2xl border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-[0.16em] text-slate-500">
                <tr>
                  <th className="px-4 py-3">DocumentSet</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Process Area</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Documents</th>
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
                      <StatusBadge tone={documentSet.status.includes("review") ? "amber" : "green"}>
                        {documentSet.status}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-4">{documentSet.document_ids.length}</td>
                    <td className="px-4 py-4 text-right">
                      <Link
                        className="rounded-xl bg-slate-950 px-3 py-2 text-xs font-semibold text-white"
                        href={`/review-ui/document-sets/${documentSet.document_set_id}`}
                      >
                        Öffnen
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
