import Link from "next/link";
import { notFound } from "next/navigation";
import { AlertCircle, ArrowLeft, CheckCircle2, ClipboardCheck, FileText, HelpCircle, SearchCheck } from "lucide-react";
import { ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import { findDemoReviewCase } from "@/src/lib/review-ui";

export function generateStaticParams() {
  return [
    { id: "dev-2025-014" },
    { id: "capa-2025-082" },
    { id: "cc-2025-211" }
  ];
}

export default async function DemoReviewCasePage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const demoCase = findDemoReviewCase(id);

  if (!demoCase) {
    notFound();
  }
  const whyItMatters = demoCase.whyItMatters.replace("Warum dieser Fall wichtig ist: ", "");

  return (
    <ReviewShell>
      <div className="mb-4">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm font-medium text-[var(--brand)] hover:text-[var(--brand-strong)]"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden />
          Zurück zur Startseite
        </Link>
      </div>

      <ReviewPanel
        title="Beispiel-Prüfmappe"
        action={<StatusBadge tone={demoCase.severity === "ready" ? "green" : demoCase.severity === "major" ? "amber" : "red"}>{demoCase.severityLabel}</StatusBadge>}
      >
        <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
          <div>
            <div className="flex flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-300">
              <span className="font-mono">{demoCase.id}</span>
              <span>{demoCase.area}</span>
              <span>{demoCase.regulation}</span>
            </div>
            <h2 className="mt-3 max-w-3xl text-2xl font-semibold leading-tight text-slate-950 dark:text-white">
              {demoCase.title}
            </h2>
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3 text-sm leading-7 text-[var(--text-secondary)]">
                <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
                  Kurzantwort
                </div>
                <p className="mt-1 font-medium text-[var(--text-primary)]">{whyItMatters}</p>
              </div>
              <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3 text-sm leading-7 text-[var(--text-secondary)]">
                <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
                  Zielzustand
                </div>
                <p className="mt-1 font-medium text-[var(--text-primary)]">
                  QA kann bestätigen, Unterlagen nachfordern oder eskalieren.
                </p>
              </div>
            </div>
            <div className="mt-4 rounded-md border border-[var(--brand)] bg-[var(--brand-soft)] px-4 py-3 text-sm leading-6 text-[var(--text-primary)]">
              <div className="flex items-start gap-3">
                <ClipboardCheck className="mt-0.5 h-4 w-4 shrink-0 text-[var(--brand)]" aria-hidden />
                <div>
                  <div className="font-semibold">Nächster Schritt</div>
                  <p className="mt-1">{demoCase.nextStep}</p>
                </div>
              </div>
            </div>
          </div>

          <aside className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] p-4 text-sm">
            <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
              Was ist der Fall?
            </div>
            <p className="mt-2 leading-6 text-[var(--text-secondary)]">
              {demoCase.summary}
            </p>
            <div className="mt-4 text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
              Prüfhinweis
            </div>
            <p className="mt-2 leading-6 text-[var(--text-secondary)]">
              {demoCase.criticNote}
            </p>
          </aside>
        </div>
      </ReviewPanel>

      <div className="grid gap-5 xl:grid-cols-3">
        <ReviewPanel title="Prüfpunkte">
          <ul className="space-y-2">
            {demoCase.findings.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                <SearchCheck className="mt-0.5 h-4 w-4 shrink-0 text-[var(--brand)]" aria-hidden />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </ReviewPanel>

        <ReviewPanel title="Quellen & Nachweise">
          <ul className="space-y-2">
            {demoCase.evidence.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                <FileText className="mt-0.5 h-4 w-4 shrink-0 text-[var(--brand)]" aria-hidden />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </ReviewPanel>

        <ReviewPanel title="Was fehlt?">
          <ul className="space-y-2">
            {demoCase.missingEvidence.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600 dark:text-amber-300" aria-hidden />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </ReviewPanel>
      </div>

      <ReviewPanel title="Offene QA-Fragen">
        <ul className="grid gap-2 md:grid-cols-3">
          {demoCase.openQuestions.map((item) => (
            <li key={item} className="flex items-start gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] p-3 text-sm text-[var(--text-secondary)]">
              <HelpCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600 dark:text-amber-300" aria-hidden />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </ReviewPanel>

      <ReviewPanel title="Was muss QA entscheiden?">
        <div className="grid gap-3 md:grid-cols-3">
          {demoCase.decisionActions.map((action, index) => (
            <button
              key={action}
              type="button"
              className={`h-10 rounded-md border px-3 text-sm font-semibold ${
                index === 0
                  ? "border-[var(--brand)] bg-[var(--brand)] text-white"
                  : "border-[var(--border-default)] bg-[var(--surface-primary)] text-[var(--text-primary)] hover:bg-[var(--surface-secondary)]"
              }`}
            >
              {action}
            </button>
          ))}
        </div>
        <p className="mt-4 text-sm leading-7 text-[var(--text-secondary)]">
          Diese Demo zeigt den Zielzustand der Prüfmappe. In echten Fällen wird die Entscheidung mit kurzer Begründung gespeichert.
        </p>
      </ReviewPanel>

      <ReviewPanel
        title="Echte Prüffälle"
        action={
          <Link
            href="/review-ui"
            className="inline-flex h-9 items-center gap-2 rounded-md bg-[var(--brand)] px-3 text-sm font-semibold text-white hover:bg-[var(--brand-strong)]"
          >
            <CheckCircle2 className="h-4 w-4" aria-hidden />
            Prüffälle öffnen
          </Link>
        }
      >
        <p className="text-sm leading-7 text-[var(--text-secondary)]">
          Echte Fälle erscheinen hier, sobald das Backend verbunden ist und ein Prüffall angelegt wurde.
        </p>
      </ReviewPanel>
    </ReviewShell>
  );
}
