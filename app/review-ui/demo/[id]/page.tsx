import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, CheckCircle2, ClipboardCheck, FileText, HelpCircle } from "lucide-react";
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
        title={demoCase.title}
        action={<StatusBadge tone={demoCase.severity === "ready" ? "green" : demoCase.severity === "major" ? "amber" : "red"}>{demoCase.severityLabel}</StatusBadge>}
      >
        <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
          <div>
            <div className="flex flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-300">
              <span className="font-mono">{demoCase.id}</span>
              <span>{demoCase.area}</span>
              <span>{demoCase.regulation}</span>
            </div>
            <p className="mt-4 text-sm leading-7 text-slate-700 dark:text-slate-200">
              {demoCase.summary}
            </p>
            <div className="mt-5 rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm leading-6 text-emerald-900 dark:border-emerald-400/25 dark:bg-emerald-950/25 dark:text-emerald-100">
              <div className="flex items-start gap-3">
                <ClipboardCheck className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
                <div>
                  <div className="font-semibold">Nächster Schritt</div>
                  <p className="mt-1">{demoCase.nextStep}</p>
                </div>
              </div>
            </div>
          </div>

          <aside className="rounded-md border border-slate-200 bg-slate-50 p-4 text-sm dark:border-white/10 dark:bg-slate-900/50">
            <div className="font-semibold text-slate-950 dark:text-white">Prüfhinweis</div>
            <p className="mt-2 leading-6 text-slate-600 dark:text-slate-300">
              {demoCase.criticNote}
            </p>
          </aside>
        </div>
      </ReviewPanel>

      <div className="grid gap-5 lg:grid-cols-2">
        <ReviewPanel title="Sichtbare Quellen">
          <ul className="space-y-2">
            {demoCase.evidence.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-200">
                <FileText className="mt-0.5 h-4 w-4 shrink-0 text-[var(--brand)]" aria-hidden />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </ReviewPanel>

        <ReviewPanel title="Offene Fragen">
          <ul className="space-y-2">
            {demoCase.openQuestions.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-200">
                <HelpCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600 dark:text-amber-300" aria-hidden />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </ReviewPanel>
      </div>

      <ReviewPanel
        title="Entscheidung"
        action={
          <Link
            href="/review-ui"
            className="inline-flex h-9 items-center gap-2 rounded-md bg-slate-950 px-3 text-sm font-semibold text-white hover:bg-slate-800 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200"
          >
            <CheckCircle2 className="h-4 w-4" aria-hidden />
            Echte Fallliste öffnen
          </Link>
        }
      >
        <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">
          Diese Demo zeigt den gewünschten Arbeitsfluss. In echten Fällen wird hier die Entscheidung
          mit Begründung gespeichert.
        </p>
      </ReviewPanel>
    </ReviewShell>
  );
}
