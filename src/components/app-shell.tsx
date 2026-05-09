"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  AlertTriangle,
  Archive,
  Bot,
  Brain,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  ClipboardCheck,
  Database,
  FileDown,
  FileText,
  FlaskConical,
  Gauge,
  Globe,
  History,
  Library,
  Loader2,
  Lock,
  Menu,
  MessageCircle,
  Moon,
  PackageCheck,
  MessageSquareWarning,
  Play,
  Bell,
  BookOpen,
  HelpCircle,
  ShieldCheck,
  Sparkles,
  Sun,
  Table2,
  Users,
  X,
  Zap
} from "lucide-react";
import { useI18n, type TranslationKey, translations } from "@/src/lib/i18n";
import { useTheme } from "@/src/lib/theme";
import { motion, AnimatePresence, AnimatedButton, AnimatedCard, FadeInUp, StaggerContainer, StaggerItem, AnimatedProgress, FlowStep, FlowConnector, Skeleton } from "@/src/components/ui/motion";
import {
  demoAuditLogs,
  demoDocuments,
  demoGaps,
  demoPlausibilityChecks,
  demoProject,
  demoRedTeamFindings,
  demoRiskItems,
  demoRiskLibrary,
  demoSnippets,
  demoUsers,
  reviewQueue
} from "@/src/lib/demo-data";
import { exportPackage, runDeterministicGates } from "@/src/lib/qrm-engine";
import { caseWorkspaceStructure, riskOrchestrationEntry } from "@/src/lib/review-ui";
import {
  buildEvidenceMap,
  buildReviewQueue,
  generateRiskDeltaReviewPack,
  summarizeWorkload,
  type PackageReviewResult,
  type ReviewPackage,
  type ReviewQueueItem
} from "@/src/lib/risk-review-package-builder";
import { generateValidationPack } from "@/src/lib/validation-pack";
import { DocumentUpload, type UploadedDocument } from "@/src/components/document-upload";
import type { LucideIcon } from "lucide-react";

// Navigation item type - uses translation keys
type NavItem = [slug: string, labelKey: TranslationKey, icon: LucideIcon];
type NavCategory = { nameKey: TranslationKey; items: NavItem[] };

// Navigation organized by categories for better UX
const navCategories: NavCategory[] = [
  {
    nameKey: "nav.category.workspace",
    items: [
      ["dashboard", "nav.dashboard", Gauge],
      ["case-workspace", "nav.caseWorkspace", PackageCheck],
      ["delta-analysis", "nav.deltaAnalysis", Bot],
      ["review-ui", "nav.backendReview", ShieldCheck],
    ]
  },
  {
    nameKey: "nav.category.admin",
    items: [
      ["projects", "nav.projects", Archive],
      ["documents", "nav.documents", FileText],
      ["risk-library", "nav.riskLibrary", Library],
      ["validation-pack", "nav.validationPack", FlaskConical],
      ["audit-trail", "nav.auditTrail", History],
      ["admin-users", "nav.adminUsers", Users],
    ]
  },
];

// Flatten for compatibility
const navItems: NavItem[] = navCategories.flatMap(cat => cat.items);
const legacySectionSlugs = [
  "source-snippets",
  "trigger-input",
  "qrm-matrix",
  "review-packages",
  "plausibility-checks",
  "red-team-findings",
  "review-queue",
  "approvals",
  "evidence-map",
  "gaps",
  "export-package"
] as const;

export const sectionSlugs = [...navItems.map(([slug]) => slug), ...legacySectionSlugs];

// Map slugs to translation keys for page titles
const pageTitleKeys: Record<string, TranslationKey> = Object.fromEntries(
  [
    ...navItems.map(([slug, labelKey]) => [slug, labelKey]),
    ["source-snippets", "nav.sourceSnippets"],
    ["trigger-input", "nav.triggerInput"],
    ["qrm-matrix", "nav.qrmMatrix"],
    ["review-packages", "nav.reviewPackages"],
    ["plausibility-checks", "nav.plausibilityChecks"],
    ["red-team-findings", "nav.redTeamFindings"],
    ["review-queue", "nav.reviewQueue"],
    ["approvals", "nav.approvals"],
    ["evidence-map", "nav.evidenceMap"],
    ["gaps", "nav.gaps"],
    ["export-package", "nav.exportPackage"]
  ]
) as Record<string, TranslationKey>;

// Helper to get translated page title
function getPageTitle(slug: string, t: (key: TranslationKey) => string): string {
  const key = pageTitleKeys[slug];
  if (key) return t(key);
  if (slug === "project-detail") return t("nav.projects");
  return t("nav.dashboard");
}

// Multi-Agent Analysis Types
interface AgentMessage {
  role: "AUTHOR" | "CRITIC" | "RESOLVER";
  timestamp: string;
  content: string;
  tokenUsage: { inputTokens: number; outputTokens: number; totalTokens: number; estimatedCostUsd: number };
}

interface MultiAgentResult {
  riskItems: Array<{
    riskId: string;
    processStep: string;
    failureMode: string;
    potentialCause: string;
    potentialEffect: string;
    severity: number;
    occurrence: number;
    detectability: number;
    initialRpn: number;
    confidenceLevel: "HIGH" | "MEDIUM" | "LOW";
    claims: Array<{ claim: string; confidence: string }>;
  }>;
  findings: Array<{
    riskItemId: string;
    severity: "BLOCKER" | "CONCERN" | "SUGGESTION";
    category: string;
    description: string;
    suggestedAction: string;
  }>;
  gaps: Array<{
    id: string;
    priority: string;
    category: string;
    description: string;
    identifiedBy: string;
  }>;
  escalatedItems: string[];
  iterationsUsed: number;
  conversation: AgentMessage[];
  tokenUsage: { inputTokens: number; outputTokens: number; totalTokens: number; estimatedCostUsd: number };
  processingTimeMs: number;
}

