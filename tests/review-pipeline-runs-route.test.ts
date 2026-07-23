import { describe, expect, it, vi } from "vitest";

vi.mock("@/utils/supabase/actor", () => ({
  authorizeReviewApiRequest: vi.fn(async () => ({
    actor: { userId: "user_qrm_author", role: "reviewer", tenantId: "tenant_example_pharma", source: "supabase" }
  }))
}));

vi.mock("@/src/lib/review-api", () => {
  class ReviewApiError extends Error {
    constructor(message: string, readonly status?: number) {
      super(message);
    }
  }

  return {
    ReviewApiError,
    getLatestPipelineRun: vi.fn(),
    runPipeline: vi.fn()
  };
});

import { GET } from "@/app/api/review-ui/document-sets/[id]/pipeline-runs/route";
import { getLatestPipelineRun } from "@/src/lib/review-api";

describe("review pipeline status route", () => {
  it("returns the current pipeline run without caching it", async () => {
    vi.mocked(getLatestPipelineRun).mockResolvedValueOnce({
      pipeline_run_id: "prun_status_demo",
      document_set_id: "ds_status_demo",
      status: "running",
      started_at: "2026-07-23T10:00:00.000Z",
      config_version: "v1",
      model_manifest: []
    });

    const response = await GET(
      new Request("https://qrm.example.test/api/review-ui/document-sets/ds_status_demo/pipeline-runs"),
      { params: Promise.resolve({ id: "ds_status_demo" }) }
    );

    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
    await expect(response.json()).resolves.toMatchObject({
      pipelineRun: { pipeline_run_id: "prun_status_demo", status: "running" }
    });
  });
});
