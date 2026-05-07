"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  AlertTriangle,
  Archive,
  Bot,
  CheckCircle2,
  ClipboardCheck,
  Database,
  FileDown,
  FileText,
  FlaskConical,
  Gauge,
  History,
  Library,
  Lock,
  PackageCheck,
  MessageSquareWarning,
  Play,
  Bell,
  BookOpen,
  HelpCircle,
  ShieldCheck,
  Table2,
  Users
} from "lucide-react";
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

const navItems = [
  ["dashboard", "Dashboard", Gauge],
  ["projects", "Projects", Archive],
  ["documents", "Documents", FileText],
  ["source-snippets", "Source snippets", Database],
  ["risk-library", "Risk library", Library],
  ["trigger-input", "Change/deviation/CAPA/finding input", ClipboardCheck],
  ["delta-analysis", "Delta analysis", Bot],
  ["review-packages", "Review Packages", PackageCheck],
  ["qrm-matrix", "QRM matrix", Table2],
  ["evidence-map", "Evidence map", ShieldCheck],
  ["gaps", "Gaps", AlertTriangle],
  ["plausibility-checks", "Plausibility checks", CheckCircle2],
  ["red-team-findings", "Red-team findings", MessageSquareWarning],
  ["review-queue", "Review queue", Users],
  ["approvals", "Approvals", Lock],
  ["audit-trail", "Audit trail", History],
  ["export-package", "Export package", FileDown],
  ["validation-pack", "Validation pack", FlaskConical],
  ["admin-users", "Admin/users", Users]
] as const;

export const sectionSlugs = navItems.map(([slug]) => slug);

const pageTitles: Record<string, string> = Object.fromEntries(navItems.map(([slug, label]) => [slug, label]));
pageTitles["project-detail"] = "Project detail";

type RunState = "idle" | "running" | "done";

export function AppShell({ section, projectId }: { section: string; projectId?: string }) {
  const active = sectionSlugs.includes(section as (typeof sectionSlugs)[number]) || section === "project-detail" ? section : "dashboard";
  const [role, setRole] = useState("QRM_AUTHOR");
  const [deltaState, setDeltaState] = useState<RunState>("idle");
  const [criticState, setCriticState] = useState<RunState>("idle");
  const [redTeamState, setRedTeamState] = useState<RunState>("idle");
  const [reviewPackages, setReviewPackages] = useState<ReviewPackage[]>([]);
  const [packageResults, setPackageResults] = useState<Record<string, PackageReviewResult>>({});
  const [riskDeltaExport, setRiskDeltaExport] = useState<ReturnType<typeof generateRiskDeltaReviewPack> | null>(null);
  const [loginMessage, setLoginMessage] = useState("Demo users use password demo123.");

  const exportDraft = useMemo(
    () => exportPackage({ project: demoProject, riskItems: demoRiskItems, gaps: demoGaps, approvedPackage: false }),
    []
  );
  const approvedStyleExport = useMemo(
    () => exportPackage({ project: demoProject, riskItems: demoRiskItems, gaps: demoGaps, approvedPackage: true }),
    []
  );

  async function runApi(path: string, setter: (state: RunState) => void) {
    setter("running");
    await fetch(path, { method: "POST", body: JSON.stringify({ projectId: demoProject.id }) });
    setter("done");
  }

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

  return (
    <div className="min-h-screen bg-mist text-ink">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-line bg-white/92 backdrop-blur lg:block">
        <div className="border-b border-line px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-lg bg-teal text-sm font-semibold text-white shadow-sm">Q</div>
            <div>
              <div className="text-[15px] font-semibold leading-5 tracking-normal">Pharma QRM</div>
              <div className="text-[15px] font-semibold leading-5 tracking-normal text-teal">Delta Factory</div>
            </div>
          </div>
          <div className="mt-4 text-xs leading-5 text-slate-600">Source-based DRAFT QRM work products for qualified human review.</div>
        </div>
        <nav className="h-[calc(100vh-104px)] overflow-y-auto px-3 py-3">
          {navItems.map(([slug, label, Icon]) => (
            <Link
              key={slug}
              href={slug === "dashboard" ? "/" : `/${slug}`}
              className={`mb-1 flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
                active === slug ? "bg-teal/10 text-teal ring-1 ring-teal/15" : "text-slate-700 hover:bg-slate-100"
              }`}
            >
              <Icon className="h-4 w-4" aria-hidden />
              <span>{label}</span>
            </Link>
          ))}
        </nav>
      </aside>

      <main className="lg:pl-72">
        <header className="sticky top-0 z-10 border-b border-line bg-white/88 px-4 py-4 backdrop-blur-xl lg:px-8">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.16em] text-slate-500">Workspace / {demoProject.name}</div>
              <h1 className="mt-1 text-[28px] font-semibold leading-tight tracking-[-0.02em]">{pageTitles[active] ?? "Dashboard"}</h1>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="hidden rounded-full border border-teal/20 bg-teal/5 px-3 py-1.5 text-xs font-medium text-teal md:inline-flex">Version 1.2.0</span>
              <button type="button" className="hidden h-9 w-9 place-items-center rounded-lg border border-line bg-white text-slate-600 md:grid" aria-label="Notifications">
                <Bell className="h-4 w-4" />
              </button>
              <button type="button" className="hidden h-9 w-9 place-items-center rounded-lg border border-line bg-white text-slate-600 md:grid" aria-label="Help">
                <HelpCircle className="h-4 w-4" />
              </button>
              <button type="button" className="hidden h-9 w-9 place-items-center rounded-lg border border-line bg-white text-slate-600 md:grid" aria-label="Documentation">
                <BookOpen className="h-4 w-4" />
              </button>
              <select
                className="h-9 rounded-lg border border-line bg-white px-3 text-sm"
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
                className="inline-flex h-9 items-center gap-2 rounded-lg bg-ink px-3 text-sm font-medium text-white shadow-sm"
                onClick={() => setLoginMessage(`Active local demo role: ${role.replaceAll("_", " ")}`)}
              >
                <Lock className="h-4 w-4" aria-hidden />
                Local auth
              </button>
            </div>
          </div>
        </header>

        <div className="px-4 py-6 lg:px-8">
          <Notice text="All AI-generated content is labeled DRAFT. The app prepares reviewable work products; it does not replace qualified human risk assessment, QA responsibility, or regulatory decisions." />
          <div className="mt-4 text-sm text-slate-600">{loginMessage}</div>
          <div className="mt-6">{renderSection(active, { deltaState, criticState, redTeamState, runApi, setDeltaState, setCriticState, setRedTeamState, exportDraft, approvedStyleExport, role, projectId, reviewPackages, packageResults, generateReviewPackages, runPackageReview, runAllPackageReviews, generateDeltaExport, riskDeltaExport })}</div>
        </div>
      </main>
    </div>
  );
}

