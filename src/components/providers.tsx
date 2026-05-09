/**
 * App Providers
 *
 * Client-side providers for theme and internationalization.
 */

"use client";

import { type ReactNode, useEffect, useState } from "react";
import { I18nProvider, type Locale } from "@/src/lib/i18n";
import { ThemeProvider } from "@/src/lib/theme";

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  const [mounted, setMounted] = useState(false);
  const [initialLocale, setInitialLocale] = useState<Locale>("de");

  // Load saved preferences on mount
  useEffect(() => {
    const savedLocale = localStorage.getItem("pharma-qrm-locale") as Locale | null;
    if (savedLocale && (savedLocale === "de" || savedLocale === "en")) {
      setInitialLocale(savedLocale);
    }
    setMounted(true);
  }, []);

  // Prevent flash of wrong theme/locale
  if (!mounted) {
    return (
      <div className="no-transitions">
        {children}
      </div>
    );
  }

  return (
    <ThemeProvider defaultTheme="system">
      <I18nProvider defaultLocale={initialLocale}>
        {children}
      </I18nProvider>
    </ThemeProvider>
  );
}
