import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/utils/supabase/config", () => ({
  hasSupabaseMiddlewareConfig: vi.fn(() => true)
}));

vi.mock("@/utils/supabase/server", () => ({
  createClient: vi.fn()
}));

import { resolveReviewActor } from "@/utils/supabase/actor";
import { createClient } from "@/utils/supabase/server";

describe("resolveReviewActor", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("uses the stable Supabase user id instead of an email address", async () => {
    vi.mocked(createClient).mockResolvedValue({
      auth: {
        getUser: vi.fn(async () => ({
          data: {
            user: {
              id: "5f6de2cb-56f0-4d3f-9b5d-2b1ed4ad1b5c",
              email: "szilard.gruenwald@example.com"
            }
          }
        }))
      }
    } as never);

    await expect(resolveReviewActor("qrm_author")).resolves.toBe(
      "5f6de2cb-56f0-4d3f-9b5d-2b1ed4ad1b5c"
    );
  });
});