function renderSection(
  section: string,
  context: {
    deltaState: RunState;
    criticState: RunState;
    redTeamState: RunState;
    runApi: (path: string, setter: (state: RunState) => void) => Promise<void>;
    setDeltaState: (state: RunState) => void;
    setCriticState: (state: RunState) => void;
    setRedTeamState: (state: RunState) => void;
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
  }
) {
  switch (section) {
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
      return <DeltaSection {...context} />;
    case "review-packages":
      return <ReviewPackagesSection {...context} />;
    case "qrm-matrix":
      return <MatrixSection />;
    case "evidence-map":
      return <EvidenceSection />;
    case "gaps":
      return <GapsSection />;
    case "plausibility-checks":
      return <PlausibilitySection {...context} />;
    case "red-team-findings":
      return <RedTeamSection {...context} />;
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
  return (
    <div className="rounded-lg border border-amber/25 border-l-4 bg-[#fff9ed] px-4 py-3 text-sm leading-6 text-slate-800 shadow-sm">
      <strong className="font-semibold">DRAFT safety notice:</strong> {text}
    </div>
  );
}

function Panel({ title, children, action }: { title: string; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-line bg-white/94 shadow-[0_18px_45px_rgba(23,32,38,0.045)]">
      <div className="flex items-center justify-between border-b border-line px-5 py-4">
        <h2 className="text-base font-semibold tracking-[-0.01em]">{title}</h2>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}

function Stat({ label, value, tone = "slate" }: { label: string; value: string | number; tone?: "slate" | "teal" | "amber" | "danger" }) {
  const toneClass = {
    slate: "text-slate-900",
    teal: "text-teal",
    amber: "text-amber",
    danger: "text-danger"
  }[tone];
  return (
    <div className="rounded-xl border border-line bg-white px-5 py-4 shadow-[0_10px_30px_rgba(23,32,38,0.035)]">
      <div className={`text-3xl font-semibold tracking-[-0.03em] ${toneClass}`}>{value}</div>
      <div className="mt-2 text-[11px] uppercase tracking-[0.16em] text-slate-500">{label}</div>
    </div>
  );
}

function DashboardSection(context: Parameters<typeof renderSection>[1]) {
  return (
    <div className="space-y-6">
      <div className="grid gap-3 md:grid-cols-4">
        <Stat label="Open high gaps" value={demoGaps.filter((gap) => gap.status === "OPEN" && ["HIGH", "CRITICAL"].includes(gap.priority)).length} tone="danger" />
        <Stat label="Level 3 review" value={demoRiskItems.filter((item) => item.reviewLevel === 3).length} tone="amber" />
        <Stat label="AI draft items" value={demoRiskItems.filter((item) => item.status === "AI_DRAFT").length} tone="teal" />
        <Stat label="Source snippets" value={demoSnippets.length} />
      </div>
      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel
          title="Risk-based human review queue"
          action={<Link className="text-sm font-medium text-teal" href="/review-queue">Open queue</Link>}
        >
          <RiskRows items={reviewQueue.slice(0, 4)} compact />
        </Panel>
        <Panel title="Run mock AI safety layers">
          <div className="grid gap-3">
            <RunButton label="Run Author AI delta" state={context.deltaState} onClick={() => context.runApi("/api/ai/delta", context.setDeltaState)} />
            <RunButton label="Run independent plausibility check" state={context.criticState} onClick={() => context.runApi("/api/ai/critic", context.setCriticState)} />
            <RunButton label="Run Red-Team missing-risk finder" state={context.redTeamState} onClick={() => context.runApi("/api/ai/red-team", context.setRedTeamState)} />
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-600">Each run uses MockLLMAdapter only. No external AI API is called.</p>
        </Panel>
      </div>
      <Panel title="Delta summary">
        <div className="grid gap-4 md:grid-cols-3">
          <SummaryBlock title="Trigger" text="Change control for modified automated visual inspection rejection threshold." />
          <SummaryBlock title="Main concern" text="Evidence package covers old threshold; new-threshold effectiveness evidence is missing." />
          <SummaryBlock title="Routing" text="Level 3 items go to SME review first, then QA workflow only after required fields and gates pass." />
        </div>
      </Panel>
    </div>
  );
}

function SummaryBlock({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <div className="text-sm font-semibold text-slate-900">{title}</div>
      <p className="mt-1 text-sm leading-6 text-slate-600">{text}</p>
    </div>
  );
}

function RunButton({ label, state, onClick }: { label: string; state: RunState; onClick: () => void }) {
  return (
    <button
      type="button"
      className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-medium text-slate-800 hover:bg-slate-50"
      onClick={onClick}
    >
      <Play className="h-4 w-4" aria-hidden />
      {state === "running" ? "Running..." : state === "done" ? `${label}: DRAFT ready` : label}
    </button>
  );
}

function ProjectsSection() {
  return (
    <Panel title="Projects">
      <div className="grid gap-4 lg:grid-cols-[1fr_0.8fr]">
        <Link href={`/projects/${demoProject.id}`} className="block rounded-lg border border-line p-4 hover:bg-slate-50">
          <div className="text-lg font-semibold">{demoProject.name}</div>
          <p className="mt-2 text-sm leading-6 text-slate-600">{demoProject.scopeStatement}</p>
          <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
            <span className="rounded bg-slate-100 px-2 py-1">{demoProject.gmpArea}</span>
            <span className="rounded bg-slate-100 px-2 py-1">{demoProject.methodology}</span>
            <span className="rounded bg-slate-100 px-2 py-1">{demoProject.triggerType}</span>
          </div>
        </Link>
        <form className="grid gap-3 rounded-lg border border-line p-4">
          <div className="font-semibold">Create QRM project</div>
          {["Project name", "Product/process/system", "GMP area", "Scope statement", "Out-of-scope statement"].map((label) => (
            <input key={label} className="h-9 rounded-md border border-line px-3 text-sm" placeholder={label} />
          ))}
          <button type="button" className="h-9 rounded-md bg-teal px-3 text-sm font-medium text-white">Create draft project</button>
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
              <dt className="text-xs uppercase tracking-[0.08em] text-slate-500">{key}</dt>
              <dd className="mt-1 text-sm leading-6 text-slate-800">{value}</dd>
            </div>
          ))}
        </dl>
      </Panel>
      <DashboardSection {...({ deltaState: "idle", criticState: "idle", redTeamState: "idle", runApi: async () => undefined, setDeltaState: () => undefined, setCriticState: () => undefined, setRedTeamState: () => undefined, exportDraft: exportPackage({ project: demoProject, riskItems: demoRiskItems, gaps: demoGaps, approvedPackage: false }), approvedStyleExport: exportPackage({ project: demoProject, riskItems: demoRiskItems, gaps: demoGaps, approvedPackage: true }), role: "QRM_AUTHOR", reviewPackages: [], packageResults: {}, generateReviewPackages: async () => undefined, runPackageReview: async () => undefined, runAllPackageReviews: async () => undefined, generateDeltaExport: () => undefined, riskDeltaExport: null } as Parameters<typeof renderSection>[1])} />
    </div>
  );
}

