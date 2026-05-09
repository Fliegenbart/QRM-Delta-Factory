import Link from "next/link";
import { getReviewPack } from "@/src/lib/review-api";
import {
  evidenceRowsForFinding,
  findTopRiskById,
  modelPositionForFinding
} from "@/src/lib/review-ui";
import { ReviewDecisionForm } from "@/src/components/review-ui/review-decision-form";
import { EmptyState, ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string; findingId: string }>;
};

export default async function FindingDetailPage({ params }: PageProps) {
  const { id, findingId } = await params;

  try {
    const pack = await getReviewPack(id);
    const risk = findTopRiskById(pack, findingId);
    const evidenceRows = evidenceRowsForFinding(pack, findingId);
    const modelPosition = modelPositionForFinding(pack, findingId);

    if (!risk) {
      return (
        <ReviewShell>
          <EmptyState message="Finding wurde im Review Pack nicht gefunden." />
        </ReviewShell>
      );
    }

    return (
      <ReviewShell>
        <div className="mb-4">
          <Link className="text-sm font-semibold text-teal-700" href={`/review-ui/document-sets/${id}/review-pack`}>
            Zurück zum Review Pack
          </Link>
        </div>

        <div className="grid gap-5 xl:grid-cols-[1fr_0.75fr]">
          <div className="space-y-5">
            <ReviewPanel title="Finding Detail mit Evidenz">
              <div className="flex flex-wrap gap-2">
                <StatusBadge tone={risk.severity === "critical" || risk.severity === "high" ? "red" : "amber"}>
                  {risk.severity}
                </StatusBadge>
                <StatusBadge>{risk.risk_category ?? "risk"}</StatusBadge>
                <StatusBadge>{risk.verifier_status}</StatusBadge>
              </div>

              <h2 className="mt-4 text-2xl font-semibold tracking-[-0.04em]">{risk.risk_statement}</h2>
              <dl className="mt-5 grid gap-4 md:grid-cols-2">
                <Detail label="Finding ID" value={risk.finding_id} mono />
                <Detail label="Risk Category" value={risk.risk_category ?? "not provided"} />
                <Detail label="Requirement Reference" value={risk.requirement_references.join(", ") || "not linked"} mono />
                <Detail label="Verifier Result" value={risk.verifier_status} />
              </dl>

              <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900">
                <strong>Required human review reason:</strong> {risk.human_review_reason}
              </div>
            </ReviewPanel>

            <ReviewPanel title="Evidence Quotes">
              {evidenceRows.length === 0 && risk.evidence_quotes.length === 0 ? (
                <EmptyState message="Keine Evidenzzitate im Review Pack verknüpft." />
              ) : (
                <div className="space-y-3">
                  {[...evidenceRows, ...risk.evidence_quotes.map((quote) => ({
                    finding_id: risk.finding_id,
                    risk_statement: risk.risk_statement,
                    document_id: quote.document_id,
                    page: quote.page,
                    chunk_id: quote.chunk_id,
                    quote: quote.quote,
                    requirement_references: risk.requirement_references,
                    verifier_status: risk.verifier_status
                  }))].map((row, index) => (
                    <blockquote key={`${row.document_id}-${row.chunk_id}-${index}`} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p className="text-sm leading-6 text-slate-800">"{row.quote}"</p>
                      <footer className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
                        <span>Document: {row.document_id}</span>
                        <span>Page: {row.page}</span>
                        <span>Chunk: {row.chunk_id}</span>
                      </footer>
                    </blockquote>
                  ))}
                </div>
              )}
            </ReviewPanel>
          </div>

          <div className="space-y-5">
            <ReviewPanel title="Model Positions">
              <PositionList label="Found by" values={modelPosition?.found_by_agents ?? risk.found_by_agents} />
              <PositionList label="Contradicted by" values={modelPosition?.contradicted_by_agents ?? risk.contradicted_by_agents} />
              <PositionList label="No issue agents" values={modelPosition?.no_issue_agents ?? risk.no_issue_agents} />
            </ReviewPanel>

            <ReviewPanel title="Review Decision Form">
              <ReviewDecisionForm findingId={findingId} />
            </ReviewPanel>
          </div>
        </div>
      </ReviewShell>
    );
  } catch (error) {
    return (
      <ReviewShell>
        <EmptyState message={`Finding konnte nicht geladen werden: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`} />
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

function PositionList({ label, values }: { label: string; values: string[] }) {
  return (
    <div className="mb-4">
      <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</h3>
      {values.length === 0 ? (
        <p className="mt-1 text-sm text-slate-500">Keine Einträge.</p>
      ) : (
        <div className="mt-2 flex flex-wrap gap-2">
          {values.map((value) => (
            <StatusBadge key={value}>{value}</StatusBadge>
          ))}
        </div>
      )}
    </div>
  );
}
