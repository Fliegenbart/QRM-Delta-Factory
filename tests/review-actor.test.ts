import { describe, expect, it } from "vitest";
import {
  authorizeReviewOperation,
  resolveReviewActorFromClaims
} from "@/utils/supabase/authorization";

describe("review actor claims", () => {
  it("uses the stable Supabase user id and signed app metadata claims", () => {
    expect(resolveReviewActorFromClaims({
      id: "5f6de2cb-56f0-4d3f-9b5d-2b1ed4ad1b5c",
      email: "szilard.gruenwald@example.com",
      app_metadata: { qrm_role: "reviewer", qrm_tenant_id: "tenant_acme" },
      user_metadata: { qrm_role: "system-owner", qrm_tenant_id: "tenant_other" }
    })).toMatchObject({
      userId: "5f6de2cb-56f0-4d3f-9b5d-2b1ed4ad1b5c",
      role: "reviewer",
      tenantId: "tenant_acme"
    });
  });

  it("fails closed for mutable, missing, or unauthorized claims", () => {
    expect(resolveReviewActorFromClaims({
      id: "user_1",
      app_metadata: {},
      user_metadata: { qrm_role: "system-owner", qrm_tenant_id: "tenant_acme" }
    })).toBeNull();
    const actor = resolveReviewActorFromClaims({
      id: "user_1",
      app_metadata: { role: "viewer", tenant_id: "tenant_acme" }
    });
    expect(actor && authorizeReviewOperation(actor, "delete-document-set").allowed).toBe(false);
  });
});
