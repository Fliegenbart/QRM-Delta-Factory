"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  FileUp,
  Loader2,
  UploadCloud,
  X
} from "lucide-react";
import type { PipelineModelManifestItem } from "@/src/lib/review-ui";

const documentTypes = [
  { value: "change_control_package", label: "Change Control" },
  { value: "deviation_package", label: "Abweichung" },
  { value: "capa_package", label: "CAPA" },
  { value: "audit_finding_package", label: "Audit Finding" },
  { value: "periodic_review_package", label: "Periodic Review" }
];

const processAreas = [
  { value: "aseptic_filling", label: "Aseptische Abfüllung" },
  { value: "automated_visual_inspection", label: "Automatische Sichtprüfung" },
  { value: "cleaning_validation", label: "Reinigung" },
  { value: "qc_lab", label: "QC Labor" },
  { value: "data_integrity", label: "Datenintegrität" },
  { value: "supplier_quality", label: "Lieferant / Material" },
  { value: "computerized_system", label: "Computergestütztes System" }
];

type IntakeStatus = "idle" | "creating" | "uploading" | "running" | "done" | "error";

type IntakeResult = {
  documentSetId: string;
  pipelineStatus?: string;
  failedStep?: string | null;
  modelManifest: PipelineModelManifestItem[];
};

const expectedAgentRuns = [
  {
    role: "Prüffall anlegen",
    action: "Metadaten und Dokumenttyp werden vorbereitet"
  },
  {
    role: "Unterlagen ordnen",
    action: "Quellen werden dem Fall zugeordnet"
  },
  {
    role: "Prüfpunkte finden",
    action: "Aussagen, Risiken und Regelwerksbezüge werden gesammelt"
  },
  {
    role: "Nachweise prüfen",
    action: "Quellen und Zitate werden abgeglichen"
  },
  {
    role: "Prüfmappe bauen",
    action: "Lücken und nächste QA-Schritte werden sichtbar gemacht"
  }
] as const;

function resultCopy(status?: string, failedStep?: string | null) {
  if (status === "failed") {
    return {
      title: "Der Prüffall wurde angelegt, aber die automatische Analyse ist fehlgeschlagen.",
      description:
        failedStep
          ? `Die Prüffälle zeigen deine hochgeladenen Unterlagen. Die Analyse ist beim Schritt "${failedStep}" stehen geblieben.`
          : "Die Prüffälle zeigen deine hochgeladenen Unterlagen. Die Prüfmappe zeigt erst dann Prüfpunkte und fehlende Nachweise, wenn die Analyse erfolgreich durchgelaufen ist.",
      tone: "warning" as const
    };
  }

  return {
    title: "Die Prüfmappe wird vorbereitet.",
    description:
      "Die Prüffälle zeigen die hochgeladenen Unterlagen. Die Prüfmappe zeigt die daraus erstellten Prüfpunkte, Quellen und fehlenden Nachweise.",
    tone: "success" as const
  };
}

