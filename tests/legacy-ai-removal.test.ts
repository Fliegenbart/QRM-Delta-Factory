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
});