export function AppShell({ section, projectId }: { section: string; projectId?: string }) {
  const active = sectionSlugs.includes(section as (typeof sectionSlugs)[number]) || section === "project-detail" ? section : "dashboard";
  const [role, setRole] = useState("QRM_AUTHOR");
  const { locale, setLocale, t } = useI18n();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [reviewPackages, setReviewPackages] = useState<ReviewPackage[]>([]);
  const [packageResults, setPackageResults] = useState<Record<string, PackageReviewResult>>({});
  const [riskDeltaExport, setRiskDeltaExport] = useState<ReturnType<typeof generateRiskDeltaReviewPack> | null>(null);
  const [loginMessage, setLoginMessage] = useState("Demo-Rollen nutzen Passwort demo123.");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(navCategories.map(cat => [cat.nameKey, true]))
  );

  // Multi-Agent Analysis State
  const [multiAgentState, setMultiAgentState] = useState<"idle" | "running" | "done" | "error">("idle");
  const [multiAgentResult, setMultiAgentResult] = useState<MultiAgentResult | null>(null);
  const [multiAgentError, setMultiAgentError] = useState<string | null>(null);
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([]);

  const exportDraft = useMemo(
    () => exportPackage({ project: demoProject, riskItems: demoRiskItems, gaps: demoGaps, approvedPackage: false }),
    []
  );
  const approvedStyleExport = useMemo(
    () => exportPackage({ project: demoProject, riskItems: demoRiskItems, gaps: demoGaps, approvedPackage: true }),
    []
  );

  async function generateReviewPackages() {
    const response = await fetch("/api/review-packages", { method: "POST" });
    const data = (await response.json()) as { packages: ReviewPackage[] };
    setReviewPackages(data.packages);
    setPackageResults({});
    setRiskDeltaExport(null);
  }

  async function runPackageReview(packageId: string) {
    const response = await fetch("/api/review-packages/plausibility", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ packageId })
    });
    const data = (await response.json()) as PackageReviewResult;
    setPackageResults((current) => ({ ...current, [packageId]: data }));
    setReviewPackages((current) =>
      current.map((pkg) => (pkg.id === packageId && data.input_status === "COMPLETE" ? { ...pkg, package_status: "PLAUSIBILITY_CHECKED" } : pkg))
    );
  }

  async function runAllPackageReviews() {
    const readyPackages = reviewPackages.filter((pkg) => pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK");
    const entries = await Promise.all(
      readyPackages.map(async (pkg) => {
        const response = await fetch("/api/review-packages/plausibility", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ packageId: pkg.id })
        });
        return [pkg.id, (await response.json()) as PackageReviewResult] as const;
      })
    );
    const nextResults = Object.fromEntries(entries);
    setPackageResults((current) => ({ ...current, ...nextResults }));
    setReviewPackages((current) =>
      current.map((pkg) => (nextResults[pkg.id]?.input_status === "COMPLETE" ? { ...pkg, package_status: "PLAUSIBILITY_CHECKED" } : pkg))
    );
  }

  function generateDeltaExport() {
    setRiskDeltaExport(generateRiskDeltaReviewPack({ packages: reviewPackages, results: packageResults, approvedExport: false }));
  }

  async function runMultiAgentAnalysis() {
    setMultiAgentState("running");
    setMultiAgentError(null);
    setMultiAgentResult(null);

    try {
      // Convert uploaded documents to source snippets format if provided
      const sourceDocuments = uploadedDocuments.length > 0
        ? uploadedDocuments.map(doc => ({
            id: doc.id,
            content: doc.content,
            documentType: doc.type.includes("pdf") ? "PDF Document"
              : doc.type.includes("word") ? "Word Document"
              : doc.name.endsWith(".csv") ? "Data File"
              : "Text Document",
            fileName: doc.name,
          }))
        : undefined; // Will use realistic mock data on server

      const response = await fetch("/api/ai/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          projectId: demoProject.id,
          changeControlId: "CC-2026-014",
          ...(sourceDocuments && { sourceDocuments }),
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Analysis failed");
      }

      setMultiAgentResult(data.result);
      setMultiAgentState("done");
    } catch (error) {
      setMultiAgentError(error instanceof Error ? error.message : "Unknown error");
      setMultiAgentState("error");
    }
  }

  function toggleCategory(categoryName: string) {
    setExpandedCategories(prev => ({ ...prev, [categoryName]: !prev[categoryName] }));
  }

  // Shared navigation content for desktop and mobile
  const navigationContent = (
    <>
      {navCategories.map((category) => (
        <div key={category.nameKey} className="mb-2">
          <button
            type="button"
            onClick={() => toggleCategory(category.nameKey)}
            className="flex w-full items-center justify-between px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-600 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
            aria-expanded={expandedCategories[category.nameKey]}
          >
            <span>{t(category.nameKey)}</span>
            {expandedCategories[category.nameKey] ? (
              <ChevronDown className="h-3 w-3" aria-hidden />
            ) : (
              <ChevronRight className="h-3 w-3" aria-hidden />
            )}
          </button>
          {expandedCategories[category.nameKey] && (
            <div className="mt-1 space-y-0.5">
              {category.items.map(([slug, labelKey, Icon]) => (
                <Link
                  key={slug}
                  href={slug === "dashboard" ? "/" : `/${slug}`}
                  onClick={() => setMobileNavOpen(false)}
                  className={`flex items-center justify-between rounded-2xl px-3 py-2.5 text-sm transition ${
                    active === slug
                      ? "bg-white dark:bg-slate-700 text-teal-600 dark:text-teal-400 shadow-[0_12px_35px_rgba(17,24,29,0.07)] dark:shadow-[0_12px_35px_rgba(0,0,0,0.3)] ring-1 ring-black/5 dark:ring-white/10"
                      : "text-slate-600 dark:text-slate-400 hover:bg-white/70 dark:hover:bg-slate-700/50 hover:text-ink dark:hover:text-white"
                  }`}
                  aria-current={active === slug ? "page" : undefined}
                >
                  <span className="flex min-w-0 items-center gap-3">
                    <Icon className="h-4 w-4 shrink-0" aria-hidden />
                    <span className="truncate">{t(labelKey)}</span>
                  </span>
                  {active === slug ? <span className="h-1.5 w-1.5 rounded-full bg-teal-500" aria-hidden /> : null}
                </Link>
              ))}
            </div>
          )}
        </div>
      ))}
    </>
  );

  return (
    <div className="min-h-screen bg-mist dark:bg-slate-900 text-ink dark:text-slate-100 transition-colors">
      {/* Mobile Navigation Overlay */}
      {mobileNavOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileNavOpen(false)}
          aria-hidden
        />
      )}

      {/* Mobile Navigation Drawer */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-[300px] transform border-r border-black/10 dark:border-white/10 bg-[#fbfcfb] dark:bg-slate-800 transition-transform duration-300 ease-in-out lg:hidden ${
          mobileNavOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Mobile navigation"
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-black/10 px-5 py-4">
            <div>
              <div className="text-[13px] font-semibold uppercase tracking-[0.18em] text-ink">Pharma QRM</div>
              <div className="text-[13px] font-semibold uppercase tracking-[0.18em] text-teal-600">Delta Factory</div>
            </div>
            <button
              type="button"
              onClick={() => setMobileNavOpen(false)}
              className="grid h-10 w-10 place-items-center rounded-xl text-slate-600 hover:bg-slate-100"
              aria-label="Close navigation"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Main navigation">
            {navigationContent}
          </nav>
        </div>
      </aside>

      {/* Desktop Sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-[300px] border-r border-black/10 dark:border-white/10 bg-[#fbfcfb]/90 dark:bg-slate-800/90 backdrop-blur-2xl lg:flex lg:flex-col" aria-label="Desktop navigation">
        <div className="border-b border-black/10 px-5 py-6">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-2xl bg-teal-500 text-sm font-semibold text-white shadow-[0_16px_35px_rgba(0,155,141,0.26)]">Q</div>
            <div>
              <div className="text-[13px] font-semibold uppercase tracking-[0.18em] text-ink">Pharma QRM</div>
              <div className="text-[13px] font-semibold uppercase tracking-[0.18em] text-teal-600">Delta Factory</div>
            </div>
          </div>
          <div className="mt-4 text-xs leading-5 text-slate-600">{t("brand.tagline")}</div>
        </div>
        <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Main navigation">
          {navigationContent}
        </nav>
        <div className="border-t border-black/10 px-5 py-4">
          <div className="flex items-center justify-center gap-4 text-slate-600">
            <button type="button" className="grid h-9 w-9 place-items-center rounded-xl hover:bg-slate-100 hover:text-ink transition-colors" aria-label="Notifications">
              <Bell className="h-4 w-4" />
            </button>
            <button type="button" className="grid h-9 w-9 place-items-center rounded-xl hover:bg-slate-100 hover:text-ink transition-colors" aria-label="Help">
              <HelpCircle className="h-4 w-4" />
            </button>
            <button type="button" className="grid h-9 w-9 place-items-center rounded-xl hover:bg-slate-100 hover:text-ink transition-colors" aria-label="Documentation">
              <BookOpen className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      <main id="main-content" className="lg:pl-[300px]">
        <header className="sticky top-0 z-10 border-b border-black/10 dark:border-white/10 bg-[#fbfcfb]/78 dark:bg-slate-900/78 px-4 py-4 backdrop-blur-2xl lg:px-8">
          <div className="mx-auto flex max-w-[1500px] flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-4">
              {/* Mobile menu button */}
              <button
                type="button"
                onClick={() => setMobileNavOpen(true)}
                className="grid h-10 w-10 place-items-center rounded-xl border border-black/10 bg-white/80 text-slate-600 lg:hidden"
                aria-label="Open navigation menu"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div>
                <div className="text-[11px] uppercase tracking-[0.22em] text-slate-600 dark:text-slate-400">Workspace / {demoProject.name}</div>
                <h1 className="mt-1 text-[26px] font-medium leading-tight tracking-[-0.045em] md:text-[30px] text-ink dark:text-white">{getPageTitle(active, t)}</h1>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
              <span className="hidden rounded-full border border-teal-500/20 bg-white/70 dark:bg-slate-800/70 dark:border-teal-500/30 px-3 py-1.5 text-xs font-medium text-teal-600 dark:text-teal-400 shadow-sm md:inline-flex">
                <ShieldCheck className="mr-1.5 h-3.5 w-3.5" aria-hidden />
                {t("header.auditTrailActive")}
              </span>
              <span className="hidden rounded-full border border-teal-500/20 bg-white/70 dark:bg-slate-800/70 dark:border-teal-500/30 px-3 py-1.5 text-xs font-medium text-teal-600 dark:text-teal-400 shadow-sm lg:inline-flex">v1.2.0</span>

              {/* Language Toggle */}
              <button
                type="button"
                onClick={() => setLocale(locale === "de" ? "en" : "de")}
                className="inline-flex h-10 items-center gap-2 rounded-2xl border border-black/10 dark:border-white/10 bg-white/80 dark:bg-slate-800/80 px-3 text-sm shadow-sm hover:bg-white dark:hover:bg-slate-700 transition-colors"
                aria-label={locale === "de" ? "Switch to English" : "Auf Deutsch wechseln"}
              >
                <Globe className="h-4 w-4 text-slate-600 dark:text-slate-300" />
                <span className="font-medium text-slate-700 dark:text-slate-200">{locale.toUpperCase()}</span>
              </button>

              {/* Theme Toggle */}
              <button
                type="button"
                onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
                className="grid h-10 w-10 place-items-center rounded-2xl border border-black/10 dark:border-white/10 bg-white/80 dark:bg-slate-800/80 shadow-sm hover:bg-white dark:hover:bg-slate-700 transition-colors"
                aria-label={resolvedTheme === "dark" ? t("theme.light") : t("theme.dark")}
              >
                <AnimatePresence mode="wait">
                  {resolvedTheme === "dark" ? (
                    <motion.div key="sun" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.2 }}>
                      <Sun className="h-4 w-4 text-amber-400" />
                    </motion.div>
                  ) : (
                    <motion.div key="moon" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.2 }}>
                      <Moon className="h-4 w-4 text-slate-600" />
                    </motion.div>
                  )}
                </AnimatePresence>
              </button>

              <select
                className="h-10 rounded-2xl border border-black/10 dark:border-white/10 bg-white/80 dark:bg-slate-800/80 dark:text-white px-3 text-sm shadow-sm"
                value={role}
                onChange={(event) => setRole(event.target.value)}
                aria-label="Current role"
              >
                {demoUsers.map((user) => (
                  <option key={user.id} value={user.role}>
                    {user.role.replaceAll("_", " ")}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="inline-flex h-10 items-center gap-2 rounded-2xl bg-ink dark:bg-teal-600 px-4 text-sm font-medium text-white shadow-[0_16px_40px_rgba(17,24,29,0.18)] transition-transform hover:scale-[1.02] active:scale-[0.98]"
                onClick={() => setLoginMessage(`Aktive Demo-Rolle: ${role.replaceAll("_", " ")}`)}
              >
                <Lock className="h-4 w-4" aria-hidden />
                <span className="hidden sm:inline">{t("header.localAuth")}</span>
              </button>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-[1500px] px-4 py-7 lg:px-8">
          <Notice text={t("notice.text")} />
          <div className="mt-4 text-sm text-slate-600">{loginMessage}</div>
          <div className="mt-6">{renderSection(active, { exportDraft, approvedStyleExport, role, projectId, reviewPackages, packageResults, generateReviewPackages, runPackageReview, runAllPackageReviews, generateDeltaExport, riskDeltaExport, multiAgentState, multiAgentResult, multiAgentError, runMultiAgentAnalysis, uploadedDocuments, setUploadedDocuments })}</div>
        </div>
      </main>
    </div>
  );
}

function renderSection(
  section: string,
  context: {
    exportDraft: ReturnType<typeof exportPackage>;
    approvedStyleExport: ReturnType<typeof exportPackage>;
    role: string;
    projectId?: string;
    reviewPackages: ReviewPackage[];
    packageResults: Record<string, PackageReviewResult>;
    generateReviewPackages: () => Promise<void>;
    runPackageReview: (packageId: string) => Promise<void>;
    runAllPackageReviews: () => Promise<void>;
    generateDeltaExport: () => void;
    riskDeltaExport: ReturnType<typeof generateRiskDeltaReviewPack> | null;
    // Multi-Agent Analysis
    multiAgentState: "idle" | "running" | "done" | "error";
    multiAgentResult: MultiAgentResult | null;
    multiAgentError: string | null;
    runMultiAgentAnalysis: () => Promise<void>;
    // Document Upload
    uploadedDocuments: UploadedDocument[];
    setUploadedDocuments: (documents: UploadedDocument[]) => void;
  }
) {
  switch (section) {
    case "case-workspace":
      return <CaseWorkspaceSection {...context} />;
    case "projects":
      return <ProjectsSection />;
    case "project-detail":
      return <ProjectDetail id={context.projectId ?? demoProject.id} />;
    case "documents":
      return <DocumentsSection />;
    case "source-snippets":
      return <SnippetsSection />;
    case "risk-library":
      return <RiskLibrarySection />;
    case "trigger-input":
      return <TriggerSection />;
    case "delta-analysis":
      return <DeltaSection />;
    case "review-packages":
      return <ReviewPackagesSection {...context} />;
    case "qrm-matrix":
      return <MatrixSection />;
    case "evidence-map":
      return <EvidenceSection />;
    case "gaps":
      return <GapsSection />;
    case "plausibility-checks":
      return <PlausibilitySection />;
    case "red-team-findings":
      return <RedTeamSection />;
    case "review-queue":
      return <ReviewQueueSection />;
    case "approvals":
      return <ApprovalsSection role={context.role} />;
    case "audit-trail":
      return <AuditTrailSection />;
    case "export-package":
      return <ExportSection {...context} />;
    case "validation-pack":
      return <ValidationPackSection />;
    case "admin-users":
      return <AdminSection />;
    default:
      return <DashboardSection {...context} />;
  }
}

function Notice({ text }: { text: string }) {
  const { t } = useI18n();
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-[22px] border border-amber/25 dark:border-amber-500/30 bg-[#fff9ed]/82 dark:bg-amber-950/30 px-5 py-4 text-sm leading-6 text-slate-800 dark:text-amber-100 shadow-[0_18px_50px_rgba(183,121,31,0.08)]"
    >
      <span className="mr-3 inline-flex h-2 w-2 rounded-full bg-amber animate-pulse align-middle" />
      <strong className="font-semibold">{t("notice.draft")}</strong> {text}
    </motion.div>
  );
}

function CaseWorkspaceSection(context: Parameters<typeof renderSection>[1]) {
  type CaseWorkspaceTabId = (typeof caseWorkspaceStructure.primaryTabs)[number]["id"];
  const [activeTab, setActiveTab] = useState<CaseWorkspaceTabId>("overview");
  const packages = context.reviewPackages;
  const workload = summarizeWorkload(packages, context.packageResults);
  const queue = buildReviewQueue(packages, context.packageResults);
  const exportPack = context.riskDeltaExport;
  const readyCount = packages.filter((pkg) => pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK").length;
  const incompleteCount = packages.filter((pkg) => pkg.package_status === "INPUT_INCOMPLETE").length;

  return (
    <div className="space-y-6">
      <section className="premium-surface overflow-hidden rounded-[30px] border border-black/10 dark:border-white/10">
        <div className="grid gap-6 p-7 lg:grid-cols-[1.15fr_0.85fr] lg:p-9">
          <div>
            <h2 className="max-w-3xl text-4xl font-light leading-[1.05] tracking-[-0.055em] text-ink dark:text-white md:text-5xl">
              Ein Fall. Eine klare Arbeitsreihenfolge.
            </h2>
            <p className="mt-5 max-w-2xl text-base leading-8 text-slate-600 dark:text-slate-300">
              Diese Fallakte bündelt den gesamten Risiko-Delta-Prozess: Quellen prüfen,
              betroffene Risiken verstehen, Review-Aufwand priorisieren und am Ende ein
              Draft Review Pack erzeugen. Die technischen Module bleiben im Hintergrund.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => void context.generateReviewPackages()}
                className="inline-flex h-12 items-center gap-2 rounded-2xl bg-teal px-5 text-sm font-semibold text-white shadow-[0_20px_45px_rgba(0,155,141,0.22)]"
              >
                <PackageCheck className="h-4 w-4" />
                Prüfpakete erstellen
              </button>
              <Link
                href={riskOrchestrationEntry.reviewWorkbenchRoute}
                className="inline-flex h-12 items-center gap-2 rounded-2xl border border-black/10 bg-white/80 px-5 text-sm font-semibold text-ink shadow-sm hover:bg-white dark:border-white/10 dark:bg-slate-800/80 dark:text-white"
              >
                <ShieldCheck className="h-4 w-4" />
                Backend-Prüfmappe öffnen
              </Link>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <Stat label="Prüfpakete" value={packages.length || 5} tone="teal" />
            <Stat label="Bereit für Check" value={readyCount || 4} tone="teal" />
            <Stat label="Zurück an Author/Ops" value={incompleteCount || 1} tone="amber" />
            <Stat label="Geschätzte Reduktion" value={`${workload.estimated_reduction_percent || 65}%`} tone="danger" />
          </div>
        </div>
        <div className="border-t border-black/10 bg-white/55 px-5 py-4 dark:border-white/10 dark:bg-slate-800/55">
          <div className="flex gap-2 overflow-x-auto">
            {caseWorkspaceStructure.primaryTabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`min-w-fit rounded-2xl border px-4 py-3 text-left transition ${
                  activeTab === tab.id
                    ? "border-teal bg-teal text-white shadow-[0_14px_35px_rgba(0,155,141,0.18)]"
                    : "border-black/10 bg-white/80 text-slate-700 hover:bg-white dark:border-white/10 dark:bg-slate-900/50 dark:text-slate-200"
                }`}
              >
                <div className="text-sm font-semibold">{tab.label}</div>
                <div className={`mt-1 text-xs ${activeTab === tab.id ? "text-white/80" : "text-slate-500 dark:text-slate-400"}`}>
                  {tab.helper}
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {activeTab === "overview" ? <CaseOverviewTab packages={packages} workload={workload} /> : null}
      {activeTab === "sources" ? <CaseSourcesTab /> : null}
      {activeTab === "risk-deltas" ? <CaseRiskDeltasTab context={context} /> : null}
      {activeTab === "review-queue" ? <CaseReviewQueueTab queue={queue} packages={packages} onGenerate={context.generateReviewPackages} /> : null}
      {activeTab === "export" ? <CaseExportTab context={context} exportPack={exportPack} /> : null}
    </div>
  );
}

function CaseOverviewTab({
  packages,
  workload
}: {
  packages: ReviewPackage[];
  workload: ReturnType<typeof summarizeWorkload>;
}) {
  return (
    <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
      <Panel title="Wo steht der Fall?">
        <div className="space-y-4">
          {[
            ["1", "Unterlagen liegen vor", "Synthetischer AVI-Threshold-Change mit FMEA, SOP und Validierungsevidenz."],
            ["2", "Wichtigste Lücke ist sichtbar", "Validierung und Training decken die neue Schwelle noch nicht belastbar ab."],
            ["3", "Review wird priorisiert", "High/Critical- und Evidenzlücken gehen zuerst an SME/QA."],
            ["4", "Export bleibt Draft", "Das Lieferpaket ist prüfbar, aber keine regulatorische Entscheidung."]
          ].map(([step, title, text]) => (
            <div key={step} className="flex gap-4 rounded-2xl bg-slate-50 p-4 dark:bg-slate-800">
              <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-teal text-sm font-semibold text-white">{step}</span>
              <div>
                <div className="font-semibold tracking-[-0.02em]">{title}</div>
                <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{text}</p>
              </div>
            </div>
          ))}
        </div>
      </Panel>
      <Panel title="Risk Review Summary">
        <div className="grid gap-3 md:grid-cols-3">
          <Metric label="Total packages" value={String(packages.length || 5)} tone="teal" />
          <Metric label="Ready for review" value={String(workload.ready_for_review || 4)} tone="teal" />
          <Metric label="Input incomplete" value={String(workload.input_incomplete || 1)} />
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <SummaryBlock title="Manual baseline" text={`${workload.manual_baseline_hours || 10}.0 h geschätzter klassischer Vorbereitungsaufwand.`} />
          <SummaryBlock title="Assisted review" text={`${workload.assisted_review_hours || 3.5} h indikative MVP-Schätzung mit priorisierter Fallakte.`} />
        </div>
      </Panel>
    </div>
  );
}

function CaseSourcesTab() {
  return (
    <div className="space-y-6">
      <Panel title="Quellen, die den Fall tragen">
        <Table
          headers={["Dokument", "Typ", "Wofür relevant?"]}
          rows={demoDocuments.map((doc) => [doc.fileName, doc.documentType, `${doc.content.slice(0, 170)}...`])}
        />
      </Panel>
      <div className="grid gap-6 xl:grid-cols-2">
        <Panel title="Wichtige Quellenzitate">
          <Table
            headers={["Quelle", "Abschnitt", "Zitat"]}
            rows={demoSnippets.slice(0, 5).map((snippet) => [snippet.id, snippet.sectionTitle, snippet.text])}
          />
        </Panel>
        <Panel title="Regel-/Risikobibliothek">
          <Table
            headers={["Bibliothek", "Prozessschritt", "Risiko", "Status"]}
            rows={demoRiskLibrary.map((item) => [item.libraryId, item.processStep, item.failureMode, item.approvalStatus])}
          />
        </Panel>
      </div>
    </div>
  );
}

function CaseRiskDeltasTab({ context }: { context: Parameters<typeof renderSection>[1] }) {
  const packages = context.reviewPackages;
  if (packages.length === 0) {
    return (
      <Panel
        title="Risiko-Deltas vorbereiten"
        action={
          <button type="button" className="rounded-xl bg-teal px-4 py-2 text-sm font-semibold text-white" onClick={() => void context.generateReviewPackages()}>
            Prüfpakete erstellen
          </button>
        }
      >
        <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">
          Noch keine Pakete erzeugt. Starte hier den Package Builder. Danach siehst du pro Risiko:
          Quellen, Evidenzlinks, Lücken, Bibliotheksbasis, Baseline-FMEA und Plausibilitätsstatus.
        </p>
      </Panel>
    );
  }

  return (
    <div className="space-y-4">
      {packages.map((pkg) => {
        const result = context.packageResults[pkg.id];
        const canRun = pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK";
        return (
          <Panel
            key={pkg.id}
            title={`${pkg.risk_item_draft.risk_id}: ${pkg.risk_item_draft.failure_mode}`}
            action={
              <button
                type="button"
                disabled={!canRun}
                onClick={() => void context.runPackageReview(pkg.id)}
                className={`rounded-xl px-4 py-2 text-sm font-semibold ${
                  canRun ? "bg-ink text-white" : "cursor-not-allowed bg-slate-100 text-slate-400"
                }`}
              >
                Plausibilität prüfen
              </button>
            }
          >
            <div className="grid gap-4 md:grid-cols-4">
              <SummaryBlock title="Status" text={pkg.package_status} />
              <SummaryBlock title="Quellen" text={`${pkg.linked_source_snippets.length} verknüpfte Zitate`} />
              <SummaryBlock title="Lücken" text={pkg.documented_gaps.length ? pkg.documented_gaps.map((gap) => gap.priority).join(", ") : "Keine dokumentierte Lücke"} />
              <SummaryBlock title="Plausibilität" text={result ? `${result.overall_result} / ${result.evidence_quality}` : "Noch nicht geprüft"} />
            </div>
          </Panel>
        );
      })}
    </div>
  );
}

function CaseReviewQueueTab({
  queue,
  packages,
  onGenerate
}: {
  queue: ReviewQueueItem[];
  packages: ReviewPackage[];
  onGenerate: () => Promise<void>;
}) {
  if (packages.length === 0) {
    return (
      <Panel
        title="Review Queue"
        action={<button type="button" className="rounded-xl bg-teal px-4 py-2 text-sm font-semibold text-white" onClick={() => void onGenerate()}>Queue vorbereiten</button>}
      >
        <RiskRows items={reviewQueue} compact />
      </Panel>
    );
  }

  return (
    <Panel title="Priorisierte Review Queue">
      <div className="space-y-3">
        {queue.map((item) => (
          <QueueItemRow key={item.package_id} item={item} />
        ))}
      </div>
    </Panel>
  );
}

function CaseExportTab({
  context,
  exportPack
}: {
  context: Parameters<typeof renderSection>[1];
  exportPack: ReturnType<typeof generateRiskDeltaReviewPack> | null;
}) {
  return (
    <Panel
      title="Draft Risk Delta Review Pack"
      action={
        <button type="button" className="inline-flex h-10 items-center gap-2 rounded-xl bg-ink px-4 text-sm font-semibold text-white" onClick={context.generateDeltaExport}>
          <FileDown className="h-4 w-4" />
          Draft Export erzeugen
        </button>
      }
    >
      <div className="grid gap-4 md:grid-cols-3">
        <SummaryBlock title="Markdown" text="Lesbares Deliverable für Kundendemo und SME/QA-Review." />
        <SummaryBlock title="CSV" text="Tabellarische Risiko-Delta-Matrix für Excel." />
        <SummaryBlock title="JSON" text="Strukturierte Daten für spätere Integration." />
      </div>
      {exportPack ? (
        <pre className="mt-5 max-h-96 overflow-auto whitespace-pre-wrap rounded-md bg-slate-950 p-4 text-xs leading-5 text-slate-100">
          {exportPack.markdown}
        </pre>
      ) : (
        <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
          Erzeuge den Draft Export erst, wenn die Pakete erstellt und idealerweise plausibilisiert wurden.
          Der Export bleibt klar als Entwurf gekennzeichnet.
        </div>
      )}
    </Panel>
  );
}

function Panel({ title, children, action }: { title: string; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="premium-surface overflow-hidden rounded-[26px] border border-black/10 dark:border-white/10"
    >
      <div className="flex items-center justify-between border-b border-black/10 dark:border-white/10 px-6 py-5">
        <h2 className="text-base font-semibold tracking-[-0.025em] text-ink dark:text-white">{title}</h2>
        {action}
      </div>
      <div className="p-6">{children}</div>
    </motion.section>
  );
}

function Stat({ label, value, tone = "slate" }: { label: string; value: string | number; tone?: "slate" | "teal" | "amber" | "danger" }) {
  const toneClass = {
    slate: "text-slate-900 dark:text-slate-100",
    teal: "text-teal dark:text-teal-400",
    amber: "text-amber dark:text-amber-400",
    danger: "text-danger dark:text-red-400"
  }[tone];
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -4, boxShadow: "0 20px 50px rgba(17,24,29,0.08)" }}
      transition={{ duration: 0.2 }}
      className="rounded-[22px] border border-black/10 dark:border-white/10 bg-white/88 dark:bg-slate-800/88 px-6 py-5 shadow-[0_16px_45px_rgba(17,24,29,0.045)] dark:shadow-[0_16px_45px_rgba(0,0,0,0.2)] cursor-default"
    >
      <motion.div
        key={value}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`text-4xl font-light tracking-[-0.07em] ${toneClass}`}
      >
        {value}
      </motion.div>
      <div className="mt-3 text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-600 dark:text-slate-400">{label}</div>
    </motion.div>
  );
}

