import Link from "next/link";
import { getDocumentSet } from "@/src/lib/review-api";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function DocumentSetDetailPage({ params }: PageProps) {
  const { id } = await params;
  try {
    const documentSet = await getDocumentSet(id);

    return (
      <ReviewShell>
        <div className="grid gap-5 lg:grid-cols-[0.8fr_0.4fr]">
          <ReviewPanel
            title="DocumentSet Detail"
            action={
              <Link
                className="rounded-xl bg-teal-700 px-4 py-2 text-sm font-semibold text-white"
                href={`/review-ui/document-sets/${id}/review-pack`}
              >
                Review Pack öffnen
              </Link>
            }
          >
            <dl className="grid gap-4 md:grid-cols-2">
              <Detail label="DocumentSet ID" value={documentSet.document_set_id} mono />
              <Detail label="Tenant" value={documentSet.tenant_id} />
              <Detail label="RequirementSet" value={documentSet.requirement_set_id} mono />
              <Detail label="Uploaded by" value={documentSet.uploaded_by} />
              <Detail label="Document Type" value={documentSet.declared_document_type} />
              <Detail label="Process Area" value={documentSet.declared_process_area} />
              <Detail label="Uploaded" value={new Date(documentSet.upload_timestamp).toLocaleString()} />
              <div>
                <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Status</dt>
                <dd className="mt-2">
                  <StatusBadge tone={documentSet.status.includes("review") ? "amber" : "green"}>
                    {documentSet.status}
                  </StatusBadge>
                </dd>
              </div>
            </dl>
          </ReviewPanel>

          <ReviewPanel title="Dokument-Referenzen">
            {documentSet.document_ids.length === 0 ? (
              <EmptyState message="Keine Dokumente verknüpft." />
            ) : (
              <ul className="space-y-2">
                {documentSet.document_ids.map((documentId) => (
                  <li key={documentId} className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 font-mono text-xs">
                    {documentId}
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
        <EmptyState message={`DocumentSet konnte nicht geladen werden: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`} />
      </ReviewShell>
    );
  }
}

function Detail({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</dt>
      <dd className={`mt-1 text-sm text-slate-900 ${mono ? "font-mono text-xs" : ""}`}>{value}</dd>
    </div>
  );
}
