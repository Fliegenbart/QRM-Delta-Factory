import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repoRoot = process.cwd();

describe("sales and production readiness surface", () => {
  it("adds a customer pilot surface to the product navigation", () => {
    const appShell = readFileSync(join(repoRoot, "src/components/app-shell.tsx"), "utf8");
    const i18n = readFileSync(join(repoRoot, "src/lib/i18n.tsx"), "utf8");

    expect(appShell).toContain('"kundenpilot"');
    expect(appShell).toContain("SalesReadinessPanel");
    expect(i18n).toContain('"nav.customerPilot"');
  });

  it("states the sellable offer with human-review and evidence-first boundaries", () => {
    const panel = readFileSync(
      join(repoRoot, "src/components/review-ui/sales-readiness-panel.tsx"),
      "utf8"
    );

    expect(panel).toContain("Unterlagen rein. Prüfmappe raus. Mensch entscheidet.");
    expect(panel).toContain("Kein Befund ohne belastbaren Beleg");
    expect(panel).toContain("Kunden-Blindtest-Kit");
    expect(panel).toContain("Go/No-Go-Gates");
    expect(panel).toContain("Datenroute");
    expect(panel).not.toContain("Freigabe möglich");
    expect(panel).not.toContain("garantiert compliant");
  });
});
