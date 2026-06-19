import Link from "next/link";
import { notFound } from "next/navigation";
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  ClipboardCheck,
  FileText,
  HelpCircle,
  SearchCheck,
  type LucideIcon,
} from "lucide-react";
import { ReviewPanel, ReviewShell, StatusBadge } from "@/src/components/review-ui/review-shell";
import { findDemoReviewCase, type DemoReviewCase } from "@/src/lib/review-ui";

const decisionReadinessItems = ["Quelle sichtbar", "Lücke benannt", "QA-Schritt klar"] as const;

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
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
          <div className="border-l-4 border-[var(--brand)] pl-5">
            <div className="flex flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-300">
              <span className="font-mono">{demoCase.id}</span>
              <span>{demoCase.area}</span>
              <span>{demoCase.regulation}</span>
            </div>
            <h2 className="mt-4 max-w-4xl text-[34px] font-semibold leading-[1.05] text-[var(--text-primary)] md:text-[46px]">
              {demoCase.title}
            </h2>
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <InsightCard label="Kurzantwort">{whyItMatters}</InsightCard>
              <InsightCard label="Zielzustand">
                QA kann bestätigen, Unterlagen nachfordern oder eskalieren.
              </InsightCard>
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

          <DecisionDesk demoCase={demoCase} />
        </div>
      </ReviewPanel>

      <div className="grid gap-5 lg:grid-cols-[0.72fr_0.28fr]">
        <ReviewPanel title="Was ist der Fall?">
          <p className="text-sm leading-7 text-[var(--text-secondary)]">
            {demoCase.summary}
          </p>
          <div className="mt-4 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3 text-sm leading-6 text-[var(--text-secondary)]">
            <span className="font-semibold text-[var(--text-primary)]">Prüfhinweis:</span>{" "}
            {demoCase.criticNote}
          </div>
        </ReviewPanel>

        <ReviewPanel title="Entscheidungsreife">
          <DecisionReadiness />
        </ReviewPanel>
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        <DossierListPanel title="Prüfpunkte" items={demoCase.findings} icon={SearchCheck} />
        <DossierListPanel title="Quellen & Nachweise" items={demoCase.evidence} icon={FileText} />
        <DossierListPanel
          title="Was fehlt?"
          items={demoCase.missingEvidence}
          icon={AlertCircle}
          tone="warning"
        />
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

      <ReviewPanel
        title="Echte Prüffälle"
        action={
          <Link
            href="/prueffaelle"
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

function DecisionDesk({ demoCase }: { demoCase: DemoReviewCase }) {
  return (
    <aside className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)]">
      <div className="border-b border-[var(--border-default)] px-4 py-3">
        <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
          Decision Desk
        </div>
        <div className="mt-1 text-[14px] font-medium text-[var(--text-primary)]">
          QA muss entscheiden
        </div>
      </div>
      <div className="divide-y divide-[var(--border-muted)] px-4">
        {demoCase.decisionActions.map((action, index) => (
          <button
            key={action}
            type="button"
            className={`flex w-full items-center justify-between gap-3 py-3 text-left text-[13px] font-medium ${
              index === 0 ? "text-[var(--brand)]" : "text-[var(--text-secondary)]"
            }`}
          >
            <span>{action}</span>
            <span className={`h-2 w-2 rounded-full ${index === 0 ? "bg-[var(--brand)]" : "bg-[var(--border-strong)]"}`} />
          </button>
        ))}
      </div>
      <div className="border-t border-[var(--border-default)] px-4 py-3 text-[12px] leading-5 text-[var(--text-secondary)]">
        Entscheidung erst speichern, wenn Quelle, Lücke und Begründung zusammenpassen.
      </div>
    </aside>
  );
}

function InsightCard({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-4 py-3 text-sm leading-7 text-[var(--text-secondary)]">
      <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
        {label}
      </div>
      <p className="mt-1 font-medium text-[var(--text-primary)]">{children}</p>
    </div>
  );
}

function DossierListPanel({
  title,
  items,
  icon: Icon,
  tone = "default",
}: {
  title: string;
  items: readonly string[];
  icon: LucideIcon;
  tone?: "default" | "warning";
}) {
  const iconClassName =
    tone === "warning" ? "text-amber-600 dark:text-amber-300" : "text-[var(--brand)]";

  return (
    <ReviewPanel title={title}>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
            <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${iconClassName}`} aria-hidden />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </ReviewPanel>
  );
}

function DecisionReadiness() {
  return (
    <div className="space-y-3">
      {decisionReadinessItems.map((item) => (
        <div key={item} className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
          <CheckCircle2 className="h-4 w-4 text-[var(--brand)]" aria-hidden />
          {item}
        </div>
      ))}
    </div>
  );
}