function DocumentsSection() {
  return (
    <Panel title="Source documents">
      <Table
        headers={["Document type", "File", "Supported format", "Content excerpt"]}
        rows={demoDocuments.map((document) => [document.documentType, document.fileName, document.fileName.split(".").pop(), document.content])}
      />
      <div className="mt-4 text-sm leading-6 text-slate-600">TODO placeholders: PDF, DOCX, XLSX, OCR, SharePoint/Teams, Veeva, TrackWise, Documentum ingestion.</div>
    </Panel>
  );
}

function SnippetsSection() {
  return (
    <Panel title="Source snippets with hashes">
      <Table
        headers={["Snippet", "Document", "Section", "Line/page placeholder", "Hash"]}
        rows={demoSnippets.map((snippet) => [snippet.id, snippet.documentType, snippet.sectionTitle, snippet.lineReference, snippet.snippetHash.slice(0, 16)])}
      />
    </Panel>
  );
}

function RiskLibrarySection() {
  return (
    <Panel title="Approved risk library">
      <Table
        headers={["Library ID", "GMP area", "Process step", "Failure mode / hazard", "Status", "Version", "SME"]}
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
      <p className="mt-4 text-sm leading-6 text-slate-600">Unapproved library items cannot be used as an approved basis. If no match exists, the risk is marked NEW_OR_UNVERIFIED and routed to SME review.</p>
    </Panel>
  );
}

