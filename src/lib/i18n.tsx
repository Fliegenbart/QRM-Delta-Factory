/**
 * Lightweight i18n System
 *
 * Simple, type-safe internationalization without heavy dependencies.
 * Supports DE/EN with easy extensibility.
 */

"use client";

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";

export type Locale = "de" | "en";

// Translation keys - fully typed
export const translations = {
  // Navigation
  "nav.category.workspace": { de: "Arbeiten", en: "Work" },
  "nav.category.admin": { de: "Setup", en: "Setup" },
  "nav.category.howItWorks": { de: "Funktionsweise", en: "How it works" },
  "nav.dashboard": { de: "Start", en: "Start" },
  "nav.aiArchitecture": { de: "Wie die Prüfmappe entsteht", en: "How the review pack is built" },
  "nav.backendReview": { de: "Prüffälle", en: "Review cases" },
  "nav.riskLibrary": { de: "Regelwerk", en: "Rule set" },
  "nav.ringversuch": { de: "Ringversuch", en: "Proficiency test" },
  "nav.ueberblick": { de: "Überblick", en: "Overview" },

  // Theme
  "theme.light": { de: "Hell", en: "Light" },
  "theme.dark": { de: "Dunkel", en: "Dark" },
} as const;

export type TranslationKey = keyof typeof translations;

// Context
interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: TranslationKey) => string;
}

const I18nContext = createContext<I18nContextType | null>(null);

// Provider
export function I18nProvider({ children, defaultLocale = "de" }: { children: ReactNode; defaultLocale?: Locale }) {
  const [locale, setLocaleState] = useState<Locale>(defaultLocale);

  // Load persisted preference after hydration
  useEffect(() => {
    const saved = localStorage.getItem("pharma-qrm-locale");
    if (saved === "de" || saved === "en") {
      setLocaleState(saved);
    }
  }, []);

  const setLocale = useCallback((newLocale: Locale) => {
    setLocaleState(newLocale);
    // Persist preference
    if (typeof window !== "undefined") {
      localStorage.setItem("pharma-qrm-locale", newLocale);
    }
  }, []);

  const t = useCallback((key: TranslationKey): string => {
    const translation = translations[key];
    if (!translation) {
      console.warn(`Missing translation for key: ${key}`);
      return key;
    }
    return translation[locale];
  }, [locale]);

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

// Hook
export function useI18n() {
  const context = useContext(I18nContext);

  // Return safe defaults for SSR/static rendering
  if (!context) {
    return {
      locale: "de" as Locale,
      setLocale: () => {},
      t: (key: TranslationKey) => translations[key]?.de ?? key,
    };
  }
  return context;
}

// Standalone translation function (for use outside React)
export function translate(key: TranslationKey, locale: Locale): string {
  const translation = translations[key];
  if (!translation) return key;
  return translation[locale];
}
