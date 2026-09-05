import { describe, expect, it } from "vitest";
import { describePipelineTiming, describeStepProgress } from "@/src/components/review-ui/pipeline-run-status";
import { pipelineStepLabel } from "@/src/lib/review-ui";

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


describe("describeStepProgress", () => {
  it("reads the requirement count out of the detail inside the long step", () => {
    expect(describeStepProgress({ step_index: 12, step_count: 13, detail: "Anforderung 13 von 26 beurteilt" })).toEqual({
      percent: 88
    });
    expect(describeStepProgress({ step_index: 1, step_count: 13, detail: null }).percent).toBe(3);
    // Never claims completion while still running.
    expect(describeStepProgress({ step_index: 13, step_count: 13, detail: "26 von 26" }).percent).toBe(97);
  });

  it("names every pipeline step in the reviewer's words", () => {
    expect(pipelineStepLabel("requirement_coverage_review")).toBe("Anforderung für Anforderung urteilen");
    expect(pipelineStepLabel("some_new_step")).toBe("some new step");
  });
});