function TriggerSection() {
  return (
    <Panel title="Change/deviation/CAPA/finding input">
      <div className="grid gap-4 md:grid-cols-2">
        <SummaryBlock title="Change control" text="Modified AVI rejection threshold to reduce false rejects while maintaining detection capability." />
        <SummaryBlock title="Deviation" text="Batch record reconciliation wording for AVI reject counts is unclear." />
        <SummaryBlock title="CAPA" text="Synthetic follow-up for threshold evidence, training completion, and reconciliation clarification." />
        <SummaryBlock title="Audit finding" text="Review whether audit trail scope explicitly covers threshold configuration." />
      </div>
    </Panel>
  );
}

function DeltaSection(context: Parameters<typeof renderSection>[1]) {
  return (
    <div className="space-y-6">
      <Panel
        title="AI-assisted risk delta generation"
        action={<RunButton label="Run Author AI delta" state={context.deltaState} onClick={() => context.runApi("/api/ai/delta", context.setDeltaState)} />}
      >
        <p className="text-sm leading-6 text-slate-600">Mock Author AI maps the trigger to existing risk items, proposes DRAFT updates, flags missing controls/evidence, and creates SME questions.</p>
        <Link href="/review-packages" className="mt-3 inline-flex h-9 items-center rounded-md bg-teal px-3 text-sm font-medium text-white">
          Build review packages
        </Link>
      </Panel>
      <RiskRows items={demoRiskItems} />
    </div>
  );
}

