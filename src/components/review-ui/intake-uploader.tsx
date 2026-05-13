"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  FileUp,
  Loader2,
  ShieldCheck,
  UploadCloud,
  X
} from "lucide-react";

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
};

export function IntakeUploader() {
  const [declaredDocumentType, setDeclaredDocumentType] = useState(documentTypes[0].value);
  const [declaredProcessArea, setDeclaredProcessArea] = useState(processAreas[0].value);
  const [uploadedBy, setUploadedBy] = useState("qrm_author");
  const [files, setFiles] = useState<File[]>([]);
  const [status, setStatus] = useState<IntakeStatus>("idle");
  const [error, setError] = useState<string | null>(null);
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
        pipelineStatus: pipeline.pipelineRun?.status
      });
      setStatus("done");
    } catch (caught) {
      setStatus("error");
      setError(caught instanceof Error ? caught.message : "Die Analyse konnte nicht gestartet werden.");
    }
  }

  return (
    <section className="rounded-[22px] border border-black/10 bg-white/88 p-5 shadow-[0_24px_70px_rgba(15,23,42,0.08)] dark:border-white/10 dark:bg-slate-800/88">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full bg-teal-500/10 px-3 py-1 text-xs font-semibold text-teal-700 dark:text-teal-300">
            <ShieldCheck className="h-3.5 w-3.5" />
            Neuer Prüffall
          </div>
          <h2 className="mt-4 text-2xl font-semibold tracking-[-0.04em] text-ink dark:text-white">
            Dokumente hochladen
          </h2>
          <p className="mt-2 max-w-xl text-sm leading-6 text-slate-600 dark:text-slate-300">
            Lade die Unterlagen zur Änderung, Abweichung oder CAPA hoch. Das System erstellt daraus eine Prüfmappe mit Quellen, offenen Fragen und fehlenden Nachweisen.
          </p>
        </div>
        <div className="hidden rounded-xl border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600 dark:border-white/10 dark:text-slate-300 sm:block">
          PDF · DOCX · TXT · MD · CSV
        </div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Anlass
          </span>
          <select
            className="mt-2 h-11 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-ink outline-none ring-teal/20 transition focus:ring-4 dark:border-white/10 dark:bg-slate-900 dark:text-white"
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
          <span className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Prozessbereich
          </span>
          <select
            className="mt-2 h-11 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-ink outline-none ring-teal/20 transition focus:ring-4 dark:border-white/10 dark:bg-slate-900 dark:text-white"
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
          <span className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Bearbeiter
          </span>
          <input
            className="mt-2 h-11 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-ink outline-none ring-teal/20 transition focus:ring-4 dark:border-white/10 dark:bg-slate-900 dark:text-white"
            value={uploadedBy}
            onChange={(event) => setUploadedBy(event.target.value)}
          />
        </label>
      </div>

      <label
        className="mt-5 flex min-h-[150px] cursor-pointer flex-col items-center justify-center rounded-[18px] border border-dashed border-teal-500/45 bg-teal-500/[0.045] px-5 py-7 text-center transition hover:bg-teal-500/[0.075] focus-within:ring-4 focus-within:ring-teal/20"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          addFiles(event.dataTransfer.files);
        }}
      >
        <UploadCloud className="h-9 w-9 text-teal" />
        <span className="mt-3 text-base font-semibold text-ink dark:text-white">
          Dateien hier ablegen oder auswählen
        </span>
        <span className="mt-1 text-sm text-slate-600 dark:text-slate-300">
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
        <div className="mt-4 rounded-[14px] border border-slate-200 bg-slate-50/80 p-3 dark:border-white/10 dark:bg-slate-900/50">
          <div className="mb-2 flex items-center justify-between text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            <span>{files.length} Datei{files.length === 1 ? "" : "en"}</span>
            <span>{formatBytes(totalSize)}</span>
          </div>
          <div className="space-y-2">
            {files.map((file) => (
              <div key={`${file.name}:${file.size}`} className="flex items-center justify-between gap-3 rounded-xl bg-white px-3 py-2 text-sm dark:bg-slate-800">
                <span className="flex min-w-0 items-center gap-2">
                  <FileUp className="h-4 w-4 shrink-0 text-teal" />
                  <span className="truncate">{file.name}</span>
                </span>
                <button
                  type="button"
                  onClick={() => removeFile(file)}
                  className="grid h-8 w-8 shrink-0 place-items-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-700 dark:hover:text-white"
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
        <div className="mt-4 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-800 dark:border-red-500/30 dark:bg-red-950/30 dark:text-red-100">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      ) : null}

      {result ? (
        <div className="mt-4 rounded-xl border border-teal-500/25 bg-teal-500/[0.055] px-4 py-4">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-teal" />
            <div>
              <div className="font-semibold text-ink dark:text-white">Prüfmappe wird vorbereitet.</div>
              <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">
                Status: {result.pipelineStatus ?? "gestartet"}. Öffne die Fallakte oder die Prüfmappe.
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <Link className="rounded-xl bg-teal px-4 py-2 text-sm font-semibold text-white" href={`/review-ui/document-sets/${result.documentSetId}/review-pack`}>
                  Prüfmappe öffnen
                </Link>
                <Link className="rounded-xl border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink dark:border-white/10 dark:bg-slate-800 dark:text-white" href={`/review-ui/document-sets/${result.documentSetId}`}>
                  Fallakte öffnen
                </Link>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-xs leading-5 text-slate-500 dark:text-slate-400">
          Jede Aussage in der Prüfmappe braucht Quelle, Zitat und genaue Textstelle.
        </div>
        <button
          type="button"
          onClick={submit}
          disabled={!canSubmit}
          className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-teal px-5 text-sm font-semibold text-white shadow-sm transition hover:bg-teal-600 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-500 dark:disabled:bg-slate-700"
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
