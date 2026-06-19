import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { selectOverviewRingversuchStats } from "@/src/lib/ringversuch-overview-stats";

describe("overview ringversuch stats", () => {
  it("shows the latest complete live run while also keeping the best confirmed complete run", () => {
    const stats = selectOverviewRingversuchStats({
      runs: [
        run("20260613_213023_live_hybrid", 24, 25, 11, 11, 0.928),
        run("20260613_210310_live_hybrid", 2, 2, 1, 1, 1),
        run("20260613_120754_live_hybrid", 25, 25, 11, 11, 0.91),
        run("20260610_065944_mock", 3, 25, 11, 11, 1, "mock"),
      ],
    });

    expect(stats.latest.sensitivityFound).toBe(24);
    expect(stats.latest.sensitivityTotal).toBe(25);
    expect(stats.latest.standDate).toBe("13.06.2026");
    expect(stats.best.sensitivityFound).toBe(25);
    expect(stats.best.sensitivityTotal).toBe(25);
    expect(stats.best.citationRate).toBe(0.91);
    expect(stats.hasBetterBestRun).toBe(true);
  });

  it("keeps the overview copy aligned with the consultant-facing qualification story", () => {
    const overview = readFileSync(
      join(process.cwd(), "src/components/review-ui/overview-landing.tsx"),
      "utf8"
    );

    expect(overview).toContain("Endlich eine KI, die nichts behauptet, was sie nicht belegen kann.");
    expect(overview).toContain("Blindtest starten");
    expect(overview).toContain("Wie es funktioniert");
    expect(overview).toContain("Was das Tool ist.");
    expect(overview).toContain("Warum KI-Risikoanalysen bisher gescheitert sind");
    expect(overview).toContain("Belegt, oder es kommt gar nicht durch.");
    expect(overview).toContain("Still, wo nichts ist.");
    expect(overview).toContain("Sagt, wenn es nicht weiß.");
    expect(overview).toContain("Was es kann.");
    expect(overview).toContain("Eine CAPA mit dokumentierten Maßnahmen, aber offener Wirksamkeitsprüfung.");
    expect(overview).toContain("Was es nicht tut:");
    expect(overview).toContain("Wie es funktioniert — in drei Schritten.");
    expect(overview).toContain("Gemessen, nicht behauptet.");
    expect(overview).toContain("Vertrauen in Stufen — jede mit einem prüfbaren Kriterium.");
    expect(overview).toContain("Dies ist ein Prototyp.");
    expect(overview).toContain("Stand 11.06.2026");
    expect(overview).not.toContain("Der nächste Schritt gehört Ihnen.");
    expect(overview).not.toContain("Blindtest anfragen");
    expect(overview).not.toContain("Die Prüfung machen Sie.");
    expect(overview).not.toContain("Das Zusammentragen macht das Tool.");
    expect(overview).not.toContain("Der teuerste Teil eines Reviews ist der langweiligste.");
    expect(overview).not.toContain("Drei Gründe, warum das hier kein KI-Versprechen ist.");
    expect(overview).not.toContain("Welche KI hier arbeitet");
    expect(overview).not.toContain("Was das System ausdrücklich nicht tut");
    expect(overview).not.toContain("Mistral Large");
  });

  it("frames the ringversuch page as a precise evidence page", () => {
    const ringversuch = readFileSync(
      join(process.cwd(), "src/components/review-ui/ringversuch-dashboard.tsx"),
      "utf8"
    );

    expect(ringversuch).toContain("Was das System findet — und was nicht. Gemessen.");
    expect(ringversuch).toContain("So läuft der Ringversuch.");
    expect(ringversuch).toContain("Letzter abgeschlossener Lauf · Stand 11.06.2026");
    expect(ringversuch).toContain("Jeder Fall einzeln — auch der verfehlte.");
    expect(ringversuch).toContain("Was dieser Nachweis zeigt — und was noch nicht.");
    expect(ringversuch).toContain("nicht der beste ausgewählte");
    expect(ringversuch).toContain("Der eine verfehlte Fall ist unten dokumentiert.");
    expect(ringversuch).not.toContain("verkaufsfähigen Kennzahlen");
  });
});

function run(
  id: string,
  found: number,
  total: number,
  decoysPassed: number,
  decoysTotal: number,
  citationRate: number | null,
  mode = "live"
) {
  return {
    id,
    run: { mode },
    aggregate: {
      sensitivity: { found, total },
      specificity_decoys: { passed: decoysPassed, total: decoysTotal },
      citation_precision: { rate: citationRate },
    },
  };
}
