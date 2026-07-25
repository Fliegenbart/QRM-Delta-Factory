"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  FileUp,
  Loader2,
  UploadCloud,
  X
} from "lucide-react";
import { PipelineRunStatus } from "@/src/components/review-ui/pipeline-run-status";
import type { PipelineRun } from "@/src/lib/review-ui";

const documentTypes = [
  { value: "change_control_package", label: "Change Control" },
  { value: "deviation_package", label: "Abweichung" },
  { value: "capa_package", label: "CAPA" },
  { value: "audit_finding_package", label: "Audit-Finding" },
  { value: "periodic_review_package", label: "Periodic Review" }
];

const processAreas = [
  { value: "aseptic_filling", label: "Aseptische Abfüllung" },
  { value: "automated_visual_inspection", label: "Automatische Sichtprüfung" },
  { value: "cleaning_validation", label: "Reinigung" },
  { value: "qc_lab", label: "QC-Labor" },
  { value: "data_integrity", label: "Datenintegrität" },
  { value: "supplier_quality", label: "Lieferant/Material" },
  { value: "computerized_system", label: "Computergestütztes System" }
];

type IntakeStatus = "idle" | "creating" | "uploading" | "running" | "done" | "error";

type IntakeResult = {
  documentSetId: string;
  pipelineRun: PipelineRun;
};

function FieldLabel({
  label,
  helper,
  required = false
}: {
  label: string;
  helper: string;
  required?: boolean;
}) {
  return (
    <span className="block">
      <span className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
        {label}
        {required ? " *" : null}
      </span>
      <span className="mt-1 block text-[12px] normal-case tracking-normal text-[var(--text-secondary)]">
        {helper}
      </span>
    </span>
  );
}

export function IntakeUploader() {
  const [declaredDocumentType, setDeclaredDocumentType] = useState(documentTypes[0].value);
  const [declaredProcessArea, setDeclaredProcessArea] = useState(processAreas[0].value);
  const [uploadedBy, setUploadedBy] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [status, setStatus] = useState<IntakeStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [needsLogin, setNeedsLogin] = useState(false);
  const [result, setResult] = useState<IntakeResult | null>(null);

  const canSubmit = files.length > 0 && status !== "creating" && status !== "uploading" && status !== "running";
  const totalSize = useMemo(
    () => files.reduce((sum, file) => sum + file.size, 0),
    [files]
  );
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
    setNeedsLogin(false);
    setResult(null);

    try {
      const createResponse = await fetch("/api/review-ui/document-sets", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          declaredDocumentType,
          declaredProcessArea,
          ...(uploadedBy.trim() ? { uploadedBy: uploadedBy.trim() } : {})
        })
      });
      if (createResponse.status === 401) {
        setStatus("error");
        setNeedsLogin(true);
        return;
      }
      const created = await readJson(createResponse);
      const documentSetId = created.documentSet?.document_set_id;
      if (!documentSetId) {
        throw new Error("Der Prüffall wurde nicht angelegt.");
      }

      setStatus("uploading");
      for (const file of files) {
        const formData = new FormData();
        if (uploadedBy.trim()) formData.set("uploadedBy", uploadedBy.trim());
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
      if (!pipeline.pipelineRun?.pipeline_run_id) {
        throw new Error("Die Analyse wurde nicht angelegt.");
      }

      setResult({
        documentSetId,
        pipelineRun: pipeline.pipelineRun as PipelineRun
      });
      setStatus("done");
    } catch (caught) {
      setStatus("error");
      setError(caught instanceof Error ? caught.message : "Die Analyse konnte nicht gestartet werden.");
    }
  }

  return (
    <section className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4">
      <AgentActivityPopup
        status={status}
      />

      <div className="grid gap-3 md:grid-cols-3">
        <label className="block">
          <FieldLabel label="Anlass" helper="Was ist der Auslöser?" required />
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
          <FieldLabel label="Prozessbereich" helper="Wo passiert es?" required />
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
          <FieldLabel label="Bearbeiter" helper="optional, fürs Protokoll" />
          <input
            className="mt-2 h-10 w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-[13px] text-[var(--text-primary)] outline-none ring-[var(--brand-ring)] transition focus:ring-4"
            value={uploadedBy}
            onChange={(event) => setUploadedBy(event.target.value)}
            placeholder="Name oder Kürzel"
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
          onChange={(event) => {
            addFiles(event.target.files);
            // Reset so the same file can be selected again after removal.
            event.target.value = "";
          }}
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

      {needsLogin ? (
        <div className="mt-4 flex flex-col gap-2 rounded-md border border-[var(--border-strong)] bg-[var(--surface-secondary)] px-4 py-3 text-sm">
          <span className="font-semibold text-[var(--text-primary)]">Bitte zuerst anmelden</span>
          <span className="leading-6 text-[var(--text-secondary)]">
            Der Prüf-Arbeitsbereich ist geschützt. Melden Sie sich an, um Unterlagen
            hochzuladen und die Prüfmappe zu erstellen.
          </span>
          <Link
            href="/login?redirect=/"
            className="mt-1 inline-flex h-9 w-fit items-center rounded-md bg-[var(--brand)] px-4 text-[13px] font-medium text-white hover:bg-[var(--brand-strong)]"
          >
            Anmelden
          </Link>
        </div>
      ) : null}

      {error ? (
        <div className="mt-4 flex items-start gap-3 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-800">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      ) : null}

      {result ? (
        <div className="mt-4 space-y-3">
          <PipelineRunStatus
            documentSetId={result.documentSetId}
            initialPipelineRun={result.pipelineRun}
          />
          <Link className="inline-flex rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-4 py-2 text-sm font-semibold text-[var(--text-primary)]" href={`/review-ui/document-sets/${result.documentSetId}`}>
            Prüffall öffnen
          </Link>
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
          className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-[var(--brand)] px-5 text-sm font-semibold text-white transition hover:bg-[var(--brand-strong)] disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-500"
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
  status
}: {
  status: IntakeStatus;
}) {
  const visible = status === "creating" || status === "uploading";
  if (!visible) return null;

  const copy = status === "uploading"
    ? { title: "Dokumente werden hochgeladen", description: "Die Dateien werden dem Prüffall zugeordnet." }
    : { title: "Prüffall wird angelegt", description: "Metadaten und Dokumenttyp werden vorbereitet." };

  return (
    <aside className="fixed bottom-4 left-4 z-40 w-[min(320px,calc(100vw-2rem))] rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-3 text-left shadow-lg shadow-slate-950/10 lg:w-[248px]">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 grid h-8 w-8 place-items-center rounded-md bg-[var(--brand-soft)] text-[var(--brand)]">
          <Loader2 className="h-4 w-4 animate-spin" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-sm font-semibold text-slate-950">
            {copy.title}
          </div>
          <div className="mt-1 text-sm text-slate-600">
            {copy.description}
          </div>
        </div>
      </div>
    </aside>
  );
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
