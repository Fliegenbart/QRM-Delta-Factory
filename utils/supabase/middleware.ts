import { createServerClient } from "@supabase/ssr";
import { type NextRequest, NextResponse } from "next/server";
import { hasSupabaseMiddlewareConfig } from "@/utils/supabase/config";
import {
  isProtectedReviewApiPath,
  isProtectedReviewPath,
  isReviewAuthRequired
} from "@/utils/supabase/review-auth";

export async function updateSession(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const mustProtectReviewRoute =
    isProtectedReviewPath(pathname) && isReviewAuthRequired();

  if (!hasSupabaseMiddlewareConfig()) {
    if (mustProtectReviewRoute) {
      return reviewAuthFailureResponse(
        request,
        "Review authentication is not configured.",
        503
      );
    }
    return NextResponse.next({ request });
  }

  let supabaseResponse = NextResponse.next({
    request: {
      headers: request.headers
    }
  });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        }
      }
    }
  );

  const hasSupabaseSessionCookie = request.cookies
    .getAll()
    .some((cookie) => cookie.name.startsWith("sb-"));
  if (!hasSupabaseSessionCookie && mustProtectReviewRoute) {
    return reviewAuthFailureResponse(request, "Authentication required.", 401);
  }

  if (hasSupabaseSessionCookie) {
    const {
      data: { user }
    } = await supabase.auth.getUser();
    if (mustProtectReviewRoute && !user) {
      return reviewAuthFailureResponse(request, "Authentication required.", 401);
    }
  }

  return supabaseResponse;
}

function reviewAuthFailureResponse(request: NextRequest, message: string, status: 401 | 503) {
  const headers = { "cache-control": "no-store" };
  if (isProtectedReviewApiPath(request.nextUrl.pathname)) {
    return NextResponse.json({ error: message }, { status, headers });
  }

  // Protected page route + missing session: send the visitor to the login page
  // and remember where they were headed. (The 503 "not configured" case keeps the
  // plain message, since login would not help there.)
  if (status === 401) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.search = "";
    loginUrl.searchParams.set("redirect", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl, { headers });
  }

  return new NextResponse(message, {
    status,
    headers: {
      ...headers,
      "content-type": "text/plain; charset=utf-8"
    }
  });
}
