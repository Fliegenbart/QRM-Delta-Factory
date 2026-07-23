import { describe, expect, it } from "vitest";
import { describePipelineTiming } from "@/src/components/review-ui/pipeline-run-status";

describe("describePipelineTiming", () => {
  it("shows a cautious remaining-time estimate while a normal analysis is running", () => {
    const timing = describePipelineTiming("2026-07-23T10:00:00.000Z", Date.parse("2026-07-23T10:02:00.000Z"));

    expect(timing).toMatchObject({
      elapsedSeconds: 120,
      waitingCopy: "Voraussichtlich noch ca. 3 Minuten."
    });
    expect(timing?.progressPercent).toBeGreaterThan(0);
    expect(timing?.progressPercent).toBeLessThan(94);
  });

  it("does not promise a completion time after the usual window", () => {
    const timing = describePipelineTiming("2026-07-23T10:00:00.000Z", Date.parse("2026-07-23T10:06:05.000Z"));

    expect(timing?.waitingCopy).toBe("Dauert länger als üblich – wird weiter verarbeitet.");
    expect(timing?.progressPercent).toBe(94);
  });
});
