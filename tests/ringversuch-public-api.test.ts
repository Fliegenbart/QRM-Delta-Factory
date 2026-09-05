import { describe, expect, it } from "vitest";
import { GET } from "@/app/api/ringversuch/route";

describe("public ringversuch API", () => {
  it("publishes qualification summaries without internal case or token raw data", async () => {
    const response = await GET();
    const payload = await response.json();

    expect(response.status).toBe(200);
    expect(payload.runs.length).toBeGreaterThan(0);

    const firstRun = payload.runs[0];
    expect(firstRun).toMatchObject({
      id: expect.any(String),
      run: expect.any(Object),
      aggregate: expect.any(Object),
    });
    expect(firstRun).not.toHaveProperty("cases");
    expect(firstRun.aggregate).not.toHaveProperty("tokens_by_provider");
    expect(JSON.stringify(payload)).not.toContain("risk_statement");
    expect(JSON.stringify(payload)).not.toContain("expected_reviewer_finding");
  });

  it("keeps the corpus and assessor shape in the published run meta", async () => {
    const response = await GET();
    const payload = await response.json();
    const blind = payload.runs.find((run: { id: string }) => run.id.startsWith("20260824_072027"));

    // Without these fields the landing page cannot tell a blind measurement
    // from a regression check -- and called the blind result a regression.
    expect(blind.run.corpus).toBe("blind3");
    expect(blind.run.assessor_mode).toBe("narrow");
    expect(blind.run.case_count).toBe(8);
  });
});
