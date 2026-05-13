"use client";

import Link from "next/link";
import { useState } from "react";
import {
  Archive,
  Brain,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  ClipboardCheck,
  FileText,
  FlaskConical,
  Gauge,
  Globe,
  History,
  Library,
  Menu,
  Moon,
  SearchCheck,
  ShieldCheck,
  Sun,
  X
} from "lucide-react";
import { useI18n, type TranslationKey } from "@/src/lib/i18n";
import { useTheme } from "@/src/lib/theme";
import { motion } from "@/src/components/ui/motion";
import { IntakeUploader } from "@/src/components/review-ui/intake-uploader";
import { aiArchitectureConcept, riskOrchestrationEntry } from "@/src/lib/review-ui";
import type { LucideIcon } from "lucide-react";

type NavItem = [slug: string, labelKey: TranslationKey, icon: LucideIcon];
type NavCategory = { nameKey: TranslationKey; items: NavItem[] };

const navCategories: NavCategory[] = [
  {
    nameKey: "nav.category.workspace",
    items: [
      ["dashboard", "nav.dashboard", Gauge],
      ["review-ui", "nav.backendReview", ShieldCheck],
      ["ai-architecture", "nav.aiArchitecture", Brain],
    ],
  },
  {
    nameKey: "nav.category.admin",
    items: [
      ["projects", "nav.projects", Archive],
      ["documents", "nav.documents", FileText],
      ["risk-library", "nav.riskLibrary", Library],
      ["audit-trail", "nav.auditTrail", History],
      ["validation-pack", "nav.validationPack", FlaskConical],
    ],
  },
];

const navItems = navCategories.flatMap((category) => category.items);

export const sectionSlugs = navItems.map(([slug]) => slug);

const pageTitleKeys = Object.fromEntries(
  navItems.map(([slug, labelKey]) => [slug, labelKey])
) as Record<string, TranslationKey>;

const roles = ["QRM_AUTHOR", "SME_REVIEWER", "QA_APPROVER", "AUDITOR", "ADMIN"] as const;

function pageTitle(slug: string, t: (key: TranslationKey) => string) {
  return t(pageTitleKeys[slug] ?? "nav.dashboard");
}

export function AppShell({ section }: { section: string; projectId?: string }) {
  const active = sectionSlugs.includes(section) ? section : "dashboard";

  return (
    <AppFrame section={active}>
      <Notice />
      <div className="mt-6">{renderSection(active)}</div>
    </AppFrame>
  );
}