function DashboardSection(context: Parameters<typeof renderSection>[1]) {
  const { t } = useI18n();
  return (
    <div className="space-y-6">
      <div className="grid gap-3 md:grid-cols-4">
        <Stat label={t("dashboard.openHighGaps")} value={demoGaps.filter((gap) => gap.status === "OPEN" && ["HIGH", "CRITICAL"].includes(gap.priority)).length} tone="danger" />
        <Stat label={t("dashboard.level3Review")} value={demoRiskItems.filter((item) => item.reviewLevel === 3).length} tone="amber" />
        <Stat label={t("dashboard.aiDraftItems")} value={demoRiskItems.filter((item) => item.status === "AI_DRAFT").length} tone="teal" />
        <Stat label={t("dashboard.sourceSnippets")} value={demoSnippets.length} />
      </div>
      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel
          title={t("dashboard.riskBasedQueue")}
          action={<Link className="text-sm font-medium text-teal dark:text-teal-400" href="/review-queue">{t("dashboard.openQueue")}</Link>}
        >
          <RiskRows items={reviewQueue.slice(0, 4)} compact />
        </Panel>
      </div>
      <Panel title={t("dashboard.deltaSummary")}>
        <div className="grid gap-4 md:grid-cols-3">
          <SummaryBlock title={t("dashboard.trigger")} text={t("dashboard.triggerText")} />
          <SummaryBlock title={t("dashboard.mainConcern")} text={t("dashboard.mainConcernText")} />
          <SummaryBlock title={t("dashboard.routing")} text={t("dashboard.routingText")} />
        </div>
      </Panel>
    </div>
  );
}

