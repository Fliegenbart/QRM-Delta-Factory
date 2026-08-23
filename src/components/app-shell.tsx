"use client";

import Link from "next/link";
import { useState } from "react";
import {
  AlertCircle,
  Brain,
  CheckCircle2,
  Crosshair,
  Gauge,
  Library,
  Menu,
  Plus,
  ShieldCheck,
  X,
} from "lucide-react";
import dynamic from "next/dynamic";
import { useI18n, type TranslationKey } from "@/src/lib/i18n";
import { aiArchitectureConcept } from "@/src/lib/review-ui";
import type { RingversuchRun } from "@/src/components/review-ui/ringversuch-dashboard";
import { deriveLandingProofStats } from "@/src/lib/ringversuch-overview";
import { SignOutButton } from "@/src/components/auth/sign-out-button";
import type { LucideIcon } from "lucide-react";

// Heavy sections load on demand so each route only ships the code it needs.
function SectionSkeleton() {
  return (
    <div className="surface animate-pulse p-6" aria-hidden>
      <div className="h-5 w-48 rounded bg-[var(--surface-secondary)]" />
      <div className="mt-4 h-3 w-full max-w-xl rounded bg-[var(--surface-secondary)]" />
      <div className="mt-2 h-3 w-3/4 max-w-lg rounded bg-[var(--surface-secondary)]" />
    </div>
  );
}

const RequirementLibraryManager = dynamic(
  () => import("@/src/components/review-ui/requirement-library-manager").then((m) => m.RequirementLibraryManager),
  { loading: () => <SectionSkeleton /> }
);
const RingversuchDashboard = dynamic(
  () => import("@/src/components/review-ui/ringversuch-dashboard").then((m) => m.RingversuchDashboard),
  { loading: () => <SectionSkeleton /> }
);
const ModelStackPanel = dynamic(
  () => import("@/src/components/review-ui/model-stack-panel").then((m) => m.ModelStackPanel),
  { ssr: false }
);
const ReviewCalibrationPanel = dynamic(
  () => import("@/src/components/review-ui/review-calibration-panel").then((m) => m.ReviewCalibrationPanel),
  { loading: () => <SectionSkeleton /> }
);
const OverviewLanding = dynamic(
  () => import("@/src/components/review-ui/overview-landing").then((m) => m.OverviewLanding),
  { loading: () => <SectionSkeleton /> }
);

type NavItem = [slug: string, labelKey: TranslationKey, icon: LucideIcon];
type NavCategory = { nameKey: TranslationKey; items: NavItem[] };

// Two jobs in the signed-in navigation, nothing else: do the work
// (Prüffälle, Regelwerk) and understand the system (Ringversuch,
// Funktionsweise, Kalibrierung). The pitch pages live outside this frame --
// /ueberblick is its own landing and "/" redirects into the tool -- because
// six equal entries for selling, working and proving read as a muddle to
// anyone who already signed in.
const primaryNavItems: NavItem[] = [
  ["prueffaelle", "nav.backendReview", ShieldCheck],
  ["risk-library", "nav.riskLibrary", Library],
];
const secondaryNavItems: NavItem[] = [
  ["ringversuch", "nav.ringversuch", Crosshair],
  ["ai-architecture", "nav.aiArchitecture", Brain],
  ["kalibrierung", "nav.calibration", Gauge],
];

const navItems = [...primaryNavItems, ...secondaryNavItems];

// Routes the [section] page answers. "dashboard" and "ueberblick" stay
// routable (home redirects, the landing renders standalone) but are no
// longer navigation entries.
export const sectionSlugs = [...navItems.map(([slug]) => slug), "dashboard", "ueberblick"];


function normalizePublicSection(section: string) {
  if (section === "review-ui") return "prueffaelle";
  return sectionSlugs.includes(section) ? section : "prueffaelle";
}

export function AppShell({
  section,
  ringversuchRuns,
}: {
  section: string;
  ringversuchRuns?: RingversuchRun[];
}) {
  const active = normalizePublicSection(section);
  // Public pitch landing renders standalone — no workspace sidebar/header chrome.
  if (active === "ueberblick") {
    return <OverviewLanding proofStats={deriveLandingProofStats(ringversuchRuns)} />;
  }
  return <AppFrame section={active}>{renderSection(active, ringversuchRuns)}</AppFrame>;
}

function NavLink({
  slug,
  labelKey,
  Icon,
  block,
  muted,
  active,
  t,
  onNavigate,
}: {
  slug: string;
  labelKey: TranslationKey;
  Icon: LucideIcon;
  block?: boolean;
  muted?: boolean;
  active: string;
  t: (key: TranslationKey) => string;
  onNavigate: () => void;
}) {
  const isActive = active === slug;
  return (
    <Link
      href={slug === "prueffaelle" ? "/review-ui" : `/${slug}`}
      onClick={onNavigate}
      aria-current={isActive ? "page" : undefined}
      className={`${block ? "flex" : "inline-flex"} items-center gap-2 rounded-md px-3 py-2 text-[13px] transition-colors ${
        isActive
          ? "bg-[var(--brand-soft)] text-[var(--brand-strong)] font-medium"
          : muted
            ? "text-[var(--text-tertiary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)]"
            : "text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)]"
      }`}
    >
      <Icon className="h-4 w-4 shrink-0" aria-hidden />
      <span>{t(labelKey)}</span>
    </Link>
  );
}

