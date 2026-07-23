"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { createClient } from "@/utils/supabase/client";

export function SignOutButton() {
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);

  async function signOut() {
    if (isSigningOut) return;

    setIsSigningOut(true);
    try {
      await createClient().auth.signOut({ scope: "local" });
    } finally {
      // A local redirect also clears the UI if the Supabase request was interrupted.
      router.replace("/login");
      router.refresh();
    }
  }

  return (
    <button
      type="button"
      onClick={signOut}
      disabled={isSigningOut}
      className="inline-flex h-9 items-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-[13px] font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)] disabled:cursor-wait disabled:opacity-60"
    >
      <LogOut className="h-4 w-4" aria-hidden />
      <span>{isSigningOut ? "Abmeldung …" : "Abmelden"}</span>
    </button>
  );
}
