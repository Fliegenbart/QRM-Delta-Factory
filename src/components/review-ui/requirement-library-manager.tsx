"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { AlertCircle, CheckCircle2, FileUp, Loader2, UploadCloud } from "lucide-react";
import type { Requirement, RequirementLibraryOverview } from "@/src/lib/review-ui";

type LoadState = "loading" | "ready" | "uploading" | "error";

export function RequirementLibraryManager() {
  const [overview, setOverview] = useState<RequirementLibraryOverview | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    void loadOverview();
  }, []);

  const sourceDocuments = useMemo(() => {
    const requirements = overview?.requirementSet.requirements ?? [];
    const bySource = new Map<string, { name: string; version: string; count: number }>();
    for (const requirement of requirements) {
      const key = `${requirement.source_name}:${requirement.source_version}`;
      const current = bySource.get(key) ?? {
        name: requirement.source_name,
        version: requirement.source_version,
        count: 0
      };
      current.count += 1;
      bySource.set(key, current);
    }
    return Array.from(bySource.values()).sort((a, b) => a.name.localeCompare(b.name));
  }, [overview]);

  async function loadOverview() {
    setState("loading");
    setError(null);
    try {
      const response = await fetch("/api/review-ui/requirement-library", {
        cache: "no-store"
      });
      const payload = await readPayload(response);
      setOverview(payload.overview);
      setState("ready");
    } catch (caught) {
      setState("error");
      setError(caught instanceof Error ? caught.message : "Risikobibliothek konnte nicht geladen werden.");
    }
  }

  async function uploadLibrary() {
    if (!selectedFile) return;
    setState("uploading");
    setError(null);
    try {
      const formData = new FormData();
      formData.set("file", selectedFile);
      formData.set("importedBy", "quality_admin");
      const response = await fetch("/api/review-ui/requirement-library", {
        method: "POST",
        body: formData
      });
      const payload = await readPayload(response);
      setOverview(payload.overview);
      setSelectedFile(null);
      setState("ready");
    } catch (caught) {
      setState("error");
      setError(caught instanceof Error ? caught.message : "Import fehlgeschlagen.");
    }
  }

  const activeCount = overview?.activeRequirements.length ?? 0;
  const currentSet = overview?.requirementSet;

  return (
    <div className="space-y-5">
      <section className="premium-surface rounded-[24px] border border-black/10 p-6 dark:border-white/10">
        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-teal">
              Risikobibliothek
            </div>
            <h2 className="mt-3 text-4xl font-light leading-tight tracking-[-0.05em] text-ink dark:text-white md:text-5xl">
              Regeln hochladen. Prüfungen steuern.
            </h2>
            <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-600 dark:text-slate-300">
              Hier liegt das aktive Regelwerk, gegen das neue Prüffälle bewertet werden.
            </p>
          </div>
          <div className="rounded-2xl border border-black/10 bg-white/70 p-4 dark:border-white/10 dark:bg-slate-900/40">
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500 dark:text-slate-400">
              Aktives Regelwerk
            </div>
            {state === "loading" && !currentSet ? (
              <div className="mt-4 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                <Loader2 className="h-4 w-4 animate-spin" />
                Lädt...
              </div>
            ) : currentSet ? (
              <div className="mt-3 space-y-2">
                <div className="text-lg font-semibold text-slate-950 dark:text-white">
                  {currentSet.name}
                </div>
                <div className="text-sm text-slate-600 dark:text-slate-300">
                  Version {currentSet.version}
                </div>
                <div className="flex flex-wrap gap-2 pt-2">
                  <Pill>{currentSet.requirements.length} Regeln</Pill>
                  <Pill>{sourceDocuments.length} Quelldokumente</Pill>
                  <Pill>{activeCount} aktiv</Pill>
                </div>
              </div>
            ) : (
              <div className="mt-3 text-sm text-slate-600 dark:text-slate-300">
                Noch kein Regelwerk geladen.
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[380px_1fr]">
        <div className="rounded-[20px] border border-black/10 bg-white/80 p-5 dark:border-white/10 dark:bg-slate-800/80">
          <div className="text-base font-semibold text-slate-950 dark:text-white">
            Bibliothek importieren
          </div>
          <label className="mt-4 flex min-h-[150px] cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-teal-500/45 bg-teal-500/[0.045] px-4 py-6 text-center">
            <UploadCloud className="h-8 w-8 text-teal" />
            <span className="mt-3 text-sm font-semibold text-slate-950 dark:text-white">
              JSON oder YAML auswählen
            </span>
            <span className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Ein RequirementSet pro Datei
            </span>
            <input
              className="sr-only"
              type="file"
              accept=".json,.yaml,.yml,application/json,text/yaml,application/x-yaml"
              onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            />
          </label>
          {selectedFile ? (
            <div className="mt-3 flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-700 dark:bg-slate-900/50 dark:text-slate-200">
              <FileUp className="h-4 w-4 text-teal" />
              <span className="truncate">{selectedFile.name}</span>
            </div>
          ) : null}
          <button
            type="button"
            onClick={uploadLibrary}
            disabled={!selectedFile || state === "uploading"}
            className="mt-4 inline-flex h-10 w-full items-center justify-center gap-2 rounded-xl bg-teal px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-500 dark:disabled:bg-slate-700"
          >
            {state === "uploading" ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
            Importieren und aktivieren
          </button>
          {error ? (
            <div className="mt-4 flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-500/30 dark:bg-red-950/30 dark:text-red-100">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          ) : null}
        </div>

        <div className="rounded-[20px] border border-black/10 bg-white/80 p-5 dark:border-white/10 dark:bg-slate-800/80">
          <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-base font-semibold text-slate-950 dark:text-white">
                Quelldokumente
              </div>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                Dokumente, aus denen Regeln in der aktiven Bibliothek stammen.
              </p>
            </div>
            <button
              type="button"
              onClick={loadOverview}
              className="h-9 rounded-xl border border-black/10 bg-white px-3 text-sm font-semibold text-slate-700 dark:border-white/10 dark:bg-slate-900 dark:text-slate-200"
            >
              Aktualisieren
            </button>
          </div>

          <div className="mt-4 space-y-2">
            {sourceDocuments.length === 0 ? (
              <EmptyLine text="Noch keine Quelldokumente gefunden." />
            ) : (
              sourceDocuments.map((source) => (
                <div key={`${source.name}:${source.version}`} className="grid gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-white/10 dark:bg-slate-900/45 md:grid-cols-[1fr_auto_auto] md:items-center">
                  <span className="font-semibold text-slate-900 dark:text-white">{source.name}</span>
                  <span className="text-slate-500 dark:text-slate-400">Version {source.version}</span>
                  <span className="text-slate-500 dark:text-slate-400">{source.count} Regeln</span>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      <section className="rounded-[20px] border border-black/10 bg-white/80 p-5 dark:border-white/10 dark:bg-slate-800/80">
        <div className="text-base font-semibold text-slate-950 dark:text-white">
          Regeln
        </div>
        <div className="mt-4 space-y-2">
          {(currentSet?.requirements ?? []).slice(0, 12).map((requirement) => (
            <RequirementRow key={requirement.requirement_id} requirement={requirement} />
          ))}
          {(currentSet?.requirements.length ?? 0) > 12 ? (
            <div className="text-sm text-slate-500 dark:text-slate-400">
              + {(currentSet?.requirements.length ?? 0) - 12} weitere Regeln
            </div>
          ) : null}
          {currentSet && currentSet.requirements.length === 0 ? (
            <EmptyLine text="Das aktive Regelwerk enthält noch keine Regeln." />
          ) : null}
        </div>
      </section>
    </div>
  );
}

function RequirementRow({ requirement }: { requirement: Requirement }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-white/10 dark:bg-slate-900/45">
      <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="font-semibold text-slate-900 dark:text-white">
            {humanRequirementName(requirement)}
          </div>
          <div className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">
            {requirement.requirement_text}
          </div>
        </div>
        <Pill>{displayCriticality(requirement.criticality)}</Pill>
      </div>
      <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-400">
        <span>{requirement.source_name} · Abschnitt {requirement.section}</span>
        <span>{requirement.required_evidence.length} Pflichtnachweise</span>
      </div>
    </article>
  );
}

function humanRequirementName(requirement: Requirement) {
  return requirement.requirement_id
    .replace(/^req_/, "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function displayCriticality(value: string) {
  const labels: Record<string, string> = {
    critical: "Kritisch",
    high: "Hoch",
    medium: "Mittel",
    low: "Niedrig",
    informational: "Info"
  };
  return labels[value] ?? value;
}

function Pill({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-900 dark:text-slate-200">
      {children}
    </span>
  );
}

function EmptyLine({ text }: { text: string }) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 px-4 py-5 text-sm text-slate-500 dark:border-white/10 dark:text-slate-400">
      {text}
    </div>
  );
}

async function readPayload(response: Response) {
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