function ReviewPackagesSection(context: Parameters<typeof renderSection>[1]) {
  const packages = context.reviewPackages;
  const [queueFilter, setQueueFilter] = useState("All");
  const queue = buildReviewQueue(packages, context.packageResults);
  const filteredQueue = queue.filter((item) => queueFilter === "All" || queueFilterMatch(item, queueFilter));
  const workload = summarizeWorkload(packages, context.packageResults);
  const exportPack = context.riskDeltaExport;

  return (
    <div className="space-y-6">
      <Panel
        title="Risk Review Package Builder"
        action={
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="inline-flex h-9 items-center gap-2 rounded-md bg-teal px-3 text-sm font-medium text-white"
              onClick={() => void context.generateReviewPackages()}
            >
              <PackageCheck className="h-4 w-4" aria-hidden />
              Generate Review Packages
            </button>
            <button
              type="button"
              className="inline-flex h-9 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-medium text-slate-800"
              disabled={packages.length === 0}
              onClick={() => void context.runAllPackageReviews()}
            >
              <Play className="h-4 w-4" aria-hidden />
              Run all ready checks
            </button>
          </div>
        }
      >
        <div className="grid gap-4 md:grid-cols-3">
          <SummaryBlock title="Architecture" text="Documents, trigger record, existing FMEA, source snippets, risk library, and scoring model are assembled before the independent reviewer can run." />
          <SummaryBlock title="Completeness gate" text="Missing technical input is routed back to Author/Ops. The Critic is not called on empty or partial packages." />
          <SummaryBlock title="Demo scenario" text="CC-2026-014 for sterile injectable AVI threshold change, old-threshold validation only, missing training record, and missing validation addendum." />
        </div>
        {packages.length > 0 ? (
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <Stat label="Generated packages" value={workload.total_packages} />
            <Stat label="Ready for review" value={workload.ready_for_review} tone="teal" />
            <Stat label="Input incomplete" value={workload.input_incomplete} tone="amber" />
          </div>
        ) : (
          <div className="mt-4 rounded-md bg-slate-50 p-3 text-sm text-slate-600">Click Generate Review Packages to assemble structured packages before plausibility review.</div>
        )}
      </Panel>

      {packages.length > 0 ? (
        <Panel title="Risk Review Summary">
          <div className="grid gap-0 overflow-hidden rounded-xl border border-line bg-white md:grid-cols-6">
            <Stat label="Total packages" value={workload.total_packages} />
            <Stat label="Ready for review" value={workload.ready_for_review} tone="teal" />
            <Stat label="Input incomplete" value={workload.input_incomplete} tone="amber" />
            <Stat label="Plausibility PASS" value={workload.plausibility_pass} tone="teal" />
            <Stat label="Plausibility PARTIAL" value={workload.plausibility_partial} tone="amber" />
            <Stat label="Plausibility FAIL" value={workload.plausibility_fail} tone="danger" />
          </div>
          <div className="mt-6 grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
            <div className="rounded-xl border border-line bg-white p-5">
              <h3 className="font-semibold">Review workload</h3>
              <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
                <li>Level 0: {workload.level_counts.LEVEL_0_BASELINE_UNCHANGED} items - no detailed review required</li>
                <li>Level 1: {workload.level_counts.LEVEL_1_QUICK_CHECK} item - quick QA check</li>
                <li>Level 2: {workload.level_counts.LEVEL_2_TARGETED_SME_REVIEW} items - targeted SME review</li>
                <li>Level 3: {workload.level_counts.LEVEL_3_FULL_SME_QA_REVIEW} items - full SME/QA review</li>
              </ul>
            </div>
            <div className="rounded-xl border border-line bg-white p-5">
              <h3 className="font-semibold">Human review saved</h3>
              <div className="mt-4 grid gap-4 sm:grid-cols-3">
                <GaugeMetric label="Manual baseline" value={workload.manual_baseline_hours} max={20} suffix="h" tone="slate" />
                <GaugeMetric label="Assisted review" value={workload.assisted_review_hours} max={20} suffix="h" tone="teal" />
                <GaugeMetric label="Reduction" value={workload.estimated_reduction_percent} max={100} suffix="%" tone="teal" />
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-600">Indicative MVP estimate only. It shows how consultant and expert time is redirected toward exceptions instead of document hunting.</p>
            </div>
          </div>
        </Panel>
      ) : null}

      {packages.length > 0 ? (
        <Panel title="Risk-Based Review Queue">
          <div className="mb-4 flex flex-wrap gap-2">
            {["All", "Input incomplete", "Ready for plausibility check", "SME required", "QA required", "Evidence gaps", "High priority", "Quick check only"].map((filter) => (
              <button
                key={filter}
                type="button"
                className={`h-8 rounded-md border px-3 text-sm ${queueFilter === filter ? "border-teal bg-teal text-white" : "border-line bg-white text-slate-700"}`}
                onClick={() => setQueueFilter(filter)}
              >
                {filter}
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
                Run Plausibility Check
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
                  <span className="font-semibold">Missing fields:</span>{" "}
                  {pkg.missing_inputs.length > 0 ? pkg.missing_inputs.join(", ") : "None"}
                </div>
                <div>
                  <span className="font-semibold">Risk library:</span> {libraryLabel}
                </div>
                <div>
                  <span className="font-semibold">Baseline:</span> {baselineLabel}
                </div>
                <div>
                  <span className="font-semibold">Scoring:</span> {pkg.scoring_model.name}, {pkg.scoring_model.scale}, RPN {pkg.risk_item_draft.initial_rpn_suggestion}
                </div>
                {result ? (
                  <div className="rounded-md bg-slate-50 p-3">
                    <div className="font-semibold">Critic result: {result.overall_result}</div>
                    <div>Evidence: {result.evidence_quality}</div>
                    <div>Recommended status: {result.recommended_status}</div>
                  </div>
                ) : null}
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <MiniList title="Linked snippets" items={pkg.linked_source_snippets.map((snippet) => `${snippet.id}: ${snippet.sectionTitle}`)} />
                <MiniList title="Evidence links" items={pkg.evidence_links.map((link) => `${link.id}: ${link.evidence_type} (${link.quality_status})`)} empty="No evidence link" />
                <MiniList title="Documented gaps" items={pkg.documented_gaps.map((gap) => `${gap.priority}: ${gap.description}`)} empty="No documented gap" />
              </div>
            </div>
            <div className="mt-5 border-t border-line pt-4">
              <h3 className="text-sm font-semibold">Evidence Map</h3>
              <Table
                headers={["Claim", "Snippet", "Document", "Evidence", "Quality", "Gap", "Supports"]}
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
                    .join(", ") || "Context only"
                ])}
              />
            </div>
          </Panel>
        );
      })}

      {packages.length > 0 ? (
        <Panel
          title="Risk Delta Review Pack Export"
          action={
            <button type="button" className="inline-flex h-9 items-center gap-2 rounded-md bg-ink px-3 text-sm font-medium text-white" onClick={context.generateDeltaExport}>
              <FileDown className="h-4 w-4" aria-hidden />
              Generate Export
            </button>
          }
        >
          <div className="grid gap-4 md:grid-cols-3">
            <SummaryBlock title="Markdown" text="Professional draft deliverable with cover, AI disclosure, workload summary, review queue, risk delta matrix, evidence map, questions, audit summary, and limitations." />
            <SummaryBlock title="CSV" text="Risk matrix queue export for spreadsheet review." />
            <SummaryBlock title="JSON" text="Structured ReviewPackage data for downstream inspection, testing, or system integration." />
          </div>
          {exportPack ? (
            <div className="mt-4 space-y-4">
              <div className="flex flex-wrap gap-2">
                <DownloadButton fileName="risk-delta-review-pack.md" mime="text/markdown" content={exportPack.markdown} label="Download .md" />
                <DownloadButton fileName="risk-delta-review-pack.csv" mime="text/csv" content={exportPack.csv} label="Download .csv" />
                <DownloadButton fileName="risk-delta-review-pack.json" mime="application/json" content={JSON.stringify(exportPack.json, null, 2)} label="Download .json" />
              </div>
              <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-md bg-slate-950 p-4 text-xs leading-5 text-slate-100">{exportPack.markdown}</pre>
            </div>
          ) : (
            <div className="mt-4 rounded-md bg-slate-50 p-3 text-sm text-slate-600">Draft export is allowed and clearly marked DRAFT. Approved export remains blocked until package approval workflow exists.</div>
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
    <Panel title="Evidence map">
      <Table
        headers={["Risk", "Required evidence / verification", "Source links", "Evidence quality"]}
        rows={demoRiskItems.map((item) => [item.id, item.requiredEvidence.join("; "), item.sourceLinks.join(", "), item.evidenceStatus])}
      />
      <p className="mt-4 text-sm leading-6 text-slate-600">SOP-only evidence can describe a control, but usually does not prove effectiveness. Validation reports or tests are stronger evidence for effectiveness.</p>
    </Panel>
  );
}

function GapsSection() {
  return (
    <Panel title="Gap and expert-question list">
      <Table headers={["Priority", "Risk", "Gap", "Question", "Status"]} rows={demoGaps.map((gap) => [gap.priority, gap.riskItemId, gap.description, gap.question, gap.status])} />
    </Panel>
  );
}

function PlausibilitySection(context: Parameters<typeof renderSection>[1]) {
  return (
    <Panel
      title="Independent AI plausibility checks"
      action={<RunButton label="Run critic" state={context.criticState} onClick={() => context.runApi("/api/ai/critic", context.setCriticState)} />}
    >
      <Table
        headers={["Risk", "Result", "Reviewer type", "Comments", "Issues"]}
        rows={demoPlausibilityChecks.map((check) => [check.riskItemId, check.result, check.requiredHumanReviewerType, check.comments, check.issues.join("; ")])}
      />
      <p className="mt-4 text-sm leading-6 text-slate-600">PASS means plausibility only. It is not a QA decision.</p>
    </Panel>
  );
}

function RedTeamSection(context: Parameters<typeof renderSection>[1]) {
  return (
    <Panel
      title="Red-Team Missing Risk Finder"
      action={<RunButton label="Run red team" state={context.redTeamState} onClick={() => context.runApi("/api/ai/red-team", context.setRedTeamState)} />}
    >
      <Table
        headers={["Category", "Priority", "Finding", "Source basis", "Status"]}
        rows={demoRedTeamFindings.map((finding) => [finding.category, finding.priority, finding.description, finding.sourceBasis, finding.status])}
      />
    </Panel>
  );
}

function ReviewQueueSection() {
  return <RiskRows items={reviewQueue} title="Prioritized review queue" />;
}

function ApprovalsSection({ role }: { role: string }) {
  const eligible = role === "QA_APPROVER";
  return (
    <Panel title="Approval workflow">
      <div className={`mb-4 border-l-4 px-4 py-3 text-sm ${eligible ? "border-teal bg-teal/10" : "border-danger bg-danger/10"}`}>
        Current role: {role.replaceAll("_", " ")}. {eligible ? "This role may perform the QA workflow step after gates pass." : "This role cannot perform the QA workflow step."}
      </div>
      <Table
        headers={["Risk", "Current status", "Gate result", "Plausibility", "Human scores", "QA route"]}
        rows={demoRiskItems.map((item) => {
          const gates = runDeterministicGates(item);
          return [
            item.id,
            item.status,
            gates.ok ? "PASS" : gates.errors.join("; "),
            item.plausibilityResult,
            `${item.humanSeverity ?? "-"} / ${item.humanOccurrence ?? "-"} / ${item.humanDetectability ?? "-"}`,
            item.reviewLevel === 3 ? "Full SME and QA review required" : "Risk-based route"
          ];
        })}
      />
    </Panel>
  );
}

function AuditTrailSection() {
  return (
    <Panel title="Append-only audit trail">
      <Table
        headers={["Timestamp", "User", "Action", "Entity", "Reason", "Payload hash", "Previous hash"]}
        rows={demoAuditLogs.map((log) => [log.timestamp, log.userName, log.action, log.entityType, log.reason, log.eventPayloadHash, log.previousEventHash])}
      />
    </Panel>
  );
}

function ExportSection(context: Parameters<typeof renderSection>[1]) {
  return (
    <div className="space-y-6">
      <Panel title="Export package">
        <div className="grid gap-4 md:grid-cols-2">
          <SummaryBlock title="Markdown export" text="Includes scope, methodology, source index, risk matrix, gaps, checks, review history, audit summary, limitations, and mandatory AI-assistance disclosure." />
          <SummaryBlock title="CSV export" text="Risk matrix rows are prepared for spreadsheet review. This MVP exposes the generated content through /api/export." />
        </div>
        <div className="mt-4 rounded-md bg-slate-50 p-3 text-sm leading-6 text-slate-700">
          Approved-style export blocked: {context.approvedStyleExport.ok ? "No" : context.approvedStyleExport.errors.join(" ")}
        </div>
      </Panel>
      <Panel title="Markdown preview">
        <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-md bg-slate-950 p-4 text-xs leading-5 text-slate-100">{context.exportDraft.markdown}</pre>
      </Panel>
    </div>
  );
}

function ValidationPackSection() {
  const artifacts = generateValidationPack(demoProject.name);
  return (
    <Panel title="System Validation Pack">
      <Table headers={["Artifact", "Status", "Purpose"]} rows={artifacts.map((artifact) => [artifact.title, artifact.status, artifact.content.split("\n")[7] ?? "Draft planning artifact"])} />
      <p className="mt-4 text-sm leading-6 text-slate-600">These are draft templates only. Production use requires formal lifecycle controls, SOPs, supplier assessment, security and privacy review, model governance, periodic review, and customer QA decisions.</p>
    </Panel>
  );
}

function AdminSection() {
  return (
    <Panel title="Admin/users">
      <Table headers={["Name", "Email", "Role"]} rows={demoUsers.map((user) => [user.name, user.email, user.role.replaceAll("_", " ")])} />
      <p className="mt-4 text-sm leading-6 text-slate-600">Simple local demo authentication uses password demo123. Production use would need enterprise identity, access review, session controls, and record-retention configuration.</p>
    </Panel>
  );
}

function RiskRows({ items, title, compact = false }: { items: typeof demoRiskItems; title?: string; compact?: boolean }) {
  const table = (
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-line text-xs uppercase tracking-[0.08em] text-slate-500">
            <tr>
              {["Risk", "Priority", "Level", "Failure mode / hazard", "Evidence", "Plausibility", "Review"].map((header) => (
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
                <td className="max-w-xl px-3 py-3">{item.failureMode}{compact ? null : <div className="mt-1 text-xs leading-5 text-slate-500">{item.potentialCause}</div>}</td>
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
    danger: "bg-danger/10 text-danger",
    amber: "bg-amber/10 text-amber",
    slate: "bg-slate-100 text-slate-700"
  }[tone];
  return <span className={`inline-flex rounded px-2 py-1 text-xs font-medium ${classes}`}>{children}</span>;
}

function Metric({ label, value, tone = "slate" }: { label: string; value: string; tone?: "slate" | "teal" }) {
  return (
    <div className="rounded-md bg-slate-50 p-3">
      <div className={`text-xl font-semibold ${tone === "teal" ? "text-teal" : "text-slate-900"}`}>{value}</div>
      <div className="mt-1 text-xs uppercase tracking-[0.08em] text-slate-500">{label}</div>
    </div>
  );
}

function QueueItemRow({ item }: { item: ReviewQueueItem }) {
  const tone = item.review_level === "LEVEL_3_FULL_SME_QA_REVIEW" ? "danger" : item.review_level === "INPUT_INCOMPLETE" || item.review_level === "LEVEL_2_TARGETED_SME_REVIEW" ? "amber" : "slate";
  const rail = tone === "danger" ? "border-l-danger" : tone === "amber" ? "border-l-amber" : "border-l-teal";
  return (
    <div className={`rounded-xl border border-l-4 border-line ${rail} bg-white p-4 shadow-[0_12px_35px_rgba(23,32,38,0.035)]`}>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-semibold">{item.risk_id}</span>
            <Badge tone={tone}>{formatBadge(item.review_level)}</Badge>
            {item.badges.map((badge) => (
              <span key={badge} className="rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
                {formatBadge(badge)}
              </span>
            ))}
          </div>
          <div className="mt-2 text-sm font-medium">{item.failure_mode}</div>
          <p className="mt-1 text-sm leading-6 text-slate-600">{item.reason}</p>
        </div>
        <div className="min-w-56 text-sm leading-6">
          <div>
            <span className="font-semibold">Reviewer:</span> {item.required_reviewer_type.join(", ")}
          </div>
          <div>
            <span className="font-semibold">Next action:</span> {item.next_action}
          </div>
        </div>
      </div>
    </div>
  );
}

function formatBadge(value: string) {
  const labels: Record<string, string> = {
    INPUT_INCOMPLETE: "Input incomplete",
    READY_FOR_PLAUSIBILITY_CHECK: "Ready for check",
    PLAUSIBILITY_PASS: "Plausibility pass",
    PLAUSIBILITY_PARTIAL: "Plausibility partial",
    PLAUSIBILITY_FAIL: "Plausibility fail",
    EVIDENCE_MISSING: "Evidence missing",
    SME_REQUIRED: "SME required",
    QA_REQUIRED: "QA required",
    AUTHOR_OPS_ACTION: "Author/Ops action",
    LEVEL_0_BASELINE_UNCHANGED: "Level 0",
    LEVEL_1_QUICK_CHECK: "Level 1 quick check",
    LEVEL_2_TARGETED_SME_REVIEW: "Level 2 targeted SME",
    LEVEL_3_FULL_SME_QA_REVIEW: "Level 3 full SME/QA"
  };
  return labels[value] ?? value.replaceAll("_", " ").toLowerCase();
}

function GaugeMetric({ label, value, max, suffix, tone }: { label: string; value: number; max: number; suffix: string; tone: "slate" | "teal" }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const color = tone === "teal" ? "#137c78" : "#4b5563";
  return (
    <div className="rounded-xl bg-slate-50 p-4">
      <div
        className="mx-auto grid h-28 w-28 place-items-center rounded-full"
        style={{
          background: `conic-gradient(${color} ${pct}%, #e6ecef ${pct}% 100%)`
        }}
      >
        <div className="grid h-20 w-20 place-items-center rounded-full bg-white shadow-inner">
          <div className="text-center">
            <div className="text-2xl font-semibold tracking-[-0.03em] text-slate-950">
              {value.toFixed(suffix === "%" ? 0 : 1)}
              <span className="text-sm">{suffix}</span>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-3 text-center text-[11px] font-medium uppercase tracking-[0.16em] text-slate-500">{label}</div>
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
      <div className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">{title}</div>
      {items.length > 0 ? (
        <ul className="mt-2 space-y-2 text-sm leading-5 text-slate-700">
          {items.map((item) => (
            <li key={item} className="rounded-md bg-slate-50 px-3 py-2">
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <div className="mt-2 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-500">{empty}</div>
      )}
    </div>
  );
}

function Table({ headers, rows }: { headers: string[]; rows: Array<Array<React.ReactNode>> }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-line text-xs uppercase tracking-[0.08em] text-slate-500">
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