function SummaryBlock({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-600 dark:text-slate-300">{title}</div>
      <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-400">{text}</p>
    </div>
  );
}

function PremiumReviewHero({
  packages,
  workload,
  onGenerate,
  onRunAll
}: {
  packages: ReviewPackage[];
  workload: ReturnType<typeof summarizeWorkload>;
  onGenerate: () => void;
  onRunAll: () => void;
}) {
  const { t } = useI18n();
  return (
    <section className="premium-surface relative overflow-hidden rounded-[32px] border border-black/10 dark:border-white/10">
      <div className="absolute right-0 top-0 hidden h-full w-[38%] xl:block">
        <LabInspectionVisual />
      </div>
      <div className="relative grid min-h-[390px] gap-8 p-7 md:p-10 xl:grid-cols-[0.65fr_0.35fr]">
        <div className="flex flex-col justify-between">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.28em] text-teal">{t("premium.reviewPackages")}</div>
            <h2 className="mt-7 pr-4 text-5xl font-light leading-[1.02] tracking-[-0.055em] text-ink dark:text-white md:text-6xl">
              {t("premium.headline")}
            </h2>
            <p className="mt-6 max-w-xl text-base leading-8 text-slate-600 dark:text-slate-300">
              {t("premium.subline")}
            </p>
          </div>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <button
              type="button"
              className="inline-flex h-12 items-center gap-2 rounded-2xl bg-teal px-5 text-sm font-semibold text-white shadow-[0_20px_45px_rgba(0,155,141,0.22)]"
              onClick={onGenerate}
            >
              <PackageCheck className="h-4 w-4" aria-hidden />
              {t("premium.generatePackages")}
            </button>
            <button
              type="button"
              className="inline-flex h-12 items-center gap-2 rounded-2xl border border-black/10 dark:border-white/10 bg-white/80 dark:bg-slate-800/80 px-5 text-sm font-semibold text-ink dark:text-white shadow-sm disabled:cursor-not-allowed disabled:text-slate-400"
              disabled={packages.length === 0}
              onClick={onRunAll}
            >
              <Play className="h-4 w-4" aria-hidden />
              {t("premium.runAllChecks")}
            </button>
            <span className="text-xs leading-5 text-slate-600 dark:text-slate-400">{t("premium.draftNote")}</span>
          </div>
        </div>
        <div className="hidden xl:block" />
      </div>
      <div className="border-t border-black/10 dark:border-white/10 bg-white/55 dark:bg-slate-800/55 px-7 py-5 backdrop-blur md:px-10">
        {packages.length > 0 ? (
          <div className="grid gap-3 md:grid-cols-3">
            <Stat label={t("review.generatedPackages")} value={workload.total_packages} />
            <Stat label={t("review.readyForReview")} value={workload.ready_for_review} tone="teal" />
            <Stat label={t("review.inputIncomplete")} value={workload.input_incomplete} tone="amber" />
          </div>
        ) : (
          <div className="grid gap-5 md:grid-cols-3">
            <SummaryBlock title={t("premium.architecture")} text={t("premium.architectureText")} />
            <SummaryBlock title={t("premium.completenessGate")} text={t("premium.completenessText")} />
            <SummaryBlock title={t("premium.demoScenario")} text={t("premium.demoText")} />
          </div>
        )}
      </div>
    </section>
  );
}

function LabInspectionLabel() {
  const { t } = useI18n();
  return (
    <div className="absolute bottom-8 left-10 max-w-52 text-[10px] font-semibold uppercase leading-5 tracking-[0.22em] text-slate-600">
      {t("premium.sterileNote")}
    </div>
  );
}

function LabInspectionVisual() {
  const vials = Array.from({ length: 9 }, (_, index) => index);
  return (
    <div className="relative h-full overflow-hidden border-l border-black/10 bg-[#eaf0ef]">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.96),transparent_24rem),linear-gradient(120deg,rgba(247,248,246,0.15),rgba(17,24,29,0.16))]" />
      <div className="lab-metal absolute right-8 top-0 h-24 w-[72%] rounded-b-[28px] opacity-95 shadow-[0_24px_60px_rgba(17,24,29,0.18)]" />
      <div className="lab-metal absolute right-20 top-20 h-36 w-12 rounded-b-2xl shadow-[0_18px_40px_rgba(17,24,29,0.2)]" />
      <div className="lab-metal absolute right-32 top-24 h-24 w-8 rounded-b-xl shadow-[0_12px_30px_rgba(17,24,29,0.18)]" />
      <div className="absolute bottom-24 right-0 h-16 w-[92%] rounded-l-full border border-white/70 bg-white/38 backdrop-blur-xl" />
      <div className="absolute bottom-24 right-8 flex items-end gap-4">
        {vials.map((vial) => (
          <div key={vial} className="relative h-28 w-10 rounded-b-2xl rounded-t-lg border border-white/75 bg-white/24 shadow-[inset_0_0_18px_rgba(255,255,255,0.85),0_18px_30px_rgba(17,24,29,0.08)] backdrop-blur">
            <div className="absolute -top-4 left-1/2 h-5 w-7 -translate-x-1/2 rounded-md border border-white/80 bg-white/50" />
            <div className="absolute bottom-0 h-10 w-full rounded-b-2xl bg-teal/10" />
          </div>
        ))}
      </div>
      <LabInspectionLabel />
    </div>
  );
}

function ExecutiveRiskSummary({ packages, results }: { packages: ReviewPackage[]; results: Record<string, PackageReviewResult> }) {
  const workload = summarizeWorkload(packages, results);
  const { t } = useI18n();
  return (
    <section className="grid gap-6 xl:grid-cols-[1fr_360px]">
      <div className="premium-surface overflow-hidden rounded-[30px] border border-black/10 dark:border-white/10">
        <div className="border-b border-black/10 dark:border-white/10 px-7 py-5">
          <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-600 dark:text-slate-400">{t("executive.reviewSummary")}</div>
        </div>
        <div className="grid grid-cols-2 gap-0 border-b border-black/10 dark:border-white/10 md:grid-cols-6">
          <MetricStripItem label={t("executive.total")} value={workload.total_packages} />
          <MetricStripItem label={t("executive.ready")} value={workload.ready_for_review} tone="teal" />
          <MetricStripItem label={t("executive.incomplete")} value={workload.input_incomplete} tone="amber" />
          <MetricStripItem label={t("executive.pass")} value={workload.plausibility_pass} tone="teal" />
          <MetricStripItem label={t("executive.partial")} value={workload.plausibility_partial} tone="amber" />
          <MetricStripItem label={t("executive.fail")} value={workload.plausibility_fail} tone="danger" />
        </div>
        <div className="grid gap-0 lg:grid-cols-[330px_1fr]">
          <div className="border-b border-black/10 dark:border-white/10 p-7 lg:border-b-0 lg:border-r">
            <GaugeMetric label={t("executive.reduction")} value={workload.estimated_reduction_percent} max={100} suffix="%" tone="teal" large />
          </div>
          <div className="grid gap-5 p-7 md:grid-cols-2">
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-600 dark:text-slate-400">{t("executive.manualBaseline")}</div>
              <div className="mt-5 text-5xl font-light tracking-[-0.07em] dark:text-white">{workload.manual_baseline_hours.toFixed(1)}h</div>
              <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-300">{t("executive.manualBaselineDesc")}</p>
            </div>
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-600 dark:text-slate-400">{t("executive.assistedReview")}</div>
              <div className="mt-5 text-5xl font-light tracking-[-0.07em] text-teal">{workload.assisted_review_hours.toFixed(1)}h</div>
              <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-300">{t("executive.assistedReviewDesc")}</p>
            </div>
          </div>
        </div>
      </div>
      <EvidenceConfidencePanel packages={packages} results={results} />
    </section>
  );
}

function MetricStripItem({ label, value, tone = "slate" }: { label: string; value: number; tone?: "slate" | "teal" | "amber" | "danger" }) {
  const color = {
    slate: "text-ink dark:text-white",
    teal: "text-teal",
    amber: "text-amber",
    danger: "text-danger"
  }[tone];
  return (
    <div className="border-r border-black/10 dark:border-white/10 px-6 py-6 last:border-r-0">
      <div className="text-sm text-slate-600 dark:text-slate-400">{label}</div>
      <div className={`mt-3 text-5xl font-light tracking-[-0.08em] ${color}`}>{value}</div>
    </div>
  );
}

function EvidenceConfidencePanel({ packages, results }: { packages: ReviewPackage[]; results: Record<string, PackageReviewResult> }) {
  const { t } = useI18n();
  const totalEvidence = packages.reduce((sum, pkg) => sum + pkg.evidence_links.length, 0);
  const totalGaps = packages.reduce((sum, pkg) => sum + pkg.documented_gaps.length + pkg.missing_inputs.length, 0);
  const checked = Object.keys(results).length;
  const bars = [
    [t("evidence.sourceCoverage"), packages.length ? Math.round(((packages.length - 1) / packages.length) * 100) : 0],
    [t("evidence.plausibilityChecked"), packages.length ? Math.round((checked / packages.length) * 100) : 0],
    [t("evidence.evidenceLinked"), packages.length ? Math.min(100, totalEvidence * 14) : 0],
    [t("evidence.openGapsVisible"), packages.length ? Math.min(100, totalGaps * 18) : 0]
  ] as const;
  return (
    <aside className="premium-surface rounded-[30px] border border-black/10 dark:border-white/10 p-7">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-600 dark:text-slate-400">{t("evidence.confidence")}</div>
          <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{t("evidence.confidenceDesc")}</p>
        </div>
        <ShieldCheck className="h-5 w-5 text-teal" />
      </div>
      <div className="mt-7 space-y-5">
        {bars.map(([label, value]) => (
          <div key={label}>
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="text-slate-700 dark:text-slate-300">{label}</span>
              <span className="font-medium text-ink dark:text-white">{value}%</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
              <div className="h-full rounded-full bg-teal" style={{ width: `${value}%` }} />
            </div>
          </div>
        ))}
      </div>
      <div className="mt-8 grid grid-cols-2 gap-3">
        <div className="rounded-2xl border border-black/10 dark:border-white/10 bg-white/70 dark:bg-slate-800/70 p-4">
          <div className="text-3xl font-light tracking-[-0.06em] dark:text-white">{totalEvidence}</div>
          <div className="mt-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600 dark:text-slate-400">{t("evidence.evidenceLinks")}</div>
        </div>
        <div className="rounded-2xl border border-black/10 dark:border-white/10 bg-white/70 dark:bg-slate-800/70 p-4">
          <div className="text-3xl font-light tracking-[-0.06em] text-amber">{totalGaps}</div>
          <div className="mt-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600 dark:text-slate-400">{t("evidence.gapsInputs")}</div>
        </div>
      </div>
    </aside>
  );
}