export function IntakeUploader() {
  const [declaredDocumentType, setDeclaredDocumentType] = useState(documentTypes[0].value);
  const [declaredProcessArea, setDeclaredProcessArea] = useState(processAreas[0].value);
  const [uploadedBy, setUploadedBy] = useState("qrm_author");
  const [files, setFiles] = useState<File[]>([]);
  const [status, setStatus] = useState<IntakeStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IntakeResult | null>(null);
  const [activeAgentIndex, setActiveAgentIndex] = useState(0);

  const canSubmit = files.length > 0 && status !== "creating" && status !== "uploading" && status !== "running";
  const totalSize = useMemo(
    () => files.reduce((sum, file) => sum + file.size, 0),
    [files]
  );
  const resultState = result ? resultCopy(result.pipelineStatus, result.failedStep) : null;

  useEffect(() => {
    if (status !== "running") {
      setActiveAgentIndex(0);
      return;
    }

    const timer = window.setInterval(() => {
      setActiveAgentIndex((current) => (current + 1) % expectedAgentRuns.length);
    }, 1800);
    return () => window.clearInterval(timer);
  }, [status]);

  function addFiles(nextFiles: FileList | null) {
    if (!nextFiles) return;
    setFiles((current) => {
      const byName = new Map(current.map((file) => [`${file.name}:${file.size}`, file]));
      Array.from(nextFiles).forEach((file) => byName.set(`${file.name}:${file.size}`, file));
      return Array.from(byName.values());
    });
    setError(null);
  }

  function removeFile(fileToRemove: File) {
    setFiles((current) => current.filter((file) => file !== fileToRemove));
  }

  async function submit() {
    if (!canSubmit) return;
    setStatus("creating");
    setError(null);
    setResult(null);

    try {
      const createResponse = await fetch("/api/review-ui/document-sets", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          declaredDocumentType,
          declaredProcessArea,
          uploadedBy
        })
      });
      const created = await readJson(createResponse);
      const documentSetId = created.documentSet?.document_set_id;
      if (!documentSetId) {
        throw new Error("Der Prüffall wurde nicht angelegt.");
      }

      setStatus("uploading");
      for (const file of files) {
        const formData = new FormData();
        formData.set("uploadedBy", uploadedBy);
        formData.set("file", file);
        const uploadResponse = await fetch(`/api/review-ui/document-sets/${encodeURIComponent(documentSetId)}/documents`, {
          method: "POST",
          body: formData
        });
        await readJson(uploadResponse);
      }

      setStatus("running");
      const pipelineResponse = await fetch(`/api/review-ui/document-sets/${encodeURIComponent(documentSetId)}/pipeline-runs`, {
        method: "POST"
      });
      const pipeline = await readJson(pipelineResponse);

      setResult({
        documentSetId,
        pipelineStatus: pipeline.pipelineRun?.status,
        failedStep: pipeline.pipelineRun?.failed_step,
        modelManifest: Array.isArray(pipeline.pipelineRun?.model_manifest)
          ? pipeline.pipelineRun.model_manifest
          : []
      });
      setStatus("done");
    } catch (caught) {
      setStatus("error");
      setError(caught instanceof Error ? caught.message : "Die Analyse konnte nicht gestartet werden.");
    }
  }

  return (
    <section className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4 dark:border-white/10">
      <AgentActivityPopup
        status={status}
        activeAgentIndex={activeAgentIndex}
        modelManifest={result?.modelManifest ?? []}
      />

      <div className="grid gap-3 md:grid-cols-3">
        <label className="block">
          <span className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
            Anlass
          </span>
          <select
            className="mt-2 h-10 w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-[13px] text-[var(--text-primary)] outline-none ring-[var(--brand-ring)] transition focus:ring-4"
            value={declaredDocumentType}
            onChange={(event) => setDeclaredDocumentType(event.target.value)}
          >
            {documentTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
            Prozessbereich
          </span>
          <select
            className="mt-2 h-10 w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-[13px] text-[var(--text-primary)] outline-none ring-[var(--brand-ring)] transition focus:ring-4"
            value={declaredProcessArea}
            onChange={(event) => setDeclaredProcessArea(event.target.value)}
          >
            {processAreas.map((area) => (
              <option key={area.value} value={area.value}>
                {area.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
            Bearbeiter
          </span>
          <input
            className="mt-2 h-10 w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-[13px] text-[var(--text-primary)] outline-none ring-[var(--brand-ring)] transition focus:ring-4"
            value={uploadedBy}
            onChange={(event) => setUploadedBy(event.target.value)}
          />
        </label>
      </div>

      <label
        className="mt-4 flex min-h-[132px] cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-[var(--border-strong)] bg-[var(--surface-secondary)] px-5 py-6 text-center transition hover:border-[var(--brand)] hover:bg-[var(--brand-soft)] focus-within:ring-4 focus-within:ring-[var(--brand-ring)]"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          addFiles(event.dataTransfer.files);
        }}
      >
        <UploadCloud className="h-8 w-8 text-[var(--brand)]" />
        <span className="mt-3 text-[15px] font-medium text-[var(--text-primary)]">
          Dateien hier ablegen oder auswählen
        </span>
        <span className="mt-1 text-[13px] leading-6 text-[var(--text-secondary)]">
          Mehrere Dokumente sind möglich. Die Originaldateien bleiben die Quelle.
        </span>
        <input
          className="sr-only"
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md,.csv,text/plain,text/markdown,text/csv,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={(event) => addFiles(event.target.files)}
        />
      </label>

      {files.length > 0 ? (
        <div className="mt-4 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] p-3">
          <div className="mb-2 flex items-center justify-between text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
            <span>{files.length} Datei{files.length === 1 ? "" : "en"}</span>
            <span>{formatBytes(totalSize)}</span>
          </div>
          <div className="space-y-2">
            {files.map((file) => (
              <div key={`${file.name}:${file.size}`} className="flex items-center justify-between gap-3 rounded-md border border-[var(--border-muted)] bg-[var(--surface-primary)] px-3 py-2 text-[13px]">
                <span className="flex min-w-0 items-center gap-2">
                  <FileUp className="h-4 w-4 shrink-0 text-[var(--brand)]" />
                  <span className="truncate">{file.name}</span>
                </span>
                <button
                  type="button"
                  onClick={() => removeFile(file)}
                  className="grid h-8 w-8 shrink-0 place-items-center rounded-md text-[var(--text-tertiary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)]"
                  aria-label={`${file.name} entfernen`}
                  disabled={status === "uploading" || status === "running"}
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {error ? (
        <div className="mt-4 flex items-start gap-3 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-800 dark:border-red-500/30 dark:bg-red-950/30 dark:text-red-100">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      ) : null}

      {result && resultState ? (
        <div className={`mt-4 rounded-md border px-4 py-4 ${
          resultState.tone === "warning"
            ? "border-amber-400/45 bg-amber-50 text-amber-950 dark:border-amber-400/30 dark:bg-amber-950/25 dark:text-amber-50"
            : "border-[var(--brand)] bg-[var(--brand-soft)]"
        }`}>
          <div className="flex items-start gap-3">
            {resultState.tone === "warning" ? (
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600 dark:text-amber-300" />
            ) : (
              <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-[var(--brand)]" />
            )}
            <div>
              <div className="font-semibold text-[var(--text-primary)]">
                {resultState.title}
              </div>
              <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                {resultState.description}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <Link className="rounded-md bg-[var(--brand)] px-4 py-2 text-sm font-semibold text-white" href={`/review-ui/document-sets/${result.documentSetId}`}>
                  Prüffälle öffnen
                </Link>
                {resultState.tone === "success" ? (
                  <Link className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-4 py-2 text-sm font-semibold text-[var(--text-primary)]" href={`/review-ui/document-sets/${result.documentSetId}/review-pack`}>
                    Prüfmappe öffnen
                  </Link>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      ) : null}

      <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
        {files.length === 0 && status === "idle" ? (
          <p className="text-sm text-[var(--text-tertiary)]">
            Bitte zuerst mindestens eine Datei auswählen.
          </p>
        ) : null}
        <button
          type="button"
          onClick={submit}
          disabled={!canSubmit}
          className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-[var(--brand)] px-5 text-sm font-semibold text-white transition hover:bg-[var(--brand-strong)] disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-500 dark:disabled:bg-slate-700"
        >
          {status === "creating" || status === "uploading" || status === "running" ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <ArrowRight className="h-4 w-4" />
          )}
          {buttonLabel(status)}
        </button>
      </div>
    </section>
  );
}

function AgentActivityPopup({
  status,
  activeAgentIndex,
  modelManifest
}: {
  status: IntakeStatus;
  activeAgentIndex: number;
  modelManifest: PipelineModelManifestItem[];
}) {
  const visible = status === "creating" || status === "uploading" || status === "running" || modelManifest.length > 0;
  if (!visible) return null;

  const activeAgent = expectedAgentRuns[activeAgentIndex] ?? expectedAgentRuns[0];
  const isRunning = status === "creating" || status === "uploading" || status === "running";

  return (
    <aside className="fixed bottom-4 left-4 z-40 w-[min(320px,calc(100vw-2rem))] rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-3 text-left shadow-lg shadow-slate-950/10 lg:w-[248px]">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 grid h-8 w-8 place-items-center rounded-md bg-[var(--brand-soft)] text-[var(--brand)]">
          {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
        </div>
        <div className="min-w-0 flex-1">
          {isRunning ? (
            <>
              <div className="text-sm font-semibold text-slate-950 dark:text-white">
                {activeAgent.role}
              </div>
              <div className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                {activeAgent.action}
              </div>
            </>
          ) : (
            <>
              <div className="mt-1 text-sm font-semibold text-slate-950 dark:text-white">
                Modellverteilung gespeichert
              </div>
              <div className="mt-2 space-y-1">
                {modelManifest.slice(0, 4).map((entry) => (
                  <div key={`${entry.agent_role}-${entry.model_run_id ?? entry.configured_model_id}`} className="flex min-w-0 items-center justify-between gap-2 text-xs">
                    <span className="min-w-0 truncate text-slate-600 dark:text-slate-300">{displayAgentRole(entry.agent_role)}</span>
                    <span className="max-w-[128px] shrink-0 truncate rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-200 lg:max-w-[112px]">
                      {displayModelName(entry)}
                    </span>
                  </div>
                ))}
                {modelManifest.length > 4 ? (
                  <div className="text-xs text-slate-500 dark:text-slate-400">
                    + {modelManifest.length - 4} weitere Modellläufe gespeichert
                  </div>
                ) : null}
              </div>
            </>
          )}
        </div>
      </div>
    </aside>
  );
}

function displayAgentRole(role: string) {
  return role
    .replace("Reviewer", "")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace("GMPData", "GMP Data")
    .trim();
}

function displayModelName(entry: PipelineModelManifestItem) {
  if (entry.configured_model_id && entry.configured_model_id !== "not_recorded") {
    return entry.configured_model_id;
  }
  return entry.model_name;
}

async function readJson(response: Response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      typeof payload.error === "string"
        ? payload.error
        : "Der Vorgang konnte nicht abgeschlossen werden."
    );
  }
  return payload;
}

function buttonLabel(status: IntakeStatus) {
  if (status === "creating") return "Prüffall anlegen";
  if (status === "uploading") return "Dokumente hochladen";
  if (status === "running") return "Analyse starten";
  if (status === "done") return "Weitere Analyse starten";
  return "Prüfung starten";
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
