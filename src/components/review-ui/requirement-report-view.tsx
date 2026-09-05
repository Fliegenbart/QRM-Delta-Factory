import Link from "next/link";
import type { ReactNode } from "react";
import { ReviewPanel, StatusBadge } from "@/src/components/review-ui/review-shell";
import { RequirementReportExportActions } from "@/src/components/review-ui/requirement-report-export-actions";
import { RetryFailedRequirements } from "@/src/components/review-ui/retry-failed-requirements";
import {
  REQUIREMENT_STATUS_LABELS,
  REQUIREMENT_STATUS_ORDER,
  deterministicCheckSummary,
  evidenceLocationLabel,
  requirementConfidenceNotes,
  requirementCoverageProgress,
  type RequirementCoverageReport,
  type RequirementVerdictRow,
  type RequirementVerdictStatus
} from "@/src/lib/review-ui";

const STATUS_TONE: Record<RequirementVerdictStatus, "red" | "amber" | "green" | "slate"> = {
  violated: "red",
  unclear: "amber",
  fulfilled: "green",
  not_applicable: "slate"
};

/**
 * What each bucket means in a reviewer's own terms, stated once at the top of
 * its group. Without this the four statuses read as machine labels; with it
 * the page reads as the reviewer's own process.
 */
const STATUS_INTENT: Record<RequirementVerdictStatus, string> = {
  violated: "Die Unterlagen belegen einen Verstoß oder eine belegte Lücke. Hier ist eine Entscheidung fällig.",
  unclear:
    "Die Unterlagen reichen für kein Urteil. Diese Anforderungen brauchen Ihren Blick — das System hat sich bewusst nicht festgelegt.",
  fulfilled: "Die Erfüllung ist belegt. Der Nachweis steht jeweils darunter.",
  not_applicable:
    "Außerhalb des Geltungsbereichs dieses Vorgangs. Ohne Modellaufruf vom Server bestimmt."
};

/**
 * The requirement coverage report as the reviewer reads it: what the report
 * answers, what the deterministic layer did, then one row per obligation
 * grouped by verdict. Rendered identically for a live case and for the
 * example cases, so what a prospect sees in the demo is what the tool
 * produces -- not a mock-up of it.
 */