// Progress Wizard for Review Flow
function ReviewProgressWizard({ currentStep }: { currentStep: number }) {
  const { t } = useI18n();
  const steps = [
    { label: t("wizard.generate"), description: t("wizard.generateDesc"), icon: PackageCheck },
    { label: t("wizard.plausibility"), description: t("wizard.plausibilityDesc"), icon: CheckCircle2 },
    { label: t("wizard.smeReview"), description: t("wizard.smeDesc"), icon: Users },
    { label: t("wizard.qaApproval"), description: t("wizard.qaDesc"), icon: ShieldCheck },
    { label: t("wizard.export"), description: t("wizard.exportDesc"), icon: FileDown },
  ];

  return (
    <div className="mb-8 overflow-hidden rounded-2xl border border-black/10 dark:border-white/10 bg-white/80 dark:bg-slate-800/80 p-6 shadow-sm" role="navigation" aria-label={t("wizard.navigation")}>
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.label} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-full transition-all duration-300 ${
                  index < currentStep
                    ? "bg-teal-500 text-white shadow-[0_8px_20px_rgba(0,155,141,0.3)]"
                    : index === currentStep
                    ? "bg-teal-500/15 text-teal-600 ring-2 ring-teal-500"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-400"
                }`}
                aria-current={index === currentStep ? "step" : undefined}
              >
                {index < currentStep ? (
                  <CheckCircle2 className="h-5 w-5" aria-hidden />
                ) : (
                  <step.icon className="h-5 w-5" aria-hidden />
                )}
              </div>
              <div className="mt-2 text-center">
                <div className={`text-xs font-semibold ${index <= currentStep ? "text-slate-800 dark:text-white" : "text-slate-400"}`}>
                  {step.label}
                </div>
                <div className="hidden text-[10px] text-slate-600 dark:text-slate-400 sm:block">{step.description}</div>
              </div>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`mx-2 h-0.5 w-8 sm:w-12 md:w-16 lg:w-20 transition-colors duration-300 ${
                  index < currentStep ? "bg-teal-500" : "bg-slate-200 dark:bg-slate-700"
                }`}
                aria-hidden
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function ProjectsSection() {
  const { t, locale } = useI18n();
  const placeholders = locale === "de"
    ? ["Projektname", "Produkt/Prozess/System", "GMP-Bereich", "Geltungsbereich", "Außerhalb Geltungsbereich"]
    : ["Project name", "Product/process/system", "GMP area", "Scope statement", "Out-of-scope statement"];
  return (
    <Panel title={t("projects.title")}>
      <div className="grid gap-4 lg:grid-cols-[1fr_0.8fr]">
        <Link href={`/projects/${demoProject.id}`} className="block rounded-lg border border-line dark:border-white/10 p-4 hover:bg-slate-50 dark:hover:bg-slate-800">
          <div className="text-lg font-semibold dark:text-white">{demoProject.name}</div>
          <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{demoProject.scopeStatement}</p>
          <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-600 dark:text-slate-400">
            <span className="rounded bg-slate-100 dark:bg-slate-700 px-2 py-1">{demoProject.gmpArea}</span>
            <span className="rounded bg-slate-100 dark:bg-slate-700 px-2 py-1">{demoProject.methodology}</span>
            <span className="rounded bg-slate-100 dark:bg-slate-700 px-2 py-1">{demoProject.triggerType}</span>
          </div>
        </Link>
        <form className="grid gap-3 rounded-lg border border-line dark:border-white/10 p-4">
          <div className="font-semibold dark:text-white">{t("projects.createProject")}</div>
          {placeholders.map((label) => (
            <input key={label} className="h-9 rounded-md border border-line dark:border-white/10 dark:bg-slate-800 dark:text-white px-3 text-sm" placeholder={label} />
          ))}
          <button type="button" className="h-9 rounded-md bg-teal px-3 text-sm font-medium text-white">{t("projects.createDraft")}</button>
        </form>
      </div>
    </Panel>
  );
}

function ProjectDetail({ id }: { id: string }) {
  return (
    <div className="space-y-6">
      <Panel title={`Project detail: ${id}`}>
        <dl className="grid gap-4 md:grid-cols-2">
          {Object.entries({
            "Product/process/system": demoProject.productProcessSystem,
            "GMP area": demoProject.gmpArea,
            Scope: demoProject.scopeStatement,
            "Out of scope": demoProject.outOfScopeStatement,
            "Trigger type": demoProject.triggerType,
            "QRM methodology": demoProject.methodology,
            "Scoring model": demoProject.scoringModel,
            "Required QA approver": demoProject.requiredQaApprover
          }).map(([key, value]) => (
            <div key={key}>
              <dt className="text-xs uppercase tracking-[0.08em] text-slate-600">{key}</dt>
              <dd className="mt-1 text-sm leading-6 text-slate-800">{value}</dd>
            </div>
          ))}
        </dl>
      </Panel>
      <DashboardSection {...({ exportDraft: exportPackage({ project: demoProject, riskItems: demoRiskItems, gaps: demoGaps, approvedPackage: false }), approvedStyleExport: exportPackage({ project: demoProject, riskItems: demoRiskItems, gaps: demoGaps, approvedPackage: true }), role: "QRM_AUTHOR", reviewPackages: [], packageResults: {}, generateReviewPackages: async () => undefined, runPackageReview: async () => undefined, runAllPackageReviews: async () => undefined, generateDeltaExport: () => undefined, riskDeltaExport: null, multiAgentState: "idle", multiAgentResult: null, multiAgentError: null, runMultiAgentAnalysis: async () => undefined, uploadedDocuments: [], setUploadedDocuments: () => undefined } as Parameters<typeof renderSection>[1])} />
    </div>
  );
}

function DocumentsSection() {
  const { t } = useI18n();
  return (
    <Panel title={t("docs.sourceDocuments")}>
      <Table
        headers={[t("docs.documentType"), t("docs.fileName"), t("docs.supportedFormat"), t("docs.contentExcerpt")]}
        rows={demoDocuments.map((document) => [document.documentType, document.fileName, document.fileName.split(".").pop(), document.content])}
      />
      <div className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-400">{t("docs.todoPlaceholder")}</div>
    </Panel>
  );
}

function SnippetsSection() {
  const { t } = useI18n();
  return (
    <Panel title={t("snippets.title")}>
      <Table
        headers={[t("snippets.snippet"), t("snippets.document"), t("snippets.section"), t("snippets.lineRef"), t("snippets.hash")]}
        rows={demoSnippets.map((snippet) => [snippet.id, snippet.documentType, snippet.sectionTitle, snippet.lineReference, snippet.snippetHash.slice(0, 16)])}
      />
    </Panel>
  );
}

function RiskLibrarySection() {
  const { t } = useI18n();
  return (
    <Panel title={t("riskLib.title")}>
      <Table
        headers={[t("riskLib.libraryId"), t("riskLib.gmpArea"), t("riskLib.processStep"), t("riskLib.failureMode"), t("riskLib.status"), t("riskLib.version"), t("riskLib.sme")]}
        rows={demoRiskLibrary.map((item) => [
          item.libraryId,
          item.gmpArea,
          item.processStep,
          item.failureMode,
          item.approvalStatus,
          item.version,
          item.requiredSmeDiscipline
        ])}
      />
      <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-400">{t("riskLib.note")}</p>
    </Panel>
  );
}

function TriggerSection() {
  const { t } = useI18n();
  return (
    <Panel title={t("trigger.title")}>
      <div className="grid gap-4 md:grid-cols-2">
        <SummaryBlock title={t("trigger.changeControl")} text={t("trigger.changeText")} />
        <SummaryBlock title={t("trigger.deviation")} text={t("trigger.deviationText")} />
        <SummaryBlock title={t("trigger.capa")} text={t("trigger.capaText")} />
        <SummaryBlock title={t("trigger.auditFinding")} text={t("trigger.auditText")} />
      </div>
    </Panel>
  );
}

function DeltaSection() {
  const { locale } = useI18n();
  const isGerman = locale === "de";
  const copy = isGerman
    ? {
        eyebrow: "Neuer Kernprozess",
        badge: "Ersetzt die bisherige Delta-Analyse",
        title: "Aus Dokumenten wird eine prüfbare Risikomappe.",
        description:
          "Der neue Pfad zeigt nicht mehr nur eine KI-Auswertung. Er sammelt Quellen, prüft Anforderungen, markiert Lücken und erzeugt ein kompaktes Review Pack für SME, QA oder Regulatory.",
        primary: "Prüfmappe öffnen",
        secondary: "Demo-Pakete ansehen",
        decisionSupport: "Decision Support",
        noVoting: "Keine Modell-Abstimmung",
        evidenceFirst: "Quellenpflicht",
        humanControl: "Entscheidung beim Menschen",
        architectureTitle: "Was passiert in diesem Schritt?",
        architectureText:
          "Die frühere Delta-Analyse ist jetzt der Einstieg in die Pipeline: Unterlagen rein, zitierte Prüfpunkte und offene Fragen raus.",
        safetyTitle: "Warum das für Consultants wichtig ist",
        safetyText:
          "Das System reduziert Such- und Sortieraufwand. Es trifft keine regulatorischen Entscheidungen, sondern zeigt, wo der Mensch gezielt prüfen muss.",
        routesTitle: "Was du testen solltest",
        routeReviewUi: "Neue Prüfmappen-UI",
        routeReviewUiText: "Prüfpaket öffnen, Quellenzitate ansehen und Review-Entscheidungen erfassen.",
        routeReviewPackages: "Demo-Cockpit",
        routeReviewPackagesText: "Zeigt Review Queue, Quellenkarte, Arbeitsaufwand und Draft Export für den synthetischen Fall.",
        routeBackend: "Backend-Pipeline",
        routeBackendText: "FastAPI verarbeitet Upload, Requirements, Claims, Reviewer, Verifier, Risk Fusion und Audit Trail."
      }
    : {
        eyebrow: "New core workflow",
        badge: "Replaces the previous Delta Analysis",
        title: "Risk orchestration instead of model voting.",
        description:
          "The new path analyzes documents backend-first, builds a cited claim ledger, checks versioned requirements, verifies findings, and creates review packs for human QA and Regulatory review.",
        primary: "Open Review Workbench",
        secondary: "View synthetic demo packages",
        decisionSupport: "Decision Support",
        noVoting: "No majority voting",
        evidenceFirst: "Evidence obligation",
        humanControl: "Human Review",
        architectureTitle: "Integrated orchestration flow",
        architectureText:
          "The old Delta Analysis is no longer the main process. It is now the entry into this pipeline: documents in, source-based claims and findings out, review pack for humans.",
        safetyTitle: "Why this fits better",
        safetyText:
          "The system does not make regulatory decisions by itself. It blocks incomplete inputs, conservatively escalates High/Critical risks, and shows only cited claims with document ID, page, chunk, and quote.",
        routesTitle: "What to test",
        routeReviewUi: "New backend review UI",
        routeReviewUiText: "Open DocumentSets, inspect Review Packs, and capture reviewer decisions.",
        routeReviewPackages: "Old frontend demo",
        routeReviewPackagesText: "Kept as a synthetic demo for packages, queue, evidence map, and export.",
        routeBackend: "Backend pipeline",
        routeBackendText: "FastAPI handles upload, requirements, claims, reviewers, verifier, risk fusion, and audit trail."
      };

  const workflow = isGerman
    ? [
        "Demo-Fall oder Kundendokumente bereitstellen",
        "Quellen und Anforderungen prüfen lassen",
        "Prüfpunkte mit Zitaten erzeugen",
        "Plausibilität und Lücken prüfen",
        "Review Pack für SME/QA öffnen"
      ]
    : [
        "Provide demo case or customer documents",
        "Check sources and requirements",
        "Create cited review points",
        "Check plausibility and gaps",
        "Open review pack for SME/QA"
      ];

  return (
    <div className="space-y-6">
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="premium-surface relative overflow-hidden rounded-[32px] border border-black/10 dark:border-white/10"
      >
        <div className="absolute right-0 top-0 hidden h-full w-[40%] bg-gradient-to-l from-teal-500/10 to-transparent lg:block" />
        <div className="relative grid gap-8 p-8 md:p-10 xl:grid-cols-[1.1fr_0.9fr]">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-teal-500/20 bg-teal-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-teal-700 dark:text-teal-300">
              <Brain className="h-3.5 w-3.5" />
              {copy.eyebrow}
            </div>
            <h2 className="mt-6 max-w-3xl text-5xl font-light leading-[1.02] tracking-[-0.055em] text-ink dark:text-white md:text-6xl">
              {copy.title}
            </h2>
            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-600 dark:text-slate-300">
              {copy.description}
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link
                href={riskOrchestrationEntry.reviewWorkbenchRoute}
                className="inline-flex h-12 items-center gap-2 rounded-2xl bg-teal px-5 text-sm font-semibold text-white shadow-[0_20px_45px_rgba(0,155,141,0.22)]"
              >
                <PackageCheck className="h-5 w-5" />
                {copy.primary}
              </Link>
              <Link
                href="/review-packages"
                className="inline-flex h-12 items-center gap-2 rounded-2xl border border-black/10 bg-white/80 px-5 text-sm font-semibold text-ink shadow-sm hover:bg-white dark:border-white/10 dark:bg-slate-800/80 dark:text-white dark:hover:bg-slate-700"
              >
                <FileDown className="h-5 w-5" />
                {copy.secondary}
              </Link>
            </div>
          </div>

          <div className="rounded-[26px] border border-black/10 bg-white/72 p-5 shadow-[0_18px_55px_rgba(17,24,29,0.06)] dark:border-white/10 dark:bg-slate-800/72">
            <div className="mb-4 flex items-center justify-between gap-3">
              <Badge tone="slate">{copy.badge}</Badge>
              <span className="text-xs font-semibold text-teal-700 dark:text-teal-300">{riskOrchestrationEntry.name}</span>
            </div>
            <div className="space-y-3">
              {workflow.map((step, index) => (
                <div key={step} className="flex items-start gap-3 rounded-2xl border border-black/5 bg-white/70 p-3 dark:border-white/10 dark:bg-slate-900/35">
                  <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-teal-500 text-xs font-semibold text-white">
                    {index + 1}
                  </span>
                  <span className="text-sm leading-6 text-slate-700 dark:text-slate-300">{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.section>

      <div className="grid gap-4 md:grid-cols-4">
        <Stat label={copy.decisionSupport} value="Human" tone="teal" />
        <Stat label={copy.noVoting} value="0" tone="danger" />
        <Stat label={copy.evidenceFirst} value="100%" tone="teal" />
        <Stat label={copy.humanControl} value="QA/SME" tone="amber" />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Panel title={copy.architectureTitle}>
          <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">{copy.architectureText}</p>
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <SummaryBlock
              title={isGerman ? "Aussagen-Liste" : "Claim Ledger"}
              text={isGerman ? "Jede Aussage braucht Quelle, Seite, Chunk, Zitat und eine nachvollziehbare Herkunft." : "Claims need quote, document ID, page, chunk ID, confidence, model and prompt version."}
            />
            <SummaryBlock
              title={isGerman ? "Prüf-Gates" : "Verifier Gates"}
              text={isGerman ? "Zitate, passende Requirements, Parserqualität und Abdeckung werden geprüft, bevor etwas in den Review geht." : "Citations, Requirement applicability, parser quality, OOD and coverage are checked before review routing."}
            />
            <SummaryBlock
              title={isGerman ? "Review Pack" : "Review Pack"}
              text={isGerman ? "Menschen erhalten ein kurzes Dossier mit Top-Risiken, Quellen, Modellpositionen und Audit-Referenzen." : "Humans receive a compact dossier with top risks, evidence table, model positions and audit references."}
            />
          </div>
        </Panel>

        <Panel title={copy.safetyTitle}>
          <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">{copy.safetyText}</p>
          <div className="mt-5 grid gap-3">
            <div className="flex items-start gap-3 rounded-2xl bg-slate-50 p-4 dark:bg-slate-800">
              <AlertTriangle className="mt-0.5 h-5 w-5 text-amber" />
              <div className="text-sm leading-6 text-slate-700 dark:text-slate-300">
                {isGerman
                  ? "Unvollständige Eingaben, Parserprobleme, fehlende Abdeckung und schwache Evidenz führen zu menschlicher Aktion, nicht zu stiller Entwarnung."
                  : "Input incomplete, parser problems, missing coverage and weak evidence route to human action, not to silent clearance."}
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-2xl bg-slate-50 p-4 dark:bg-slate-800">
              <ShieldCheck className="mt-0.5 h-5 w-5 text-teal" />
              <div className="text-sm leading-6 text-slate-700 dark:text-slate-300">
                {isGerman
                  ? "Modell, Prompt, RequirementSet und Orchestrierungsversion werden im Audit Trail nachvollziehbar gehalten."
                  : "Model, prompt, RequirementSet and orchestration versions are part of the audit trail."}
              </div>
            </div>
          </div>
        </Panel>
      </div>

      <Panel title={copy.routesTitle}>
        <div className="grid gap-4 md:grid-cols-3">
          <Link href={riskOrchestrationEntry.reviewWorkbenchRoute} className="rounded-[22px] border border-black/10 bg-white/78 p-5 transition hover:-translate-y-0.5 hover:bg-white dark:border-white/10 dark:bg-slate-800/78">
            <PackageCheck className="h-5 w-5 text-teal" />
            <h3 className="mt-4 font-semibold text-ink dark:text-white">{copy.routeReviewUi}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">{copy.routeReviewUiText}</p>
          </Link>
          <Link href="/review-packages" className="rounded-[22px] border border-black/10 bg-white/78 p-5 transition hover:-translate-y-0.5 hover:bg-white dark:border-white/10 dark:bg-slate-800/78">
            <ClipboardCheck className="h-5 w-5 text-teal" />
            <h3 className="mt-4 font-semibold text-ink dark:text-white">{copy.routeReviewPackages}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">{copy.routeReviewPackagesText}</p>
          </Link>
          <Link href="http://localhost:8000/docs" className="rounded-[22px] border border-black/10 bg-white/78 p-5 transition hover:-translate-y-0.5 hover:bg-white dark:border-white/10 dark:bg-slate-800/78">
            <Database className="h-5 w-5 text-teal" />
            <h3 className="mt-4 font-semibold text-ink dark:text-white">{copy.routeBackend}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">{copy.routeBackendText}</p>
          </Link>
        </div>
      </Panel>
    </div>
  );
}

// Agent Card Component
function AgentCard({
  name,
  model,
  role,
  description,
  icon,
  status,
  color,
}: {
  name: string;
  model: string;
  role: string;
  description: string;
  icon: React.ReactNode;
  status: "idle" | "active" | "done";
  color: "blue" | "purple" | "teal";
}) {
  const colorClasses = {
    blue: {
      bg: "bg-blue-500/10 dark:bg-blue-500/20",
      border: "border-blue-500/20 dark:border-blue-400/30",
      icon: "text-blue-600 dark:text-blue-400",
      ring: status === "active" ? "ring-2 ring-blue-500 ring-offset-2 dark:ring-offset-slate-900" : "",
    },
    purple: {
      bg: "bg-purple-500/10 dark:bg-purple-500/20",
      border: "border-purple-500/20 dark:border-purple-400/30",
      icon: "text-purple-600 dark:text-purple-400",
      ring: status === "active" ? "ring-2 ring-purple-500 ring-offset-2 dark:ring-offset-slate-900" : "",
    },
    teal: {
      bg: "bg-teal-500/10 dark:bg-teal-500/20",
      border: "border-teal-500/20 dark:border-teal-400/30",
      icon: "text-teal-600 dark:text-teal-400",
      ring: status === "active" ? "ring-2 ring-teal-500 ring-offset-2 dark:ring-offset-slate-900" : "",
    },
  };

  const c = colorClasses[color];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3 }}
      className={`relative rounded-2xl border ${c.border} ${c.bg} p-5 transition-all ${c.ring}`}
    >
      <AnimatePresence>
        {status === "active" && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center"
          >
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-teal-400 opacity-75" />
            <span className="relative inline-flex h-3 w-3 rounded-full bg-teal-500" />
          </motion.div>
        )}
        {status === "done" && (
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            className="absolute -right-1 -top-1"
          >
            <CheckCircle2 className="h-5 w-5 text-teal-500" />
          </motion.div>
        )}
      </AnimatePresence>
      <div className={`inline-flex h-10 w-10 items-center justify-center rounded-xl ${c.bg} ${c.icon}`}>
        {icon}
      </div>
      <div className="mt-4">
        <div className="font-semibold text-slate-900 dark:text-white">{name}</div>
        <div className="text-xs text-slate-600 dark:text-slate-400">{model} • {role}</div>
      </div>
      <p className="mt-2 text-sm leading-5 text-slate-600 dark:text-slate-300">{description}</p>
    </motion.div>
  );
}

// Agent Message Bubble
function AgentMessageBubble({ message }: { message: AgentMessage }) {
  const roleConfig = {
    AUTHOR: { label: "Author (GPT-4o)", color: "bg-blue-500", icon: <Bot className="h-4 w-4" /> },
    CRITIC: { label: "Critic (Claude)", color: "bg-purple-500", icon: <MessageCircle className="h-4 w-4" /> },
    RESOLVER: { label: "Resolver (GPT-4o)", color: "bg-teal-500", icon: <Zap className="h-4 w-4" /> },
  };

  const config = roleConfig[message.role];

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex gap-4 p-4 rounded-xl bg-white/50 dark:bg-slate-800/50 border border-black/5 dark:border-white/5"
    >
      <motion.div
        whileHover={{ scale: 1.1 }}
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${config.color} text-white shadow-lg`}
      >
        {config.icon}
      </motion.div>
      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-semibold text-slate-900 dark:text-white">{config.label}</span>
          <span className="text-xs text-slate-500 dark:text-slate-400">{new Date(message.timestamp).toLocaleTimeString()}</span>
          <span className="text-xs text-slate-500 dark:text-slate-400">• {message.tokenUsage.totalTokens} tokens</span>
        </div>
        <p className="mt-1 text-sm leading-6 text-slate-700 dark:text-slate-300">{message.content}</p>
      </div>
    </motion.div>
  );
}

