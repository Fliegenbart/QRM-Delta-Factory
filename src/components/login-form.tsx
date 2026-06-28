"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, Lock } from "lucide-react";
import { createClient } from "@/utils/supabase/client";

export function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const redirectTo = sanitizeRedirect(params.get("redirect"));

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const supabase = createClient();
      const { error: signInError } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });
      if (signInError) {
        setError("Anmeldung fehlgeschlagen. Bitte E-Mail und Passwort prüfen.");
        setLoading(false);
        return;
      }
      router.replace(redirectTo);
      router.refresh();
    } catch {
      setError("Anmeldung ist derzeit nicht möglich. Bitte später erneut versuchen.");
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-sm">
      <div className="mb-6 flex items-center gap-2.5">
        <div
          className="grid h-8 w-8 place-items-center rounded-md bg-[var(--brand)] text-[13px] font-semibold text-white"
          aria-hidden
        >
          Q
        </div>
        <span className="text-[15px] font-semibold text-[var(--text-primary)]">Pharma QRM</span>
      </div>

      <h1 className="text-[22px] font-semibold tracking-[-0.01em] text-[var(--text-primary)]">
        Anmelden
      </h1>
      <p className="mt-1.5 text-[14px] leading-6 text-[var(--text-secondary)]">
        Der Prüf-Arbeitsbereich ist geschützt. Melden Sie sich an, um Unterlagen
        hochzuladen und die Prüfmappe zu erstellen.
      </p>

      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <div>
          <label htmlFor="email" className="mb-1.5 block text-[13px] font-medium text-[var(--text-primary)]">
            E-Mail
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="name@firma.de"
            className="h-11 w-full rounded-lg border border-[var(--border-strong)] bg-[var(--surface-primary)] px-3.5 text-[14px] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] outline-none focus:border-[var(--brand)]"
          />
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block text-[13px] font-medium text-[var(--text-primary)]">
            Passwort
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="h-11 w-full rounded-lg border border-[var(--border-strong)] bg-[var(--surface-primary)] px-3.5 text-[14px] text-[var(--text-primary)] outline-none focus:border-[var(--brand)]"
          />
        </div>

        {error ? (
          <p
            role="alert"
            className="rounded-lg border border-[var(--severity-critical)] bg-[var(--severity-critical-soft)] px-3.5 py-2.5 text-[13px] leading-5 text-[var(--severity-critical)]"
          >
            {error}
          </p>
        ) : null}

        <button
          type="submit"
          disabled={loading}
          className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-[var(--brand)] text-[14px] font-medium text-white transition-colors hover:bg-[var(--brand-strong)] disabled:opacity-60"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              Anmeldung läuft …
            </>
          ) : (
            <>
              <Lock className="h-4 w-4" aria-hidden />
              Anmelden
            </>
          )}
        </button>
      </form>

      <p className="mt-6 text-[12px] leading-5 text-[var(--text-tertiary)]">
        Noch kein Zugang? Ihr Konto wird von Pharma QRM angelegt — wenden Sie sich an
        Ihren Ansprechpartner.
      </p>
    </div>
  );
}

function sanitizeRedirect(value: string | null): string {
  // Only allow same-origin absolute paths to avoid open-redirects.
  if (value && value.startsWith("/") && !value.startsWith("//")) {
    return value;
  }
  return "/";
}