export function RequirementReportView({
  report,
  reviewPackHref,
  exportable = true,
  retryDocumentSetId,
  intro
}: {
  report: RequirementCoverageReport;
  reviewPackHref?: string;
  exportable?: boolean;
  /** Live case: enables re-judging rows a failed model call left behind. */
  retryDocumentSetId?: string;
  intro?: ReactNode;
}) {
  const progress = requirementCoverageProgress(report);
  const checks = deterministicCheckSummary(report);
  const retryable = report.verdicts.filter((row) => row.needs_retry).length;
  const grouped = REQUIREMENT_STATUS_ORDER.map((status) => ({
    status,
    rows: report.verdicts.filter((row) => row.published_status === status)
  })).filter((group) => group.rows.length > 0);

  return (
    <div className="space-y-5">
      <ReviewPanel
        title="Anforderungsabdeckung"
        action={
          <div className="flex flex-wrap items-center justify-end gap-2">
            {exportable ? <RequirementReportExportActions report={report} /> : null}
            <StatusBadge tone={progress.needsAttention > 0 ? "amber" : "green"}>
              {progress.needsAttention > 0 ? `${progress.needsAttention} offen` : "Nichts offen"}
            </StatusBadge>
          </div>
        }
      >
        {intro}
        <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
          <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3">
            <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
              Was dieser Bericht beantwortet
            </div>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
              Jede Anforderung des hinterlegten Regelwerks wird genau einmal
              beantwortet — erfüllt, verletzt, unklar oder nicht anwendbar.
              Die Vollständigkeit ist damit nicht behauptet, sondern die
              Struktur des Berichts selbst. Jede Zeile nennt ihre Quelle im
              Regelwerk und trägt entweder ihren geprüften Beleg oder die
              Lücke, die offen bleibt.
            </p>
          </div>
          <dl className="grid gap-3 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3 text-sm">
            <div className="flex items-baseline justify-between gap-3">
              <dt className="text-[var(--text-tertiary)]">Anforderungen</dt>
              <dd className="font-medium text-[var(--text-primary)]">{progress.total}</dd>
            </div>
            <div className="flex items-baseline justify-between gap-3">
              <dt className="text-[var(--text-tertiary)]">Ihr Blick nötig</dt>
              <dd className="font-medium text-[var(--text-primary)]">{progress.needsAttention}</dd>
            </div>
            <div className="flex items-baseline justify-between gap-3">
              <dt className="text-[var(--text-tertiary)]">Ohne Befund</dt>
              <dd className="font-medium text-[var(--text-primary)]">{progress.answered}</dd>
            </div>
            {report.failed_model_call_count > 0 ? (
              <div className="flex items-baseline justify-between gap-3">
                <dt className="text-[var(--text-tertiary)]">Fehlgeschlagene Prüfschritte</dt>
                <dd className="font-medium text-[var(--severity-major)]">
                  {report.failed_model_call_count}
                </dd>
              </div>
            ) : null}
          </dl>
        </div>
        {checks ? (
          <div className="mt-4 rounded-md border border-[var(--border-default)] px-4 py-3">
            <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
              Deterministisch geprüft
            </div>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
              Das Modell liest; Regeln entscheiden, was Regeln entscheiden können — ein Wert
              gegen seine Grenze, ein Schritt vor dem Ereignis, das er betrifft, eine CAPA
              ohne Wirksamkeitsprüfung. Aus den Unterlagen wurden{" "}
              {checks.rows.length === 0
                ? "keine typisierten Einträge"
                : checks.rows.map((row) => `${row.count} ${row.label}`).join(", ")}{" "}
              extrahiert und wortwörtlich gegen den Quelltext geerdet
              {checks.dropped > 0 ? ` (${checks.dropped} nicht belegbare Einträge verworfen)` : ""}
              . Daraus folgten{" "}
              <strong className="font-semibold text-[var(--text-primary)]">
                {checks.findings === 1 ? "1 Regelbefund" : `${checks.findings} Regelbefunde`}
              </strong>
              ; jeder davon steht unten an seiner Anforderung, mit Beleg.
            </p>
          </div>
        ) : null}
        {retryDocumentSetId && retryable > 0 ? (
          <RetryFailedRequirements documentSetId={retryDocumentSetId} retryable={retryable} />
        ) : null}
        {reviewPackHref ? (
          <p className="mt-3 text-xs leading-5 text-[var(--text-tertiary)]">
            <Link href={reviewPackHref} className="underline underline-offset-2">
              Zur klassischen Prüfmappe
            </Link>{" "}
            — dieselben Unterlagen, nach Befunden statt nach Anforderungen geordnet.
          </p>
        ) : null}
      </ReviewPanel>

      {grouped.map((group) => (
        <ReviewPanel
          key={group.status}
          title={`${REQUIREMENT_STATUS_LABELS[group.status]} (${group.rows.length})`}
          action={
            <StatusBadge tone={STATUS_TONE[group.status]}>
              {REQUIREMENT_STATUS_LABELS[group.status]}
            </StatusBadge>
          }
        >
          <p className="mb-4 text-sm leading-6 text-[var(--text-secondary)]">
            {STATUS_INTENT[group.status]}
          </p>
          <div className="space-y-4">
            {group.rows.map((row) => (
              <RequirementRow key={row.requirement_id} row={row} />
            ))}
          </div>
        </ReviewPanel>
      ))}
    </div>
  );
}

function RequirementRow({ row }: { row: RequirementVerdictRow }) {
  const notes = requirementConfidenceNotes(row);
  const isSettled =
    row.published_status === "fulfilled" || row.published_status === "not_applicable";

  return (
    <article className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3">
      <header className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
        <h3 className="text-sm font-medium text-[var(--text-primary)]">
          {row.requirement_title ?? row.requirement_id}
        </h3>
        <span className="text-[11px] uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
          {row.source_name} · Abschnitt {row.section}
        </span>
      </header>
      <p className="mt-1 text-xs leading-5 text-[var(--text-tertiary)]">{row.requirement_text}</p>
      <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">{row.rationale}</p>
      {row.needs_retry ? (
        <p className="mt-2 text-xs leading-5 text-amber-800">
          Modellaufruf fehlgeschlagen — diese Zeile ist ein Platzhalter, kein Urteil, und kann
          allein erneut geprüft werden.
        </p>
      ) : null}

      {row.evidence.length > 0 ? (
        <div className="mt-3 space-y-2">
          {row.evidence.map((item, index) => (
            <blockquote
              key={`${item.chunk_id}-${index}`}
              className="border-l-2 border-[var(--border-strong)] pl-3 text-xs leading-5 text-[var(--text-secondary)]"
            >
              <span className="block font-mono">„{item.quote}"</span>
              <cite className="mt-1 block not-italic text-[var(--text-tertiary)]">
                {evidenceLocationLabel(item)}
              </cite>
            </blockquote>
          ))}
        </div>
      ) : !isSettled ? (
        <p className="mt-3 text-xs leading-5 text-[var(--text-tertiary)]">
          Kein prüfbares Zitat verblieben — deshalb steht hier kein abschließendes Urteil.
        </p>
      ) : null}

      {notes.length > 0 ? (
        <ul className="mt-3 space-y-1 text-xs leading-5 text-[var(--text-tertiary)]">
          {notes.map((note) => (
            <li key={note}>· {note}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}
