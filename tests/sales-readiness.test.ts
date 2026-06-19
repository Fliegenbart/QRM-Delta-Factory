import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repoRoot = process.cwd();

describe("sales and production readiness surface", () => {
  it("keeps the sales/customer-pilot surface out of the public navigation", () => {
    const appShell = readFileSync(join(repoRoot, "src/components/app-shell.tsx"), "utf8");
    const i18n = readFileSync(join(repoRoot, "src/lib/i18n.tsx"), "utf8");

    expect(appShell).not.toContain('"kundenpilot"');
    expect(appShell).not.toContain("SalesReadinessPanel");
    expect(i18n).not.toContain('"nav.category.commercial"');
    expect(i18n).not.toContain('"nav.customerPilot"');
  });

  it("keeps the internal sales panel copy conservative if reused later", () => {
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
