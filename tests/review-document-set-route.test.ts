import { describe, expect, it, vi } from "vitest";

vi.mock("@/utils/supabase/actor", () => ({
  resolveReviewActor: vi.fn(async () => "user_qrm_author")
}));

vi.mock("@/src/lib/review-api", () => {
  class ReviewApiError extends Error {
    constructor(message: string, readonly status?: number) {
      super(message);
    }
  }

  return {
    ReviewApiError,
    createDocumentSet: vi.fn()
  };
});

import { POST } from "@/app/api/review-ui/document-sets/route";
import { ReviewApiError, createDocumentSet } from "@/src/lib/review-api";

describe("review document set route", () => {
  it("preserves backend validation errors instead of converting them to 502", async () => {
    vi.mocked(createDocumentSet).mockRejectedValueOnce(
      new ReviewApiError("uploaded_by may only contain letters, numbers, underscores, or hyphens", 422)
    );

    const response = await POST(
      new Request("https://qrm.example.test/api/review-ui/document-sets", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          declaredDocumentType: "deviation_package",
          declaredProcessArea: "aseptic_filling"
        })
      })
    );

    expect(response.status).toBe(422);
    await expect(response.json()).resolves.toEqual({
      error: "uploaded_by may only contain letters, numbers, underscores, or hyphens"
    });
  });
});
