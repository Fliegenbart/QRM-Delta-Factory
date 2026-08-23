import case01 from "@/src/data/demo-cases/case_01.json";
import case08 from "@/src/data/demo-cases/case_08.json";
import case09 from "@/src/data/demo-cases/case_09.json";
import type { RequirementCoverageReport } from "@/src/lib/review-ui";

/**
 * The example cases are real engine output, not fixtures: each JSON is one
 * case of the proficiency-test corpus as a finished goldstandard run left it,
 * exported by backend/app/evals/export_demo_cases.py. Nothing in the report
 * is edited by hand -- the point of showing them is that a prospect sees
 * exactly what the tool produces, planted errors and all.
 *
 * Server-side only by usage: the JSON is large, and the pages that render it
 * are server components, so it never reaches a client bundle.
 */
export type DemoCase = {
  id: string;
  slug: string;
  title: string;
  area: string;
  trigger: string;
  product: string;
  dosage_form: string;
  batch: string;
  documents: { file_name: string; label: string }[];
  run: {
    started_at: string | null;
    stack: string | null;
    assessor_mode: string | null;
    model: string | null;
    engine_version: string | null;
    pipeline_status: string | null;
    model_calls: number;
    failed_model_calls: number;
    input_tokens: number;
    output_tokens: number;
  };
  gold: { planted: number; found: number; decoys: number; decoys_passed: number };
  report: RequirementCoverageReport;
};

export const demoCases: DemoCase[] = [case01, case08, case09] as unknown as DemoCase[];

export function demoCaseHref(demoCase: Pick<DemoCase, "slug">): string {
  return `/review-ui/demo/${demoCase.slug}`;
}

export function findDemoCase(slug: string): DemoCase | undefined {
  return demoCases.find((demoCase) => demoCase.slug === slug);
}

/** "2 von 2 eingebauten Fehlern gefunden" -- the honest one-liner per card. */
export function demoCaseScoreline(demoCase: Pick<DemoCase, "gold">): string {
  const { planted, found } = demoCase.gold;
  return `${found} von ${planted} eingebauten Fehlern gefunden`;
}

const STACK_LABELS: Record<string, string> = {
  hetzner: "lokaler Stack, Qwen auf dem EU-Server",
  local: "lokaler Stack, Qwen auf dem EU-Server",
  cascade: "Kaskade: lokal gelesen, extern nachgeprüft",
  mixed: "Cloud-Stack, Claude und GPT",
  cloud: "Cloud-Stack, Claude und GPT"
};

/** How the example came to be, in one paragraph a prospect can check. */
export function demoCaseProvenance(demoCase: DemoCase): string {
  const date = demoCase.run.started_at
    ? new Date(demoCase.run.started_at).toLocaleDateString("de-DE", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric"
      })
    : "unbekanntem Datum";
  const stack = STACK_LABELS[demoCase.run.stack ?? ""] ?? demoCase.run.stack ?? "unbekannter Stack";
  const mode =
    demoCase.run.assessor_mode === "narrow"
      ? "pro Anforderung erst Belege gesucht, dann geurteilt"
      : "sechs Anforderungen je Aufruf beurteilt";
  const calls =
    demoCase.run.failed_model_calls > 0
      ? `${demoCase.run.model_calls} Modellaufrufe, ${demoCase.run.failed_model_calls} davon fehlgeschlagen und als solche ausgewiesen`
      : `${demoCase.run.model_calls} Modellaufrufe, keiner fehlgeschlagen`;
  const decoys =
    demoCase.gold.decoys > 0
      ? ` ${demoCase.gold.decoys === 1 ? "Die eine Täuschstelle" : `Die ${demoCase.gold.decoys} Täuschstellen`} — auffällig formuliert, aber regelkonform — ${
          demoCase.gold.decoys_passed === demoCase.gold.decoys
            ? "blieb ohne Fehlalarm."
            : `lösten ${demoCase.gold.decoys - demoCase.gold.decoys_passed} Fehlalarm(e) aus.`
        }`
      : "";
  return (
    `Echter Prüflauf vom ${date} mit ${demoCase.run.model ?? "unbekanntem Modell"} (${stack}; ${mode}; ${calls}). ` +
    `Die Unterlagen sind synthetisch und stammen aus dem Ringversuch-Korpus: ${demoCase.gold.planted} Fehler wurden absichtlich eingebaut, ` +
    `${demoCase.gold.found} davon hat das System gefunden.${decoys} Nichts an diesem Bericht wurde nachbearbeitet.`
  );
}