export function AppFrame({
  section,
  children,
}: {
  section: string;
  children: React.ReactNode;
}) {
  const active = sectionSlugs.includes(section) ? section : "dashboard";
  const [role, setRole] = useState<(typeof roles)[number]>("QRM_AUTHOR");
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
        <div key={category.nameKey} className="mb-2">
          <button
            type="button"
            onClick={() => toggleCategory(category.nameKey)}
            className="flex w-full items-center justify-between px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-600 transition hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
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
              {category.items.map(([slug, labelKey, Icon]) => (
                <Link
                  key={slug}
                  href={slug === "dashboard" ? "/" : `/${slug}`}
                  onClick={() => setMobileNavOpen(false)}
                  aria-current={active === slug ? "page" : undefined}
                  className={`flex items-center justify-between rounded-xl px-3 py-2.5 text-sm transition ${
                    active === slug
                      ? "bg-white text-teal-600 shadow-sm ring-1 ring-black/5 dark:bg-slate-700 dark:text-teal-400 dark:ring-white/10"
                      : "text-slate-600 hover:bg-white/70 hover:text-ink dark:text-slate-400 dark:hover:bg-slate-700/50 dark:hover:text-white"
                  }`}
                >
                  <span className="flex min-w-0 items-center gap-3">
                    <Icon className="h-4 w-4 shrink-0" aria-hidden />
                    <span className="truncate">{t(labelKey)}</span>
                  </span>
                  {active === slug ? (
                    <span className="h-1.5 w-1.5 rounded-full bg-teal-500" aria-hidden />
                  ) : null}
                </Link>
              ))}
            </div>
          ) : null}
        </div>
      ))}
    </>
  );

  return (
    <div className="min-h-screen bg-mist text-ink transition-colors dark:bg-slate-900 dark:text-slate-100">
      {mobileNavOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/45 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileNavOpen(false)}
          aria-label="Close navigation"
        />
      ) : null}

      <aside
        className={`fixed inset-y-0 left-0 z-50 w-[280px] transform border-r border-black/10 bg-[#fbfcfb] transition-transform duration-300 dark:border-white/10 dark:bg-slate-800 lg:hidden ${
          mobileNavOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Mobile navigation"
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-black/10 px-5 py-4 dark:border-white/10">
            <BrandMark />
            <button
              type="button"
              onClick={() => setMobileNavOpen(false)}
              className="grid h-10 w-10 place-items-center rounded-xl text-slate-600 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-700"
              aria-label="Close navigation"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Main navigation">
            {navigation}
          </nav>
        </div>
      </aside>

      <aside className="fixed inset-y-0 left-0 hidden w-[280px] border-r border-black/10 bg-[#fbfcfb]/90 backdrop-blur-2xl dark:border-white/10 dark:bg-slate-800/90 lg:flex lg:flex-col">
        <div className="border-b border-black/10 px-5 py-6 dark:border-white/10">
          <BrandMark />
          <div className="mt-4 text-xs leading-5 text-slate-600 dark:text-slate-400">
            {t("brand.tagline")}
          </div>
        </div>
        <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Main navigation">
          {navigation}
        </nav>
        <div className="border-t border-black/10 px-5 py-4 text-xs leading-5 text-slate-500 dark:border-white/10 dark:text-slate-400">
          Draft output. QA/SME entscheidet.
        </div>
      </aside>

      <main id="main-content" className="lg:pl-[280px]">
        <header className="sticky top-0 z-10 border-b border-black/10 bg-[#fbfcfb]/78 px-4 py-4 backdrop-blur-2xl dark:border-white/10 dark:bg-slate-900/78 lg:px-8">
          <div className="mx-auto flex max-w-[1500px] items-center justify-between gap-3">
            <div className="flex items-center gap-4">
              <button
                type="button"
                onClick={() => setMobileNavOpen(true)}
                className="grid h-10 w-10 place-items-center rounded-xl border border-black/10 bg-white/80 text-slate-600 lg:hidden"
                aria-label="Open navigation menu"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div>
                <div className="text-[11px] uppercase tracking-[0.22em] text-slate-600 dark:text-slate-400">
                  Pharma QRM Delta Engine
                </div>
                <h1 className="mt-1 text-[26px] font-medium leading-tight tracking-[-0.045em] text-ink dark:text-white md:text-[30px]">
                  {pageTitle(active, t)}
                </h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="hidden rounded-full border border-teal-500/20 bg-white/70 px-3 py-1.5 text-xs font-medium text-teal-600 shadow-sm dark:border-teal-500/30 dark:bg-slate-800/70 dark:text-teal-400 md:inline-flex">
                <ShieldCheck className="mr-1.5 h-3.5 w-3.5" aria-hidden />
                Draft
              </span>
              <button
                type="button"
                onClick={() => setLocale(locale === "de" ? "en" : "de")}
                className="hidden h-10 items-center gap-2 rounded-xl border border-black/10 bg-white/80 px-3 text-sm shadow-sm hover:bg-white dark:border-white/10 dark:bg-slate-800/80 dark:hover:bg-slate-700 sm:inline-flex"
                aria-label={locale === "de" ? "Switch to English" : "Auf Deutsch wechseln"}
              >
                <Globe className="h-4 w-4 text-slate-600 dark:text-slate-300" />
                <span className="font-medium text-slate-700 dark:text-slate-200">
                  {locale.toUpperCase()}
                </span>
              </button>
              <button
                type="button"
                onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
                className="hidden h-10 w-10 place-items-center rounded-xl border border-black/10 bg-white/80 shadow-sm hover:bg-white dark:border-white/10 dark:bg-slate-800/80 dark:hover:bg-slate-700 sm:grid"
                aria-label={resolvedTheme === "dark" ? t("theme.light") : t("theme.dark")}
              >
                {resolvedTheme === "dark" ? (
                  <Sun className="h-4 w-4 text-amber-400" />
                ) : (
                  <Moon className="h-4 w-4 text-slate-600" />
                )}
              </button>
              <select
                className="hidden h-10 rounded-xl border border-black/10 bg-white/80 px-3 text-sm shadow-sm dark:border-white/10 dark:bg-slate-800/80 dark:text-white sm:block"
                value={role}
                onChange={(event) => setRole(event.target.value as (typeof roles)[number])}
                aria-label="Current role"
              >
                {roles.map((candidate) => (
                  <option key={candidate} value={candidate}>
                    {candidate.replaceAll("_", " ")}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-[1500px] px-4 py-7 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  );
}

function BrandMark() {
  return (
    <div className="flex items-center gap-3">
      <div className="grid h-10 w-10 place-items-center rounded-xl bg-teal-500 text-sm font-semibold text-white shadow-[0_12px_28px_rgba(0,155,141,0.22)]">
        Q
      </div>
      <div>
        <div className="text-[13px] font-semibold uppercase tracking-[0.18em] text-ink dark:text-white">
          Pharma QRM
        </div>
        <div className="text-[13px] font-semibold uppercase tracking-[0.18em] text-teal-600 dark:text-teal-400">
          Review Engine
        </div>
      </div>
    </div>
  );
}

function Notice() {
  const { t } = useI18n();
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="inline-flex items-center rounded-full border border-amber/25 bg-[#fff9ed]/82 px-4 py-2 text-sm text-slate-800 shadow-sm dark:border-amber-500/30 dark:bg-amber-950/30 dark:text-amber-100"
    >
      <span className="mr-2 inline-flex h-2 w-2 rounded-full bg-amber align-middle" />
      <strong className="mr-2 font-semibold">{t("notice.draft")}</strong>
      {t("notice.text")}
    </motion.div>
  );
}

function renderSection(section: string) {
  switch (section) {
    case "case-workspace":
      return <CaseWorkspaceSection />;
    case "review-ui":
      return <ReviewEntrySection />;
    case "ai-architecture":
      return <AiArchitectureSection />;
    case "projects":
      return <EmptyAdminSection title="Projekte" description="Noch keine Projekte geladen." />;
    case "documents":
      return <EmptyAdminSection title="Dokumente" description="Keine Dokumente im Frontend vorbefüllt." />;
    case "risk-library":
      return <EmptyAdminSection title="Risikobibliothek" description="Regelwerke werden über das Backend importiert." />;
    case "audit-trail":
      return <EmptyAdminSection title="Audit Trail" description="Audit Events entstehen nach Upload, Pipeline und Review." />;
    case "validation-pack":
      return <EmptyAdminSection title="Validierungsunterlagen" description="Draft-Templates werden nach Projektanlage erzeugt." />;
    default:
      return <DashboardSection />;
  }
}

function DashboardSection() {
  return (
    <div className="space-y-6">
      <section className="grid gap-6 lg:grid-cols-[0.86fr_1.14fr] lg:items-start">
        <div className="pt-3">
          <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-teal">
            QA-Prüfung vorbereiten
          </div>
          <h2 className="mt-5 max-w-3xl text-5xl font-light leading-[1.02] tracking-[-0.055em] text-ink dark:text-white md:text-6xl">
            Unterlagen hochladen. Prüfmappe erhalten.
          </h2>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 dark:text-slate-300">
            Lade Unterlagen zu einer Änderung, Abweichung, CAPA oder einem Audit hoch. Das System sortiert Quellen, offene Nachweise und Prüfpunkte, damit QA oder ein Fachexperte schneller entscheiden kann.
          </p>
          <div className="mt-7 grid gap-3 sm:grid-cols-2">
            <SummaryBlock title="Quelle sichtbar" text="Jeder Prüfpunkt braucht Dokument, Seite und Zitat." />
            <SummaryBlock title="Keine Auto-Freigabe" text="Unklare oder hohe Risiken bleiben bei einem Menschen." />
            <SummaryBlock title="Mehrere Blickwinkel" text="Das System sucht Risiken, Lücken und Widersprüche." />
            <SummaryBlock title="Auditierbar" text="Modell, Prompt, Regelwerk und Entscheidung bleiben nachvollziehbar." />
          </div>
        </div>
        <IntakeUploader />
      </section>

      <div className="grid gap-3 md:grid-cols-4">
        <Stat label="KI-Entscheidung" value="0" />
        <Stat label="Quelle Pflicht" value="100%" tone="teal" />
        <Stat label="Prüfmappe" value="Entwurf" tone="teal" />
        <Stat label="Letzter Schritt" value="QA/SME" />
      </div>

      <Panel title="So arbeitet der Prüfflow">
        <div className="grid gap-4 md:grid-cols-3">
          <SummaryBlock title="1. Unterlagen laden" text="Fallunterlagen, FMEA, SOP, Batch Record, Validierung oder Audit-Auszug." />
          <SummaryBlock title="2. Nachweise prüfen" text="Aussagen werden aus Quellen gezogen und gegen das Regelwerk geprüft." />
          <SummaryBlock title="3. Prüfung fokussieren" text="QA und SME sehen nur die relevanten Prüfpunkte, Lücken und Fragen." />
        </div>
      </Panel>
    </div>
  );
}

function CaseWorkspaceSection() {
  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_0.8fr]">
      <Panel title="Fallübersicht">
        <EmptyState
          title="Fallübersicht öffnen"
          text="Alle angelegten Prüffälle liegen in der Fallübersicht. Von dort öffnest du entweder den Fall selbst oder seine Prüfmappe."
          action={
            <Link
              href="/review-ui"
              className="inline-flex h-10 items-center rounded-xl bg-teal px-4 text-sm font-semibold text-white"
            >
              Zur Fallübersicht
            </Link>
          }
        />
      </Panel>
      <Panel title="Import-Pfad">
        <ol className="space-y-3 text-sm leading-6 text-slate-700 dark:text-slate-300">
          <li>1. Regelwerk importieren oder aktivieren.</li>
          <li>2. Prüffall anlegen.</li>
          <li>3. PDF/TXT/DOCX hochladen.</li>
          <li>4. Analyse starten.</li>
          <li>5. Prüfmappe öffnen.</li>
        </ol>
      </Panel>
    </div>
  );
}

function ReviewEntrySection() {
  return (
    <Panel title="Fallübersicht">
      <EmptyState
        title="Keine Demo-Fälle mehr"
        text="Lege auf der Startseite einen echten Prüffall an. Danach erscheint hier der Fall mit Link zur Prüfmappe."
        action={
          <Link
            href="/review-ui"
            className="inline-flex h-10 items-center rounded-xl bg-teal px-4 text-sm font-semibold text-white"
          >
            Fallübersicht öffnen
          </Link>
        }
      />
    </Panel>
  );
}

function AiArchitectureSection() {
  const roleIcons: Record<string, React.ReactNode> = {
    "Claim Extractor": <FileText className="h-5 w-5" />,
    "Primary Reviewer Agents": <Brain className="h-5 w-5" />,
    "Evidence Verifier": <SearchCheck className="h-5 w-5" />,
    "Adversarial Reviewer": <ClipboardCheck className="h-5 w-5" />,
    "Risk Fusion": <ShieldCheck className="h-5 w-5" />,
  };

  return (
    <div className="space-y-6">
      <section className="premium-surface rounded-[26px] border border-black/10 p-7 dark:border-white/10 lg:p-9">
        <div className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-teal">
              KI-Aufbau
            </div>
            <h2 className="mt-5 max-w-3xl text-5xl font-light leading-[1.02] tracking-[-0.055em] text-ink dark:text-white md:text-6xl">
              {aiArchitectureConcept.title}
            </h2>
            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 dark:text-slate-300">
              {aiArchitectureConcept.subtitle}
            </p>
          </div>
          <div className="space-y-3">
            {aiArchitectureConcept.flow.map((step, index) => (
              <div key={step.id} className="grid gap-3 rounded-xl border border-black/5 bg-white/76 p-4 dark:border-white/10 dark:bg-slate-800/72 md:grid-cols-[44px_1fr]">
                <div className="grid h-10 w-10 place-items-center rounded-full bg-teal text-sm font-semibold text-white">
                  {index + 1}
                </div>
                <div>
                  <div className="font-semibold tracking-[-0.025em]">{step.title}</div>
                  <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Panel title="KI-Rollen">
        <div className="grid gap-4 lg:grid-cols-5">
          {aiArchitectureConcept.aiRoles.map((role) => (
            <div key={role.role} className="rounded-[18px] border border-black/10 bg-white/78 p-5 dark:border-white/10 dark:bg-slate-800/78">
              <div className="grid h-10 w-10 place-items-center rounded-xl bg-teal-500/10 text-teal">
                {roleIcons[role.role] ?? <Brain className="h-5 w-5" />}
              </div>
              <h3 className="mt-4 font-semibold tracking-[-0.025em]">{role.role}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
                {role.purpose}
              </p>
              <div className="mt-4 rounded-xl bg-slate-50 p-3 text-xs leading-5 text-slate-600 dark:bg-slate-900/50 dark:text-slate-300">
                <span className="font-semibold text-ink dark:text-white">Gate:</span>{" "}
                {role.guardrail}
              </div>
            </div>
          ))}
        </div>
      </Panel>

      <Panel title="Guardrails">
        <div className="grid gap-3 md:grid-cols-2">
          {aiArchitectureConcept.nonNegotiables.map((rule) => (
            <div key={rule} className="flex items-start gap-3 rounded-xl bg-slate-50 p-4 text-sm leading-6 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
              <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-teal" />
              <span>{rule}</span>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}

function EmptyAdminSection({ title, description }: { title: string; description: string }) {
  return (
    <Panel title={title}>
      <EmptyState title="Leer" text={description} />
    </Panel>
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
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="premium-surface overflow-hidden rounded-[20px] border border-black/10 dark:border-white/10"
    >
      <div className="flex items-center justify-between border-b border-black/10 px-5 py-4 dark:border-white/10">
        <h2 className="text-base font-semibold tracking-[-0.025em]">{title}</h2>
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
    <div className="rounded-xl border border-dashed border-slate-300 bg-white/70 p-8 text-center dark:border-slate-700 dark:bg-slate-800/50">
      <h3 className="font-semibold tracking-[-0.025em]">{title}</h3>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-600 dark:text-slate-300">
        {text}
      </p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}

function SummaryBlock({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-600 dark:text-slate-300">
        {title}
      </div>
      <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-400">{text}</p>
    </div>
  );
}

function Stat({
  label,
  value,
  tone = "slate",
}: {
  label: string;
  value: string | number;
  tone?: "slate" | "teal";
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
      className="cursor-default rounded-[18px] border border-black/10 bg-white/88 px-5 py-4 shadow-sm dark:border-white/10 dark:bg-slate-800/88"
    >
      <div className={`text-3xl font-light tracking-[-0.06em] ${tone === "teal" ? "text-teal" : ""}`}>
        {value}
      </div>
      <div className="mt-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600 dark:text-slate-400">
        {label}
      </div>
    </motion.div>
  );
}