function ReviewPackagesSection(context: Parameters<typeof renderSection>[1]) {
  const { t } = useI18n();
  const packages = context.reviewPackages;
  const [queueFilter, setQueueFilter] = useState("All");
  const queue = buildReviewQueue(packages, context.packageResults);
  const filteredQueue = queue.filter((item) => queueFilter === "All" || queueFilterMatch(item, queueFilter));
  const workload = summarizeWorkload(packages, context.packageResults);
  const exportPack = context.riskDeltaExport;
  const queueFilters = [
    { value: "All", label: "Alle" },
    { value: "Input incomplete", label: "Unvollständig" },
    { value: "Ready for plausibility check", label: "Bereit für Quellencheck" },
    { value: "SME required", label: "SME erforderlich" },
    { value: "QA required", label: "QA erforderlich" },
    { value: "Evidence gaps", label: "Evidenzlücken" },
    { value: "High priority", label: "Hohe Priorität" },
    { value: "Quick check only", label: "Nur Schnellcheck" }
  ];

  // Calculate current step for progress wizard
  const currentStep = useMemo(() => {
    if (packages.length === 0) return 0;
    const hasPlausibilityResults = Object.keys(context.packageResults).length > 0;
    const allChecked = packages.every(pkg => context.packageResults[pkg.id]);
    const hasExport = exportPack !== null;

    if (hasExport) return 4;
    if (allChecked) return 3;
    if (hasPlausibilityResults) return 2;
    if (packages.length > 0) return 1;
    return 0;
  }, [packages, context.packageResults, exportPack]);

  return (
    <div className="space-y-7">
      {/* Progress Wizard */}
      <ReviewProgressWizard currentStep={currentStep} />

      <PremiumReviewHero
        packages={packages}
        workload={workload}
        onGenerate={() => void context.generateReviewPackages()}
        onRunAll={() => void context.runAllPackageReviews()}
      />

      {packages.length > 0 ? (
        <ExecutiveRiskSummary packages={packages} results={context.packageResults} />
      ) : null}

      {packages.length > 0 ? (
        <Panel title={t("review.riskBasedQueue")}>
          <div className="mb-5 flex flex-wrap gap-2">
            {queueFilters.map((filter) => (
              <button
                key={filter.value}
                type="button"
                className={`h-10 rounded-2xl border px-4 text-sm transition ${
                  queueFilter === filter.value ? "border-teal bg-teal text-white shadow-[0_14px_35px_rgba(0,155,141,0.18)]" : "border-black/10 bg-white/75 text-slate-700 hover:bg-white"
                }`}
                onClick={() => setQueueFilter(filter.value)}
              >
                {filter.label}
              </button>
            ))}
          </div>
          <div className="space-y-3">
            {filteredQueue.map((item) => (
              <QueueItemRow key={item.package_id} item={item} />
            ))}
          </div>
        </Panel>
      ) : null}

      {packages.map((pkg) => {
        const result = context.packageResults[pkg.id];
        const canRun = pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK";
        const libraryLabel =
          pkg.risk_library_reference === "NO_APPROVED_LIBRARY_MATCH"
            ? "NO_APPROVED_LIBRARY_MATCH"
            : `${pkg.risk_library_reference.libraryId} v${pkg.risk_library_reference.version}`;
        const baselineLabel =
          pkg.baseline_risk_item === "NOT_A_DELTA_UPDATE"
            ? "NOT_A_DELTA_UPDATE"
            : pkg.baseline_risk_item
              ? `${pkg.baseline_risk_item.risk_code} v${pkg.baseline_risk_item.approved_version}`
              : "Missing";

        return (
          <Panel
            key={pkg.id}
            title={`${pkg.risk_item_draft.risk_id}: ${pkg.risk_item_draft.failure_mode}`}
            action={
              <button
                type="button"
                className={`inline-flex h-9 items-center gap-2 rounded-md px-3 text-sm font-medium ${
                  canRun ? "bg-ink text-white" : "cursor-not-allowed bg-slate-100 text-slate-400"
                }`}
                disabled={!canRun}
                onClick={() => void context.runPackageReview(pkg.id)}
              >
                <Play className="h-4 w-4" aria-hidden />
                Plausibilitätscheck starten
              </button>
            }
          >
            <div className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
              <div className="space-y-3 text-sm leading-6">
                <div>
                  <span className="font-semibold">Status:</span>{" "}
                  <Badge tone={pkg.package_status === "INPUT_INCOMPLETE" ? "amber" : "slate"}>{pkg.package_status}</Badge>
                </div>
                <div>
                  <span className="font-semibold">Fehlende Eingaben:</span>{" "}
                  {pkg.missing_inputs.length > 0 ? pkg.missing_inputs.join(", ") : "keine"}
                </div>
                <div>
                  <span className="font-semibold">Risikobibliothek:</span> {libraryLabel}
                </div>
                <div>
                  <span className="font-semibold">Bestehender FMEA-Eintrag:</span> {baselineLabel}
                </div>
                <div>
                  <span className="font-semibold">Bewertungsvorschlag:</span> {pkg.scoring_model.name}, {pkg.scoring_model.scale}, RPN {pkg.risk_item_draft.initial_rpn_suggestion}
                </div>
                {result ? (
                  <div className="rounded-md bg-slate-50 p-3">
                    <div className="font-semibold">Plausibilitätscheck: {result.overall_result}</div>
                    <div>Evidenzqualität: {result.evidence_quality}</div>
                    <div>Empfohlener nächster Status: {result.recommended_status}</div>
                  </div>
                ) : null}
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <MiniList title="Quellenzitate" items={pkg.linked_source_snippets.map((snippet) => `${snippet.id}: ${snippet.sectionTitle}`)} />
                <MiniList title="Evidenzlinks" items={pkg.evidence_links.map((link) => `${link.id}: ${link.evidence_type} (${link.quality_status})`)} empty="Kein Evidenzlink" />
                <MiniList title="Dokumentierte Lücken" items={pkg.documented_gaps.map((gap) => `${gap.priority}: ${gap.description}`)} empty="Keine Lücke dokumentiert" />
              </div>
            </div>
            <div className="mt-5 border-t border-line pt-4">
              <h3 className="text-sm font-semibold">Quellenkarte</h3>
              <Table
                headers={["Aussage", "Quelle", "Dokument", "Evidenztyp", "Qualität", "Lücke", "Stützt"]}
                rows={buildEvidenceMap(pkg).map((row) => [
                  row.risk_item_claim,
                  row.source_snippet_id,
                  row.document_type,
                  row.evidence_type,
                  row.evidence_quality,
                  row.gap_status,
                  Object.entries(row.supports)
                    .filter(([, supported]) => supported)
                    .map(([key]) => key.replaceAll("_", " "))
                    .join(", ") || "nur Kontext"
                ])}
              />
            </div>
          </Panel>
        );
      })}

      {packages.length > 0 ? (
        <Panel
          title="Draft Risk Delta Review Pack"
          action={
            <button type="button" className="inline-flex h-9 items-center gap-2 rounded-md bg-ink px-3 text-sm font-medium text-white" onClick={context.generateDeltaExport}>
              <FileDown className="h-4 w-4" aria-hidden />
              Draft Export erzeugen
            </button>
          }
        >
          <div className="grid gap-4 md:grid-cols-3">
            <SummaryBlock title="Markdown" text="Lesbare Prüfmappen-Vorschau mit Scope, KI-Hinweis, Aufwand, Review Queue, Risiko-Delta-Matrix, Quellenkarte, Fragen und Grenzen." />
            <SummaryBlock title="CSV" text="Tabellarischer Risiko- und Queue-Export für Excel oder interne Review-Listen." />
            <SummaryBlock title="JSON" text="Strukturierte Paketdaten für technische Prüfung, Tests oder spätere Integration." />
          </div>
          {exportPack ? (
            <div className="mt-4 space-y-4">
              <div className="flex flex-wrap gap-2">
                <DownloadButton fileName="risk-delta-review-pack.md" mime="text/markdown" content={exportPack.markdown} label=".md herunterladen" />
                <DownloadButton fileName="risk-delta-review-pack.csv" mime="text/csv" content={exportPack.csv} label=".csv herunterladen" />
                <DownloadButton fileName="risk-delta-review-pack.json" mime="application/json" content={JSON.stringify(exportPack.json, null, 2)} label=".json herunterladen" />
              </div>
              <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-md bg-slate-950 p-4 text-xs leading-5 text-slate-100">{exportPack.markdown}</pre>
            </div>
          ) : (
            <div className="mt-4 rounded-md bg-slate-50 p-3 text-sm text-slate-600">Der Draft Export ist erlaubt und klar als ENTWURF gekennzeichnet. Ein freigegebener Export bleibt blockiert, solange keine menschliche QA-Entscheidung dokumentiert ist.</div>
          )}
        </Panel>
      ) : null}
    </div>
  );
}

