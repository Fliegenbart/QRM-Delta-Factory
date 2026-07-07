import { hasSupabaseMiddlewareConfig } from "@/utils/supabase/config";
import { createClient } from "@/utils/supabase/server";

/**
 * Resolves the acting person for audit-relevant writes.
 *
 * When a Supabase session exists, the authenticated identity wins —
 * client-supplied names must not be able to spoof the audit trail.
 * Without Supabase (local demo mode) the provided fallback is used.
 */
export async function resolveReviewActor(fallback: string): Promise<string> {
  if (!hasSupabaseMiddlewareConfig()) return fallback;
  try {
    const supabase = await createClient();
    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (user) return user.email ?? user.id;
  } catch {
    // No session available (e.g. unauthenticated demo route) — keep fallback.
  }
  return fallback;
}
