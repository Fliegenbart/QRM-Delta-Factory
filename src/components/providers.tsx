/**
 * App Providers
 *
 * Client-side providers for theme and internationalization.
 * Renders a stable tree — no mounted gate, so the app is not
 * remounted after hydration. Theme flash is prevented by the
 * inline script in app/layout.tsx; saved preferences are loaded
 * inside the providers themselves.
 */

"use client";

import { type ReactNode } from "react";
import { I18nProvider } from "@/src/lib/i18n";
import { ThemeProvider } from "@/src/lib/theme";

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider defaultTheme="system">
      <I18nProvider>{children}</I18nProvider>
    </ThemeProvider>
  );
}