function MatrixSection() {
  return (
    <Panel title="QRM / FMEA matrix">
      <Table
        headers={["Risk ID", "Step", "Failure mode / hazard", "Cause", "Effect", "S/O/D", "RPN", "Evidence", "Review", "Status"]}
        rows={demoRiskItems.map((item) => [
          item.id,
          item.processStep,
          item.failureMode,
          item.potentialCause,
          item.potentialEffect,
          `${item.severity}/${item.occurrence}/${item.detectability}`,
          item.severity * item.occurrence * item.detectability,
          item.evidenceStatus,
          `Level ${item.reviewLevel}`,
          item.status
        ])}
      />
    </Panel>
  );
}

function EvidenceSection() {
  return (
    <Panel title="Quellenkarte">
      <Table
        headers={["Risiko", "Benötigte Evidenz", "Quellen", "Qualität"]}
        rows={demoRiskItems.map((item) => [item.id, item.requiredEvidence.join("; "), item.sourceLinks.join(", "), item.evidenceStatus])}
      />
      <p className="mt-4 text-sm leading-6 text-slate-600">Eine SOP beschreibt oft nur die Regel. Für Wirksamkeit sind Tests, Validierungsberichte oder Effektivitätsnachweise belastbarer.</p>
    </Panel>
  );
}

function GapsSection() {
  return (
    <Panel title="Lücken und gezielte Expertenfragen">
      <Table headers={["Priorität", "Risiko", "Lücke", "Frage", "Status"]} rows={demoGaps.map((gap) => [gap.priority, gap.riskItemId, gap.description, gap.question, gap.status])} />
    </Panel>
  );
}

function PlausibilitySection() {
  return (
    <Panel title="Unabhängiger Plausibilitätscheck">
      <Table
        headers={["Risiko", "Ergebnis", "Benötigte Rolle", "Kommentar", "Themen"]}
        rows={demoPlausibilityChecks.map((check) => [check.riskItemId, check.result, check.requiredHumanReviewerType, check.comments, check.issues.join("; ")])}
      />
      <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-400">PASS bedeutet nur: Die Plausibilitätsprüfung hat keinen Blocker gefunden. Das ist keine QA-Entscheidung.</p>
    </Panel>
  );
}

function RedTeamSection() {
  return (
    <Panel title="Blind-Spot-Prüfung">
      <Table
        headers={["Kategorie", "Priorität", "Prüfpunkt", "Quellenbasis", "Status"]}
        rows={demoRedTeamFindings.map((finding) => [finding.category, finding.priority, finding.description, finding.sourceBasis, finding.status])}
      />
    </Panel>
  );
}

function ReviewQueueSection() {
  return <RiskRows items={reviewQueue} title="Priorisierte Review-Liste" />;
}

function ApprovalsSection({ role }: { role: string }) {
  const eligible = role === "QA_APPROVER";
  return (
    <Panel title="QA-Entscheidungsworkflow">
      <div className={`mb-4 border-l-4 px-4 py-3 text-sm ${eligible ? "border-teal bg-teal/10" : "border-danger bg-danger/10"}`}>
        Aktuelle Rolle: {role.replaceAll("_", " ")}. {eligible ? "Diese Rolle darf den QA-Schritt dokumentieren, wenn die Gates bestanden sind." : "Diese Rolle darf den QA-Schritt nicht dokumentieren."}
      </div>
      <Table
        headers={["Risiko", "Aktueller Status", "Gate-Ergebnis", "Plausibilität", "Menschliche Scores", "QA-Pfad"]}
        rows={demoRiskItems.map((item) => {
          const gates = runDeterministicGates(item);
          return [
            item.id,
            item.status,
            gates.ok ? "PASS" : gates.errors.join("; "),
            item.plausibilityResult,
            `${item.humanSeverity ?? "-"} / ${item.humanOccurrence ?? "-"} / ${item.humanDetectability ?? "-"}`,
            item.reviewLevel === 3 ? "Vollständiger SME- und QA-Review nötig" : "Risikobasierter Pfad"
          ];
        })}
      />
    </Panel>
  );
}