export function AppFrame({
  section,
  children,
}: {
  section: string;
  children: React.ReactNode;
}) {
  const active = normalizePublicSection(section);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const { t } = useI18n();
  const closeMobileNav = () => setMobileNavOpen(false);

  return (
    <div className="min-h-screen text-[var(--text-primary)]">
      <header className="sticky top-0 z-20 border-b border-[var(--border-default)] bg-[var(--background)]">
        <div className="mx-auto flex max-w-[1280px] items-center justify-between gap-4 px-4 py-3 lg:px-8">
          <div className="flex items-center gap-5">
            <Link href="/" aria-label="Pharma QRM" className="shrink-0">
              <BrandMark />
            </Link>
            <nav className="hidden items-center gap-0.5 lg:flex" aria-label="Hauptnavigation">
              {primaryNavItems.map(([slug, labelKey, Icon]) => (
                <NavLink key={slug} slug={slug} labelKey={labelKey} Icon={Icon} active={active} t={t} onNavigate={closeMobileNav} />
              ))}
              <span className="mx-2 h-5 w-px bg-[var(--border-default)]" aria-hidden />
              {secondaryNavItems.map(([slug, labelKey, Icon]) => (
                <NavLink key={slug} slug={slug} labelKey={labelKey} Icon={Icon} active={active} t={t} onNavigate={closeMobileNav} muted />
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-2">
            <SignOutButton />
            <button
              type="button"
              onClick={() => setMobileNavOpen((open) => !open)}
              className="grid h-9 w-9 place-items-center rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] text-[var(--text-secondary)] lg:hidden"
              aria-label="Menü"
              aria-expanded={mobileNavOpen}
            >
              {mobileNavOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </button>
          </div>
        </div>
        {mobileNavOpen ? (
          <nav
            className="border-t border-[var(--border-default)] px-4 py-3 lg:hidden"
            aria-label="Hauptnavigation"
          >
            <div className="flex flex-col gap-0.5">
              {navItems.map(([slug, labelKey, Icon]) => (
                <NavLink key={slug} slug={slug} labelKey={labelKey} Icon={Icon} block active={active} t={t} onNavigate={closeMobileNav} />
              ))}
            </div>
          </nav>
        ) : null}
      </header>

      <main id="main-content">
        <div className="mx-auto max-w-[1280px] px-4 py-8 lg:px-8">{children}</div>
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

function renderSection(section: string, ringversuchRuns?: RingversuchRun[]) {
  switch (section) {
    case "prueffaelle":
      return <ReviewEntrySection />;
    case "ai-architecture":
      return <AiArchitectureSection />;
    case "risk-library":
      return <RequirementLibraryManager />;
    case "ringversuch":
      return <RingversuchDashboard initialRuns={ringversuchRuns} />;
    case "kalibrierung":
      return <CalibrationSection />;
    default:
      return <ReviewEntrySection />;
  }
}

function CalibrationSection() {
  return (
    <div className="space-y-4">
      <SectionIntro
        title="Kalibrierung"
        description="Freigegebene QA-Entscheidungen aus echten Fällen werden zu Beispielen, gegen die jede neue Version des Prüfwerks bestehen muss. Nur Beispiele mit bestandenem Regressionstest sind aktiv."
      />
      <Panel title="Qualität der Prüfhinweise aus geprüften Fällen">
        <ReviewCalibrationPanel />
      </Panel>
    </div>
  );
}

/* ----- Triage dashboard ----- */

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

function ReviewEntrySection() {
  return (
    <Panel title="Prüffälle">
      <EmptyState
        title="Prüffälle"
        text="Die Prüffälle liegen unter /review-ui."
        action={
          <Link
            href="/review-ui"
            className="inline-flex h-9 items-center rounded-md bg-[var(--brand)] px-3 text-[13px] font-medium text-white hover:bg-[var(--brand-strong)]"
          >
            Zu den Prüffällen
          </Link>
        }
      />
    </Panel>
  );
}

function AiArchitectureSection() {
  return (
    <div className="space-y-6">
      <section className="surface p-6">
        <div className="grid gap-7 lg:grid-cols-[0.82fr_1.18fr]">
          <div>
            <div className="text-[11px] font-medium uppercase tracking-[0.16em] text-[var(--brand)]">
              Funktionsweise
            </div>
            <h2 className="mt-3 max-w-2xl text-[30px] font-semibold leading-tight text-[var(--text-primary)]">
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
                  <div className="mt-2 rounded border border-[var(--border-muted)] bg-[var(--surface-primary)] px-2.5 py-2 text-[11px] leading-relaxed text-[var(--text-secondary)]">
                    {step.safeguard}
                  </div>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <ModelStackPanel />

      <Panel title="Die Grenzen, die fest eingebaut sind:">
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
    <section className="surface overflow-hidden rise-in">
      <div className="flex items-center justify-between border-b border-[var(--border-default)] px-5 py-3">
        <h2 className="ui-title text-[14px] font-medium text-[var(--text-primary)]">{title}</h2>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </section>
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
