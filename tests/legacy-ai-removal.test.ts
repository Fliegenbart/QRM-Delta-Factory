import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repoRoot = process.cwd();

describe("legacy frontend AI cleanup", () => {
  it("removes retired TypeScript ensemble and document-verifier agents", () => {
    const retiredPaths = [
      "app/api/ai/analyze",
      "app/api/ai/verify",
      "app/api/ai/delta",
      "app/api/ai/red-team",
      "app/api/ai/ensemble",
      "app/api/ai",
      "src/lib/agents",
      "src/lib/llm-adapter.ts",
      "src/components/document-upload.tsx"
    ];

    for (const retiredPath of retiredPaths) {
      expect(existsSync(join(repoRoot, retiredPath)), `${retiredPath} should be removed`).toBe(false);
    }
  });

  it("keeps AppShell focused on backend-first packages rather than legacy multi-agent analysis", () => {
    const appShell = readFileSync(join(repoRoot, "src/components/app-shell.tsx"), "utf8");

    expect(appShell).not.toContain("runMultiAgentAnalysis");
    expect(appShell).not.toContain("MultiAgentResult");
    expect(appShell).not.toContain("/api/ai/analyze");
    expect(appShell).not.toContain("DocumentUpload");
  });

  it("keeps the landing page free from redundant proof-flow explainer blocks", () => {
    const appShell = readFileSync(join(repoRoot, "src/components/app-shell.tsx"), "utf8");

    expect(appShell).not.toContain("KI-Entscheidung");
    expect(appShell).not.toContain("Quelle Pflicht");
    expect(appShell).not.toContain('Stat label="Prüfmappe"');
    expect(appShell).not.toContain("Letzter Schritt");
    expect(appShell).not.toContain("So arbeitet der Prüfflow");
    expect(appShell).not.toContain("Unterlagen laden");
    expect(appShell).not.toContain("Nachweise prüfen");
    expect(appShell).not.toContain("Prüfung fokussieren");
  });

  it("keeps the landing intro full-width and removes duplicate upload copy", () => {
    const appShell = readFileSync(join(repoRoot, "src/components/app-shell.tsx"), "utf8");
    const intakeUploader = readFileSync(join(repoRoot, "src/components/review-ui/intake-uploader.tsx"), "utf8");

    expect(appShell).not.toContain("lg:grid-cols-[0.86fr_1.14fr]");
    expect(intakeUploader).not.toContain("Lade die Unterlagen zur Änderung, Abweichung oder CAPA hoch.");
  });
});