function AuditTrailSection() {
  return (
    <Panel title="Audit Trail">
      <Table
        headers={["Zeitpunkt", "Nutzer", "Aktion", "Objekt", "Grund", "Payload-Hash", "Vorheriger Hash"]}
        rows={demoAuditLogs.map((log) => [log.timestamp, log.userName, log.action, log.entityType, log.reason, log.eventPayloadHash, log.previousEventHash])}
      />
    </Panel>
  );
}

function ExportSection(context: Parameters<typeof renderSection>[1]) {
  return (
    <div className="space-y-6">
      <Panel title="Review-Pack Export">
        <div className="grid gap-4 md:grid-cols-2">
          <SummaryBlock title="Markdown" text="Lesbare Draft-Prüfmappe mit Scope, Quellenindex, Risikomatrix, Lücken, Checks, Review-Historie, Audit-Zusammenfassung und Grenzen." />
          <SummaryBlock title="CSV" text="Risikomatrix als Tabelle für Excel oder interne Review-Listen." />
        </div>
        <div className="mt-4 rounded-md bg-slate-50 p-3 text-sm leading-6 text-slate-700">
          Freigegebener Export blockiert: {context.approvedStyleExport.ok ? "Nein" : context.approvedStyleExport.errors.join(" ")}
        </div>
      </Panel>
      <Panel title="Markdown-Vorschau">
        <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-md bg-slate-950 p-4 text-xs leading-5 text-slate-100">{context.exportDraft.markdown}</pre>
      </Panel>
    </div>
  );
}

function ValidationPackSection() {
  const artifacts = generateValidationPack(demoProject.name);
  return (
    <Panel title="System Validation Pack">
      <Table headers={["Unterlage", "Status", "Zweck"]} rows={artifacts.map((artifact) => [artifact.title, artifact.status, artifact.content.split("\n")[7] ?? "Draft planning artifact"])} />
      <p className="mt-4 text-sm leading-6 text-slate-600">Das sind nur Entwurfsunterlagen. Produktiver Einsatz braucht formale Lifecycle-Kontrollen, SOPs, Lieferantenbewertung, Security-/Privacy-Review, Model Governance, Periodic Review und Kundenseitige QA-Entscheidungen.</p>
    </Panel>
  );
}

function AdminSection() {
  return (
    <Panel title="Admin / Benutzer">
      <Table headers={["Name", "E-Mail", "Rolle"]} rows={demoUsers.map((user) => [user.name, user.email, user.role.replaceAll("_", " ")])} />
      <p className="mt-4 text-sm leading-6 text-slate-600">Die lokale Demo nutzt Passwort demo123. Für produktiven Einsatz braucht es Unternehmens-Login, regelmäßige Zugriffsprüfung, Session-Kontrollen und Aufbewahrungsregeln.</p>
    </Panel>
  );
}

function RiskRows({ items, title, compact = false }: { items: typeof demoRiskItems; title?: string; compact?: boolean }) {
  const table = (
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-line text-xs uppercase tracking-[0.08em] text-slate-600">
            <tr>
              {["Risiko", "Priorität", "Level", "Fehlermodus / Risiko", "Evidenz", "Plausibilität", "Review"].map((header) => (
                <th key={header} className="px-3 py-2 font-semibold">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b border-line align-top">
                <td className="px-3 py-3 font-medium">{item.id}</td>
                <td className="px-3 py-3"><Badge tone={item.priority === "CRITICAL" ? "danger" : item.priority === "HIGH" ? "amber" : "slate"}>{item.priority}</Badge></td>
                <td className="px-3 py-3">Level {item.reviewLevel}</td>
                <td className="max-w-xl px-3 py-3">{item.failureMode}{compact ? null : <div className="mt-1 text-xs leading-5 text-slate-600">{item.potentialCause}</div>}</td>
                <td className="px-3 py-3">{item.evidenceStatus}</td>
                <td className="px-3 py-3">{item.plausibilityResult}</td>
                <td className="px-3 py-3">{item.reviewStatus}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
  );

  if (compact && !title) return table;
  return <Panel title={title ?? "Risk items"}>{table}</Panel>;
}

function Badge({ children, tone }: { children: React.ReactNode; tone: "danger" | "amber" | "slate" }) {
  const classes = {
    danger: "bg-danger/10 dark:bg-red-500/20 text-danger dark:text-red-400 ring-danger/10 dark:ring-red-400/20",
    amber: "bg-amber/10 dark:bg-amber-500/20 text-amber dark:text-amber-400 ring-amber/10 dark:ring-amber-400/20",
    slate: "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 ring-black/5 dark:ring-white/10"
  }[tone];
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1 ${classes}`}>{children}</span>;
}

function Metric({ label, value, tone = "slate" }: { label: string; value: string; tone?: "slate" | "teal" }) {
  return (
    <div className="rounded-md bg-slate-50 dark:bg-slate-800 p-3">
      <div className={`text-xl font-semibold ${tone === "teal" ? "text-teal dark:text-teal-400" : "text-slate-900 dark:text-white"}`}>{value}</div>
      <div className="mt-1 text-xs uppercase tracking-[0.08em] text-slate-600 dark:text-slate-400">{label}</div>
    </div>
  );
}

function QueueItemRow({ item }: { item: ReviewQueueItem }) {
  const tone = item.review_level === "LEVEL_3_FULL_SME_QA_REVIEW" ? "danger" : item.review_level === "INPUT_INCOMPLETE" || item.review_level === "LEVEL_2_TARGETED_SME_REVIEW" ? "amber" : "slate";
  const rail = tone === "danger" ? "bg-danger" : tone === "amber" ? "bg-amber" : "bg-teal";
  return (
    <div className="relative overflow-hidden rounded-[22px] border border-black/10 bg-white/78 p-5 shadow-[0_18px_45px_rgba(17,24,29,0.045)]">
      <div className={`absolute inset-y-0 left-0 w-1 ${rail}`} />
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="mr-1 font-semibold tracking-[-0.02em]">{item.risk_id}</span>
            <Badge tone={tone}>{formatBadge(item.review_level)}</Badge>
            {item.badges.map((badge) => (
              <span key={badge} className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-700">
                {formatBadge(badge)}
              </span>
            ))}
          </div>
          <div className="mt-3 text-[15px] font-semibold tracking-[-0.02em]">{item.failure_mode}</div>
          <p className="mt-1 text-sm leading-6 text-slate-600">{item.reason}</p>
        </div>
        <div className="min-w-64 rounded-2xl border border-black/10 bg-slate-50/80 px-4 py-3 text-sm leading-6">
          <div>
            <span className="font-semibold">Benötigte Rolle:</span> {item.required_reviewer_type.join(", ")}
          </div>
          <div>
            <span className="font-semibold">Nächster Schritt:</span> {formatNextAction(item.next_action)}
          </div>
        </div>
      </div>
    </div>
  );
}

function formatBadge(value: string) {
  const labels: Record<string, string> = {
    INPUT_INCOMPLETE: "Unvollständig",
    READY_FOR_PLAUSIBILITY_CHECK: "Bereit für Check",
    PLAUSIBILITY_PASS: "Plausibilität ok",
    PLAUSIBILITY_PARTIAL: "Teilweise plausibel",
    PLAUSIBILITY_FAIL: "Plausibilität fehlgeschlagen",
    EVIDENCE_MISSING: "Evidenz fehlt",
    SME_REQUIRED: "SME nötig",
    QA_REQUIRED: "QA nötig",
    AUTHOR_OPS_ACTION: "Author/Ops",
    LEVEL_0_BASELINE_UNCHANGED: "Level 0",
    LEVEL_1_QUICK_CHECK: "Level 1 Schnellcheck",
    LEVEL_2_TARGETED_SME_REVIEW: "Level 2 gezielter SME",
    LEVEL_3_FULL_SME_QA_REVIEW: "Level 3 SME/QA"
  };
  return labels[value] ?? value.replaceAll("_", " ").toLowerCase();
}

function formatNextAction(value: string) {
  const labels: Record<string, string> = {
    "complete input": "Eingabe vervollständigen",
    "run plausibility check": "Plausibilitätscheck starten",
    "resolve evidence gap": "Evidenzlücke klären",
    "SME review": "SME-Review durchführen",
    "QA approval": "QA-Entscheidung vorbereiten",
    "ready for export": "Bereit für Draft Export"
  };
  return labels[value] ?? value;
}

function GaugeMetric({ label, value, max, suffix, tone, large = false }: { label: string; value: number; max: number; suffix: string; tone: "slate" | "teal"; large?: boolean }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const color = tone === "teal" ? "#009b8d" : "#4b5563";
  return (
    <div className={large ? "" : "rounded-xl bg-slate-50 p-4"}>
      <div
        className={`${large ? "h-52 w-52" : "h-28 w-28"} mx-auto grid place-items-center rounded-full`}
        style={{
          background: `conic-gradient(${color} ${pct}%, #e6ecef ${pct}% 100%)`
        }}
      >
        <div className={`${large ? "h-36 w-36" : "h-20 w-20"} grid place-items-center rounded-full bg-white shadow-inner`}>
          <div className="text-center">
            <div className={`${large ? "text-5xl font-light tracking-[-0.08em]" : "text-2xl font-semibold tracking-[-0.03em]"} text-slate-950`}>
              {value.toFixed(suffix === "%" ? 0 : 1)}
              <span className="text-sm">{suffix}</span>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-3 text-center text-[11px] font-medium uppercase tracking-[0.16em] text-slate-600">{label}</div>
    </div>
  );
}

function queueFilterMatch(item: ReviewQueueItem, filter: string) {
  if (filter === "Input incomplete") return item.review_level === "INPUT_INCOMPLETE";
  if (filter === "Ready for plausibility check") return item.badges.includes("READY_FOR_PLAUSIBILITY_CHECK");
  if (filter === "SME required") return item.badges.includes("SME_REQUIRED");
  if (filter === "QA required") return item.badges.includes("QA_REQUIRED");
  if (filter === "Evidence gaps") return item.badges.includes("EVIDENCE_MISSING");
  if (filter === "High priority") return item.review_level === "LEVEL_3_FULL_SME_QA_REVIEW";
  if (filter === "Quick check only") return item.review_level === "LEVEL_1_QUICK_CHECK";
  return true;
}

function DownloadButton({ fileName, mime, content, label }: { fileName: string; mime: string; content: string; label: string }) {
  const href = `data:${mime};charset=utf-8,${encodeURIComponent(content)}`;
  return (
    <a href={href} download={fileName} className="inline-flex h-9 items-center rounded-md border border-line bg-white px-3 text-sm font-medium text-slate-800">
      {label}
    </a>
  );
}

function MiniList({ title, items, empty = "None" }: { title: string; items: string[]; empty?: string }) {
  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-600">{title}</div>
      {items.length > 0 ? (
        <ul className="mt-2 space-y-2 text-sm leading-5 text-slate-700">
          {items.map((item) => (
            <li key={item} className="rounded-md bg-slate-50 px-3 py-2">
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <div className="mt-2 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600">{empty}</div>
      )}
    </div>
  );
}

function Table({ headers, rows }: { headers: string[]; rows: Array<Array<React.ReactNode>> }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-line text-xs uppercase tracking-[0.08em] text-slate-600">
          <tr>
            {headers.map((header) => (
              <th key={header} className="px-3 py-2 font-semibold">{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index} className="border-b border-line align-top">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="max-w-md px-3 py-3 leading-6">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
