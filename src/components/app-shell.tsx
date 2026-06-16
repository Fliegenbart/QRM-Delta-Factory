"use client";

import Link from "next/link";
import { useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  Brain,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  ClipboardCheck,
  Compass,
  Crosshair,
  FileCheck2,
  FileText,
  Gauge,
  Globe,
  Library,
  Menu,
  Moon,
  Plus,
  SearchCheck,
  ShieldCheck,
  Sun,
  X,
} from "lucide-react";
import { useI18n, type TranslationKey } from "@/src/lib/i18n";
import { useTheme } from "@/src/lib/theme";
import { motion } from "@/src/components/ui/motion";
import { IntakeUploader } from "@/src/components/review-ui/intake-uploader";
import { RequirementLibraryManager } from "@/src/components/review-ui/requirement-library-manager";
import { HumanFeedbackRegistryPanel } from "@/src/components/review-ui/human-feedback-registry-panel";
import { RingversuchDashboard } from "@/src/components/review-ui/ringversuch-dashboard";
import { OverviewLanding } from "@/src/components/review-ui/overview-landing";
import { SalesReadinessPanel } from "@/src/components/review-ui/sales-readiness-panel";
import { aiArchitectureConcept, demoReviewCases, productHomeCopy } from "@/src/lib/review-ui";
import { CaseCard } from "@/src/components/triage/case-card";
import type { LucideIcon } from "lucide-react";

type NavItem = [slug: string, labelKey: TranslationKey, icon: LucideIcon];
type NavCategory = { nameKey: TranslationKey; items: NavItem[] };

const navCategories: NavCategory[] = [
  {
    nameKey: "nav.category.workspace",
    items: [
      ["ueberblick", "nav.ueberblick", Compass],
      ["dashboard", "nav.dashboard", Gauge],
      ["review-ui", "nav.backendReview", ShieldCheck],
      ["ringversuch", "nav.ringversuch", Crosshair],
    ],
  },
  {
    nameKey: "nav.category.admin",
    items: [["risk-library", "nav.riskLibrary", Library]],
  },
  {
    nameKey: "nav.category.commercial",
    items: [["kundenpilot", "nav.customerPilot", ClipboardCheck]],
  },
  {
    nameKey: "nav.category.howItWorks",
    items: [["ai-architecture", "nav.aiArchitecture", Brain]],
  },
];

const navItems = navCategories.flatMap((category) => category.items);

export const sectionSlugs = navItems.map(([slug]) => slug);

const pageTitleKeys = Object.fromEntries(
  navItems.map(([slug, labelKey]) => [slug, labelKey])
) as Record<string, TranslationKey>;

const homeDecisionActions = ["Bestätigen", "Nachfordern", "Eskalieren"] as const;

function pageTitle(slug: string, t: (key: TranslationKey) => string) {
  if (slug === "dashboard") return "QA-Prüfung vorbereiten";
  return t(pageTitleKeys[slug] ?? "nav.dashboard");
}

export function AppShell({ section }: { section: string; projectId?: string }) {
  const active = sectionSlugs.includes(section) ? section : "dashboard";
  return <AppFrame section={active}>{renderSection(active)}</AppFrame>;
}

