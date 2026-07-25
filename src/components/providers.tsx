/**
 * App Providers
 *
 * Client-side providers for internationalization.
 * Renders a stable tree — no mounted gate, so the app is not
 * remounted after hydration. Saved preferences are loaded
 * inside the providers themselves.
 */

"use client";

import { type ReactNode } from "react";
import { I18nProvider } from "@/src/lib/i18n";

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return <I18nProvider>{children}</I18nProvider>;
}
