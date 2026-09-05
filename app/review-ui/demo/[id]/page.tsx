import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, FileText, FlaskConical } from "lucide-react";
import { ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import { RequirementReportView } from "@/src/components/review-ui/requirement-report-view";
import {
  demoCaseProvenance,
  demoCaseScoreline,
  demoCases,
  findDemoCase
} from "@/src/lib/demo-cases";
import { displayReviewValue } from "@/src/lib/review-ui";

export function generateStaticParams() {
  return demoCases.map((demoCase) => ({ id: demoCase.slug }));
}

export default async function DemoReviewCasePage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const demoCase = findDemoCase(id);

  if (!demoCase) {
    notFound();
  }

  const violated = demoCase.report.status_counts.violated ?? 0;

  return (
    <ReviewShell>
      <div className="mb-4">
        <Link
          href="/review-ui"
          className="inline-flex items-center gap-2 text-sm font-medium text-[var(--brand)] hover:text-[var(--brand-strong)]"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden />
          Zurück zu den Prüffällen
        </Link>
      </div>

      <ReviewPanel
        title="Beispiel-Prüfmappe"
        action={
          <StatusBadge tone={violated > 0 ? "red" : "green"}>
            {violated > 0 ? `${violated} verletzt` : "Keine Verletzung"}
          </StatusBadge>
        }
      >
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
          <div className="border-l-4 border-[var(--brand)] pl-5">
            <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-[var(--text-tertiary)]">
              <span className="font-mono">{demoCase.id.toUpperCase()}</span>
              <span>{demoCase.trigger}</span>
              <span>{demoCase.area}</span>
            </div>
            <h2 className="mt-3 max-w-4xl text-[28px] font-semibold leading-[1.1] text-[var(--text-primary)] md:text-[36px]">
              {demoCase.title}
            </h2>
            <dl className="mt-4 grid gap-x-6 gap-y-2 text-sm sm:grid-cols-3">
              <div>
                <dt className="text-[11px] uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Produkt</dt>
                <dd className="mt-0.5 text-[var(--text-primary)]">
                  {demoCase.product}
                  {demoCase.dosage_form ? `, ${demoCase.dosage_form}` : ""}
                </dd>
              </div>
              <div>
                <dt className="text-[11px] uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Charge</dt>
                <dd className="mt-0.5 font-mono text-[var(--text-primary)]">{demoCase.batch}</dd>
              </div>
              <div>
                <dt className="text-[11px] uppercase tracking-[0.12em] text-[var(--text-tertiary)]">Ergebnis</dt>
                <dd className="mt-0.5 text-[var(--text-primary)]">{demoCaseScoreline(demoCase)}</dd>
              </div>
            </dl>
            <div className="mt-4 flex items-start gap-3 rounded-md border border-[var(--brand)] bg-[var(--brand-soft)] px-4 py-3 text-sm leading-6 text-[var(--text-primary)]">
              <FlaskConical className="mt-0.5 h-4 w-4 shrink-0 text-[var(--brand)]" aria-hidden />
              <div>
                <div className="font-semibold">So ist dieses Beispiel entstanden</div>
                <p className="mt-1">{demoCaseProvenance(demoCase)}</p>
              </div>
            </div>
          </div>

          <aside className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)]">
            <div className="border-b border-[var(--border-default)] px-4 py-3">
              <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
                Geprüfte Unterlagen
              </div>
            </div>
            <ul className="divide-y divide-[var(--border-muted)] px-4">
              {demoCase.documents.map((document) => (
                <li key={document.file_name} className="flex items-start gap-2 py-2.5 text-[13px]">
                  <FileText className="mt-0.5 h-4 w-4 shrink-0 text-[var(--brand)]" aria-hidden />
                  <div className="min-w-0">
                    <div className="font-medium text-[var(--text-primary)]">{document.label}</div>
                    <div className="truncate font-mono text-[11px] text-[var(--text-tertiary)]">
                      {document.file_name}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
            <div className="border-t border-[var(--border-default)] px-4 py-3 text-[12px] leading-5 text-[var(--text-secondary)]">
              Status des Laufs:{" "}
              <span className="font-medium text-[var(--text-primary)]">
                {displayReviewValue(demoCase.run.pipeline_status ?? "")}
              </span>
              . Engine {demoCase.report.engine_version}.
            </div>
          </aside>
        </div>
      </ReviewPanel>

      <RequirementReportView report={demoCase.report} exportable={false} />

      <ReviewPanel
        title="Eigene Unterlagen prüfen"
        action={
          <Link
            href="/review-ui#new-case"
            className="inline-flex h-9 items-center gap-2 rounded-md bg-[var(--brand)] px-3 text-sm font-semibold text-white hover:bg-[var(--brand-strong)]"
          >
            Neuen Prüffall anlegen
          </Link>
        }
      >
        <p className="text-sm leading-7 text-[var(--text-secondary)]">
          Dieselbe Prüfkette, dieselbe Darstellung — mit Ihren Unterlagen und Ihrem
          Regelwerk. Der Bericht eines echten Prüffalls lässt sich zusätzlich als PDF
          und Excel exportieren und trägt die dokumentierte QA-Entscheidung.
        </p>
      </ReviewPanel>
    </ReviewShell>
  );
}