export function AppFrame({
  section,
  children,
}: {
  section: string;
  children: React.ReactNode;
}) {
  const active = sectionSlugs.includes(section) ? section : "dashboard";
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(navCategories.map((category) => [category.nameKey, true]))
  );
  const { locale, setLocale, t } = useI18n();
  const { resolvedTheme, setTheme } = useTheme();

  function toggleCategory(categoryName: string) {
    setExpandedCategories((current) => ({
      ...current,
      [categoryName]: !current[categoryName],
    }));
  }

  const navigation = (
    <>
      {navCategories.map((category) => (
        <div key={category.nameKey} className="mb-3">
          <button
            type="button"
            onClick={() => toggleCategory(category.nameKey)}
            className="flex w-full items-center justify-between px-2 py-1.5 text-[10px] font-medium uppercase tracking-[0.16em] text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]"
            aria-expanded={expandedCategories[category.nameKey]}
          >
            <span>{t(category.nameKey)}</span>
            {expandedCategories[category.nameKey] ? (
              <ChevronDown className="h-3 w-3" aria-hidden />
            ) : (
              <ChevronRight className="h-3 w-3" aria-hidden />
            )}
          </button>
          {expandedCategories[category.nameKey] ? (
            <div className="mt-1 space-y-0.5">
              {category.items.map(([slug, labelKey, Icon]) => {
                const isActive = active === slug;
                return (
                  <Link
                    key={slug}
                    href={slug === "dashboard" ? "/" : `/${slug}`}
                    onClick={() => setMobileNavOpen(false)}
                    aria-current={isActive ? "page" : undefined}
                    className={`flex items-center gap-2.5 rounded-md px-2 py-1.5 text-[13px] transition-colors ${
                      isActive
                        ? "bg-[var(--brand-soft)] text-[var(--brand-strong)] font-medium"
                        : "text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)]"
                    }`}
                  >
                    <Icon className="h-4 w-4 shrink-0" aria-hidden />
                    <span className="truncate">{t(labelKey)}</span>
                  </Link>
                );
              })}
            </div>
          ) : null}
        </div>
      ))}
    </>
  );

  return (
    <div className="min-h-screen text-[var(--text-primary)]">
      {mobileNavOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={() => setMobileNavOpen(false)}
          aria-label="Close navigation"
        />
      ) : null}

      <aside
        className={`fixed inset-y-0 left-0 z-50 w-[240px] transform border-r border-[var(--border-default)] bg-[var(--surface-secondary)] transition-transform duration-200 lg:hidden ${
          mobileNavOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Mobile navigation"
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-[var(--border-default)] px-4 py-4">
            <BrandMark />
            <button
              type="button"
              onClick={() => setMobileNavOpen(false)}
              className="grid h-9 w-9 place-items-center rounded-md text-[var(--text-secondary)] hover:bg-[var(--surface-primary)]"
              aria-label="Close navigation"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Main navigation">
            {navigation}
          </nav>
        </div>
      </aside>

      <aside className="fixed inset-y-0 left-0 hidden w-[240px] flex-col border-r border-[var(--border-default)] bg-[var(--surface-secondary)] lg:flex">
        <div className="border-b border-[var(--border-default)] px-4 py-5">
          <BrandMark />
          <div className="mt-3 text-[11px] leading-5 text-[var(--text-tertiary)]">
            {t("brand.tagline")}
          </div>
        </div>
        <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Main navigation">
          {navigation}
        </nav>
        <div className="border-t border-[var(--border-default)] px-4 py-3 text-[11px] text-[var(--text-tertiary)]">
          <div className="mono">ICH Q9 R1 · v2026.1</div>
          <div className="mt-0.5">Reviewer: David</div>
        </div>
      </aside>

      <main id="main-content" className="lg:pl-[240px]">
        <header className="sticky top-0 z-10 border-b border-[var(--border-default)] bg-[var(--background)] px-4 py-3 lg:px-8">
          <div className="mx-auto flex max-w-[1280px] items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setMobileNavOpen(true)}
                className="grid h-9 w-9 place-items-center rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] text-[var(--text-secondary)] lg:hidden"
                aria-label="Open navigation menu"
              >
                <Menu className="h-4 w-4" />
              </button>
              <div>
                <div className="text-[11px] uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
                  Pharma QRM
                </div>
                <h1 className="mt-0.5 text-[20px] font-medium leading-tight text-[var(--text-primary)]">
                  {pageTitle(active, t)}
                </h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setLocale(locale === "de" ? "en" : "de")}
                className="hidden h-9 items-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-[12px] text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] sm:inline-flex"
                aria-label={locale === "de" ? "Switch to English" : "Auf Deutsch wechseln"}
              >
                <Globe className="h-3.5 w-3.5" />
                <span className="font-medium">{locale.toUpperCase()}</span>
              </button>
              <button
                type="button"
                onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
                className="hidden h-9 w-9 place-items-center rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] sm:grid"
                aria-label={resolvedTheme === "dark" ? t("theme.light") : t("theme.dark")}
              >
                {resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-[1280px] px-4 py-7 lg:px-8">{children}</div>
      </main>
    </div>
  );
}

function BrandMark() {
  return (
    <div className="flex items-center gap-2.5">
      <div
        className="grid h-7 w-7 place-items-center rounded-md bg-[var(--brand)] text-[12px] font-medium text-white"
        aria-hidden
      >
        Q
      </div>
      <div className="leading-tight">
        <div className="text-[12px] font-medium tracking-[0.04em] text-[var(--text-primary)]">
          Pharma QRM
        </div>
        <div className="text-[11px] text-[var(--text-tertiary)]">Prüfmappe vorbereiten</div>
      </div>
    </div>
  );
}

function renderSection(section: string) {
  switch (section) {
    case "review-ui":
      return <ReviewEntrySection />;
    case "ai-architecture":
      return <AiArchitectureSection />;
    case "risk-library":
      return <RequirementLibraryManager />;
    case "ringversuch":
      return <RingversuchDashboard />;
    case "ueberblick":
      return <OverviewLanding />;
    case "kundenpilot":
      return <SalesReadinessPanel />;
    default:
      return <DashboardSection />;
  }
}

/* ----- Triage dashboard ----- */

function DashboardSection() {
  return (
    <div className="space-y-10">
      <ProductHero />
      <OutcomeChecklist />

      <section id="new-case">
        <SectionIntro
          title={productHomeCopy.primaryAction}
          description="Change, CAPA, Abweichung oder Audit hochladen. Die Originaldateien bleiben die Quelle."
          meta="KI bereitet vor. QA entscheidet."
        />
        <IntakeUploader />
      </section>

      <section>
        <SectionIntro
          title={productHomeCopy.exampleTitle}
          description={productHomeCopy.exampleDescription}
          meta={
            <div className="hidden gap-4 text-[11px] text-[var(--text-tertiary)] sm:flex">
              <span>3 Beispiele</span>
              <span className="mono">{new Date().toLocaleDateString("de-DE")}</span>
            </div>
          }
        />

        <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-4">
          {demoReviewCases.map((c) => (
            <CaseCard key={c.id} data={c} />
          ))}
        </div>
      </section>
    </div>
  );
}

function SectionIntro({
  title,
  description,
  meta,
}: {
  title: string;
  description: string;
  meta?: React.ReactNode;
}) {
  return (
    <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h2 className="text-[18px] font-medium text-[var(--text-primary)]">{title}</h2>
        <p className="mt-1 max-w-2xl text-[13px] leading-6 text-[var(--text-secondary)]">
          {description}
        </p>
      </div>
      {meta ? <div className="text-[12px] text-[var(--text-tertiary)]">{meta}</div> : null}
    </div>
  );
}

function ProductHero() {
  return (
    <section className="relative overflow-hidden border-b border-[var(--border-default)] pb-10">
      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_430px] lg:items-stretch">
        <div className="flex min-h-[520px] flex-col justify-between border-l-4 border-[var(--brand)] pl-5 md:pl-7">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 py-1 text-[11px] font-medium text-[var(--text-secondary)]">
              <FileCheck2 className="h-3.5 w-3.5 text-[var(--brand)]" aria-hidden />
              QA-Mappe mit Quellen, Lücken und Entscheidung
            </div>
            <h2 className="mt-6 max-w-4xl text-[42px] font-medium leading-[0.98] text-[var(--text-primary)] md:text-[68px]">
              {productHomeCopy.title}
            </h2>
            <p className="mt-6 max-w-2xl text-[18px] leading-8 text-[var(--text-secondary)]">
              {productHomeCopy.subtitle}
            </p>
          </div>

          <div className="mt-8 grid gap-5 xl:grid-cols-[1fr_auto] xl:items-end">
            <div>
              <div className="text-[24px] font-medium leading-tight text-[var(--text-primary)] md:text-[32px]">
                {productHomeCopy.decisionLine}
              </div>
              <p className="mt-2 text-[13px] font-medium text-[var(--text-secondary)]">
                {productHomeCopy.valueLine}
              </p>
            </div>
            <a
              href="#new-case"
              className="inline-flex h-12 w-fit items-center gap-2 rounded-md bg-[var(--brand)] px-5 text-[14px] font-medium text-white hover:bg-[var(--brand-strong)]"
            >
              {productHomeCopy.primaryAction}
              <ArrowRight className="h-4 w-4" aria-hidden />
            </a>
          </div>
        </div>

        <DossierPreview />
      </div>

      <WorkflowSteps />
    </section>
  );
}

function DossierPreview() {
  return (
    <aside className="flex min-h-[520px] flex-col justify-between rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)]">
      <div className="border-b border-[var(--border-default)] px-5 py-4">
        <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
          Prüfmappe-Vorschau
        </div>
        <div className="mt-2 flex items-center justify-between gap-3">
          <div className="text-[15px] font-medium text-[var(--text-primary)]">
            Entscheidung offen
          </div>
          <span className="rounded-full bg-[var(--severity-major-soft)] px-2.5 py-1 text-[11px] font-medium text-[var(--severity-major)]">
            QA prüfen
          </span>
        </div>
      </div>

      <div className="px-5 py-5">
        <DossierAlert
          title="Quelle passt nicht zur Aussage"
          description="Annex-Referenz und HEPA-Vorlauf müssen vor Freigabe abgeglichen werden."
        />

        <div className="mt-5 divide-y divide-[var(--border-muted)]">
          {productHomeCopy.dossierPreview.map((item) => (
            <DossierPreviewRow key={item.label} label={item.label} value={item.value} />
          ))}
        </div>
      </div>

      <div className="border-t border-[var(--border-default)] px-5 py-4">
        <div className="grid grid-cols-3 gap-2">
          {homeDecisionActions.map((action, index) => (
            <DecisionActionPreview key={action} action={action} active={index === 0} />
          ))}
        </div>
      </div>
    </aside>
  );
}

function DossierAlert({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] p-4">
      <div className="flex items-start gap-3">
        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-[var(--severity-major)]" aria-hidden />
        <div>
          <div className="text-[13px] font-medium text-[var(--text-primary)]">{title}</div>
          <p className="mt-1 text-[12px] leading-5 text-[var(--text-secondary)]">{description}</p>
        </div>
      </div>
    </div>
  );
}

function DossierPreviewRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-[96px_1fr] gap-3 py-3 text-[13px]">
      <div className="text-[11px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
        {label}
      </div>
      <div className="leading-6 text-[var(--text-primary)]">{value}</div>
    </div>
  );
}

function DecisionActionPreview({ action, active }: { action: string; active: boolean }) {
  return (
    <div
      className={`rounded-md border px-2 py-2 text-center text-[11px] font-medium ${
        active
          ? "border-[var(--brand)] bg-[var(--brand)] text-white"
          : "border-[var(--border-default)] bg-[var(--surface-secondary)] text-[var(--text-secondary)]"
      }`}
    >
      {action}
    </div>
  );
}

function WorkflowSteps() {
  return (
    <ol className="mt-8 grid gap-2 sm:grid-cols-4">
      {productHomeCopy.workflow.map((step, index) => (
        <li key={step} className="flex items-center gap-2 border-t border-[var(--border-default)] pt-3 text-[12px] leading-5 text-[var(--text-secondary)]">
          <span className="mono grid h-6 w-6 shrink-0 place-items-center rounded-md bg-[var(--surface-primary)] text-[11px] text-[var(--text-tertiary)]">
            {index + 1}
          </span>
          <span>{step}</span>
        </li>
      ))}
    </ol>
  );
}

function OutcomeChecklist() {
  return (
    <section className="grid gap-4 md:grid-cols-5">
      {productHomeCopy.outcomeChecks.map((check) => (
        <div key={check} className="border-l border-[var(--border-default)] pl-3 text-[13px] leading-6 text-[var(--text-secondary)]">
          <CheckCircle2 className="mb-2 h-4 w-4 text-[var(--brand)]" aria-hidden />
          {check}
        </div>
      ))}
    </section>
  );
}

function ReviewEntrySection() {
  return (
    <Panel title="Prüffälle">
      <EmptyState
        title="Noch kein echter Prüffall"
        text="Lege auf der Startseite einen Prüffall an. Danach erscheint hier der Link zur Prüfmappe."
        action={
          <Link
            href="/"
            className="inline-flex h-9 items-center rounded-md bg-[var(--brand)] px-3 text-[13px] font-medium text-white hover:bg-[var(--brand-strong)]"
          >
            <Plus className="mr-1.5 h-3.5 w-3.5" /> Prüffall vorbereiten
          </Link>
        }
      />
    </Panel>
  );
}

function AiArchitectureSection() {
  const roleIcons: Record<string, React.ReactNode> = {
    "Claim Extractor": <FileText className="h-4 w-4" />,
    "Scope & Signal Router": <SearchCheck className="h-4 w-4" />,
    "7 Reviewer Agents": <Brain className="h-4 w-4" />,
    "Evidence Verifier": <SearchCheck className="h-4 w-4" />,
    "Risk Fusion": <ShieldCheck className="h-4 w-4" />,
    "Human Review": <ClipboardCheck className="h-4 w-4" />,
  };

  return (
    <div className="space-y-5">
      <section className="surface p-6">
        <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
          <div>
            <div className="text-[11px] font-medium uppercase tracking-[0.16em] text-[var(--brand)]">
              Funktionsweise
            </div>
            <h2 className="mt-3 max-w-2xl text-[24px] font-medium leading-snug text-[var(--text-primary)]">
              {aiArchitectureConcept.title}
            </h2>
            <p className="mt-3 max-w-xl text-[14px] leading-relaxed text-[var(--text-secondary)]">
              {aiArchitectureConcept.subtitle}
            </p>
          </div>
          <ol className="space-y-2">
            {aiArchitectureConcept.flow.map((step, index) => (
              <li
                key={step.id}
                className="grid gap-3 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] p-3 md:grid-cols-[28px_1fr]"
              >
                <div className="mono grid h-6 w-6 place-items-center rounded bg-[var(--brand-soft)] text-[12px] font-medium text-[var(--brand-strong)]">
                  {index + 1}
                </div>
                <div>
                  <div className="text-[13px] font-medium">{step.title}</div>
                  <p className="mt-0.5 text-[12px] leading-relaxed text-[var(--text-secondary)]">
                    {step.description}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <Panel title="KI-Rollen">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {aiArchitectureConcept.aiRoles.map((role) => (
            <div
              key={role.role}
              className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4"
            >
              <div className="grid h-8 w-8 place-items-center rounded bg-[var(--brand-soft)] text-[var(--brand-strong)]">
                {roleIcons[role.role] ?? <Brain className="h-4 w-4" />}
              </div>
              <h3 className="mt-3 text-[14px] font-medium">{role.role}</h3>
              <p className="mt-1.5 text-[12px] leading-relaxed text-[var(--text-secondary)]">
                {role.purpose}
              </p>
              <div className="mt-3 rounded border border-[var(--border-muted)] bg-[var(--surface-secondary)] p-2.5 text-[11px] leading-relaxed text-[var(--text-secondary)]">
                <span className="font-medium text-[var(--text-primary)]">Gate:</span>{" "}
                {role.guardrail}
              </div>
            </div>
          ))}
        </div>
      </Panel>

      <Panel title="Human Feedback Registry">
        <HumanFeedbackRegistryPanel />
      </Panel>

      <Panel title="Guardrails">
        <div className="grid gap-2 md:grid-cols-2">
          {aiArchitectureConcept.nonNegotiables.map((rule) => (
            <div
              key={rule}
              className="flex items-start gap-2.5 rounded-md border border-[var(--border-muted)] bg-[var(--surface-secondary)] p-3 text-[12px] leading-relaxed text-[var(--text-secondary)]"
            >
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[var(--brand)]" />
              <span>{rule}</span>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}

function Panel({
  title,
  children,
  action,
}: {
  title: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.18 }}
      className="surface overflow-hidden"
    >
      <div className="flex items-center justify-between border-b border-[var(--border-default)] px-5 py-3">
        <h2 className="text-[14px] font-medium text-[var(--text-primary)]">{title}</h2>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </motion.section>
  );
}

function EmptyState({
  title,
  text,
  action,
}: {
  title: string;
  text: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="rounded-md border border-dashed border-[var(--border-strong)] bg-[var(--surface-secondary)] p-7 text-center">
      <h3 className="text-[14px] font-medium text-[var(--text-primary)]">{title}</h3>
      <p className="mx-auto mt-1.5 max-w-xl text-[13px] leading-relaxed text-[var(--text-secondary)]">
        {text}
      </p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
