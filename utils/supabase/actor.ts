import { NextResponse } from "next/server";
import { isConfiguredReviewTenant } from "@/src/lib/review-runtime-config";
import {
  authorizeReviewOperation,
  getLocalReviewFallbackActor,
  resolveReviewActorFromClaims,
  type ReviewActor,
  type ReviewOperation
} from "@/utils/supabase/authorization";
import { hasSupabaseMiddlewareConfig } from "@/utils/supabase/config";
import { createClient } from "@/utils/supabase/server";

export async function authorizeReviewApiRequest(
  operation: ReviewOperation
): Promise<{ actor: ReviewActor } | { response: NextResponse }> {
  if (!hasSupabaseMiddlewareConfig()) {
    const localActor = getLocalReviewFallbackActor();
    if (!localActor) {
      return { response: authorizationFailure("Review authentication is not configured.", 503) };
    }
    return authorizeActor(localActor, operation);
  }

  const supabase = await createClient();
  const {
    data: { user },
    error
  } = await supabase.auth.getUser();
  if (error || !user) {
    return { response: authorizationFailure("Authentication required.", 401) };
  }

  const actor = resolveReviewActorFromClaims(user);
  if (!actor) {
    return { response: authorizationFailure("Valid review role and tenant claims are required.", 403) };
  }
  if (!isConfiguredReviewTenant(actor.tenantId)) {
    return { response: authorizationFailure("Actor tenant is not authorized for this backend.", 403) };
  }
  return authorizeActor(actor, operation);
}

function authorizeActor(
  actor: ReviewActor,
  operation: ReviewOperation
): { actor: ReviewActor } | { response: NextResponse } {
  const authorization = authorizeReviewOperation(actor, operation);
  return authorization.allowed
    ? { actor }
    : { response: authorizationFailure(authorization.reason, 403) };
}

function authorizationFailure(message: string, status: 401 | 403 | 503): NextResponse {
  return NextResponse.json(
    { error: message },
    { status, headers: { "cache-control": "no-store" } }
  );
}
