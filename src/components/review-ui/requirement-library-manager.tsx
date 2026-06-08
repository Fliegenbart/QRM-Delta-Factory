"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { AlertCircle, CheckCircle2, FileUp, Loader2, RefreshCcw, UploadCloud } from "lucide-react";
import { userFacingReviewLoadError, type Requirement, type RequirementLibraryOverview } from "@/src/lib/review-ui";

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
        count: 0,
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
        cache: "no-store",
      });
      const payload = await readPayload(response);
      setOverview(payload.overview);
      setState("ready");
    } catch (caught) {
      setState("error");
      setError(caught instanceof Error ? caught.message : "Regelwerk konnte nicht geladen werden.");
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
        body: formData,
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
      <section className="surface p-5">
        <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
          <div>
            <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
              Regelwerk
            </div>
            <h2 className="mt-2 text-[20px] font-medium leading-snug text-[var(--text-primary)]">
              Aktives Regelwerk und Quelldokumente
            </h2>
            <p className="mt-2 max-w-2xl text-[13px] leading-relaxed text-[var(--text-secondary)]">
              Dieses Regelwerk wird zur Bewertung neuer Prüffälle herangezogen. Importiere eine Regelwerk-Datei, um sie zu aktivieren.
            </p>
          </div>
          <aside className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] p-4">
            <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
              Aktives Regelwerk
            </div>
            {state === "loading" && !currentSet ? (
              <div className="mt-3 flex items-center gap-2 text-[13px] text-[var(--text-secondary)]">
                <Loader2 className="h-4 w-4 animate-spin" />
                Regelwerk wird geladen...
              </div>
            ) : state === "error" && !currentSet ? (
              <div className="mt-3 text-[13px] leading-6 text-[var(--text-secondary)]">
                {error ? userFacingReviewLoadError(error).title : "Regelwerk konnte nicht geladen werden"}
              </div>
            ) : currentSet ? (
              <div className="mt-2 space-y-1.5">
                <div className="text-[14px] font-medium text-[var(--text-primary)]">
                  {currentSet.name}
                </div>
                <div className="mono text-[12px] text-[var(--text-secondary)]">
                  v{currentSet.version}
                </div>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  <Pill>{currentSet.requirements.length} Regeln</Pill>
                  <Pill>{sourceDocuments.length} Quellen</Pill>
                  <Pill>{activeCount} aktiv</Pill>
                </div>
              </div>
            ) : (
              <div className="mt-2 text-[13px] text-[var(--text-secondary)]">
                Noch kein Regelwerk geladen.
              </div>
            )}
          </aside>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-[340px_1fr]">
        <div className="surface p-5">
          <div className="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            Regelwerk importieren
          </div>
          <label className="mt-3 flex min-h-[130px] cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-[var(--border-strong)] bg-[var(--surface-secondary)] px-4 py-5 text-center transition-colors hover:bg-[var(--brand-soft)] hover:border-[var(--brand)]">
            <UploadCloud className="h-7 w-7 text-[var(--brand)]" aria-hidden />
            <span className="mt-2 text-[13px] font-medium text-[var(--text-primary)]">
              JSON oder YAML auswählen
            </span>
            <span className="mt-0.5 text-[11px] text-[var(--text-tertiary)]">
              Eine Regelwerk-Datei pro Import
            </span>
            <input
              className="sr-only"
              type="file"
              accept=".json,.yaml,.yml,application/json,text/yaml,application/x-yaml"
              onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            />
          </label>
          {selectedFile ? (
            <div className="mt-3 flex items-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-3 py-1.5 text-[13px] text-[var(--text-primary)]">
              <FileUp className="h-3.5 w-3.5 text-[var(--brand)]" aria-hidden />
              <span className="mono truncate text-[12px]">{selectedFile.name}</span>
            </div>
          ) : null}
          <button
            type="button"
            onClick={uploadLibrary}
            disabled={!selectedFile || state === "uploading"}
            className="mt-3 inline-flex h-9 w-full items-center justify-center gap-2 rounded-md bg-[var(--brand)] px-3 text-[13px] font-medium text-white hover:bg-[var(--brand-strong)] disabled:cursor-not-allowed disabled:bg-[var(--border-strong)] disabled:text-[var(--text-tertiary)]"
          >
            {state === "uploading" ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <CheckCircle2 className="h-3.5 w-3.5" />
            )}
            Importieren und aktivieren
          </button>
          {error ? (
            <div className="mt-3 flex items-start gap-2 rounded-md border border-[color:var(--severity-critical)] bg-[var(--severity-critical-soft)] px-3 py-2 text-[12px] leading-relaxed text-[var(--severity-critical)]">
              <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <span>{userFacingReviewLoadError(error).message}</span>
            </div>
          ) : null}
        </div>

        <div className="surface p-5">
          <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
                Quelldokumente
              </div>
              <p className="mt-1 text-[12px] leading-relaxed text-[var(--text-secondary)]">
                Dokumente, aus denen Regeln in der aktiven Bibliothek stammen.
              </p>
            </div>
            <button
              type="button"
              onClick={loadOverview}
              className="inline-flex h-8 items-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-2.5 text-[12px] text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)]"
            >
              <RefreshCcw className="h-3 w-3" aria-hidden />
              Aktualisieren
            </button>
          </div>

          <div className="mt-3 space-y-1.5">
            {sourceDocuments.length === 0 ? (
              <EmptyLine text="Noch keine Quelldokumente gefunden." />
            ) : (
              sourceDocuments.map((source) => (
                <div
                  key={`${source.name}:${source.version}`}
                  className="grid gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-3 py-2 text-[12px] md:grid-cols-[1fr_auto_auto] md:items-center"
                >
                  <span className="font-medium text-[var(--text-primary)]">{source.name}</span>
                  <span className="mono text-[var(--text-tertiary)]">v{source.version}</span>
                  <span className="text-[var(--text-tertiary)]">{source.count} Regeln</span>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      <section className="surface p-5">
        <div className="flex items-center justify-between">
          <div className="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            Regeln
          </div>
          {currentSet ? (
            <span className="mono text-[11px] text-[var(--text-tertiary)]">
              {currentSet.requirements.length} insgesamt
            </span>
          ) : null}
        </div>
        <div className="mt-3 space-y-1.5">
          {(currentSet?.requirements ?? []).slice(0, 12).map((requirement) => (
            <RequirementRow key={requirement.requirement_id} requirement={requirement} />
          ))}
          {(currentSet?.requirements.length ?? 0) > 12 ? (
            <div className="mt-2 text-[12px] text-[var(--text-tertiary)]">
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

const criticalityTone: Record<string, { fg: string; bg: string }> = {
  critical: { fg: "var(--severity-critical)", bg: "var(--severity-critical-soft)" },
  high: { fg: "var(--severity-major)", bg: "var(--severity-major-soft)" },
  medium: { fg: "var(--severity-minor)", bg: "var(--severity-minor-soft)" },
  low: { fg: "var(--text-tertiary)", bg: "var(--surface-secondary)" },
  informational: { fg: "var(--text-tertiary)", bg: "var(--surface-secondary)" },
};

function RequirementRow({ requirement }: { requirement: Requirement }) {
  const tone = criticalityTone[requirement.criticality] ?? criticalityTone.low;
  return (
    <article className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] px-3 py-2.5">
      <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
        <div className="min-w-0">
          <div className="mono text-[12px] text-[var(--text-tertiary)]">
            {requirement.requirement_id}
          </div>
          <div className="mt-0.5 text-[13px] font-medium text-[var(--text-primary)]">
            {humanRequirementName(requirement)}
          </div>
          <p className="mt-1 text-[12px] leading-relaxed text-[var(--text-secondary)]">
            {requirement.requirement_text}
          </p>
        </div>
        <span
          className="self-start rounded-full px-2 py-[2px] text-[11px] font-medium"
          style={{ color: tone.fg, backgroundColor: tone.bg }}
        >
          {displayCriticality(requirement.criticality)}
        </span>
      </div>
      <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-[var(--text-tertiary)]">
        <span className="mono">
          {requirement.source_name} · §{requirement.section}
        </span>
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
    informational: "Info",
  };
  return labels[value] ?? value;
}

function Pill({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex rounded-full bg-[var(--surface-primary)] border border-[var(--border-default)] px-2 py-[2px] text-[11px] font-medium text-[var(--text-secondary)]">
      {children}
    </span>
  );
}

function EmptyLine({ text }: { text: string }) {
  return (
    <div className="rounded-md border border-dashed border-[var(--border-strong)] bg-[var(--surface-secondary)] px-3 py-4 text-[12px] text-[var(--text-tertiary)]">
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
