import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { getSupabasePublicConfig } from "@/utils/supabase/config";

export const createClient = async () => {
  const cookieStore = await cookies();
  const { supabaseUrl, supabaseKey } = getSupabasePublicConfig();

  return createServerClient(supabaseUrl, supabaseKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          );
        } catch {
          // Server Components cannot always write cookies. Middleware refreshes sessions.
        }
      }
    }
  });
};
