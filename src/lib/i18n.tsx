/**
 * Lightweight i18n System
 *
 * Simple, type-safe internationalization without heavy dependencies.
 * Supports DE/EN with easy extensibility.
 */

"use client";

import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

export type Locale = "de" | "en";

// Translation keys - fully typed
export const translations = {
  // Navigation
  "nav.dashboard": { de: "Dashboard", en: "Dashboard" },
  "nav.delta": { de: "Delta-Analyse", en: "Delta Analysis" },
  "nav.documents": { de: "Dokumente", en: "Documents" },
  "nav.riskRegister": { de: "Risikoregister", en: "Risk Register" },
  "nav.review": { de: "Review", en: "Review" },
  "nav.settings": { de: "Einstellungen", en: "Settings" },
  "nav.category.analysis": { de: "Analyse", en: "Analysis" },
  "nav.category.data": { de: "Daten", en: "Data" },
  "nav.category.workflow": { de: "Workflow", en: "Workflow" },
  "nav.category.system": { de: "System", en: "System" },

  // Dashboard
  "dashboard.title": { de: "QRM Delta Engine", en: "QRM Delta Engine" },
  "dashboard.subtitle": { de: "Pharmazeutisches Qualit\u00e4tsrisikomanagement", en: "Pharmaceutical Quality Risk Management" },
  "dashboard.welcome": { de: "Willkommen zur\u00fcck", en: "Welcome back" },
  "dashboard.lastAnalysis": { de: "Letzte Analyse", en: "Last Analysis" },
  "dashboard.openRisks": { de: "Offene Risiken", en: "Open Risks" },
  "dashboard.criticalItems": { de: "Kritische Punkte", en: "Critical Items" },
  "dashboard.compliance": { de: "Compliance-Status", en: "Compliance Status" },

  // Multi-Agent Analysis
  "agent.title": { de: "Multi-Agent Risikoanalyse", en: "Multi-Agent Risk Analysis" },
  "agent.subtitle": { de: "KI-gest\u00fctzte Analyse mit GPT-4o und Claude", en: "AI-powered analysis with GPT-4o and Claude" },
  "agent.start": { de: "Analyse starten", en: "Start Analysis" },
  "agent.running": { de: "Analyse l\u00e4uft...", en: "Analysis running..." },
  "agent.author": { de: "Autor", en: "Author" },
  "agent.author.desc": { de: "Erstellt initiale Risikobewertungen aus Quelldokumenten", en: "Creates initial risk assessments from source documents" },
  "agent.critic": { de: "Kritiker", en: "Critic" },
  "agent.critic.desc": { de: "Pr\u00fcft Behauptungen, findet L\u00fccken und Inkonsistenzen", en: "Verifies claims, finds gaps and inconsistencies" },
  "agent.resolver": { de: "Vermittler", en: "Resolver" },
  "agent.resolver.desc": { de: "Mediiert Konflikte, trifft finale Entscheidungen", en: "Mediates conflicts, makes final decisions" },
  "agent.workflow": { de: "Agent-Workflow", en: "Agent Workflow" },
  "agent.conversation": { de: "Agent-Konversation", en: "Agent Conversation" },
  "agent.results": { de: "Analyseergebnisse", en: "Analysis Results" },
  "agent.iterations": { de: "Iterationen", en: "Iterations" },
  "agent.findings": { de: "Findings", en: "Findings" },
  "agent.processingTime": { de: "Verarbeitungszeit", en: "Processing Time" },
  "agent.cost": { de: "Kosten", en: "Cost" },

  // Risk Items
  "risk.title": { de: "Risiko-Items", en: "Risk Items" },
  "risk.rpn": { de: "RPN-Score", en: "RPN Score" },
  "risk.severity": { de: "Schweregrad", en: "Severity" },
  "risk.probability": { de: "Wahrscheinlichkeit", en: "Probability" },
  "risk.detectability": { de: "Entdeckbarkeit", en: "Detectability" },
  "risk.mitigation": { de: "Mitigation", en: "Mitigation" },
  "risk.status": { de: "Status", en: "Status" },
  "risk.blocker": { de: "Blocker", en: "Blocker" },
  "risk.concern": { de: "Bedenken", en: "Concern" },
  "risk.suggestion": { de: "Vorschlag", en: "Suggestion" },

  // Gaps
  "gaps.title": { de: "Identifizierte L\u00fccken", en: "Identified Gaps" },
  "gaps.empty": { de: "Keine L\u00fccken gefunden", en: "No gaps found" },

  // Documents
  "docs.title": { de: "Quelldokumente", en: "Source Documents" },
  "docs.type": { de: "Dokumenttyp", en: "Document Type" },
  "docs.file": { de: "Datei", en: "File" },
  "docs.format": { de: "Format", en: "Format" },
  "docs.excerpt": { de: "Auszug", en: "Excerpt" },

  // Review
  "review.title": { de: "Review-Workflow", en: "Review Workflow" },
  "review.pending": { de: "Ausstehend", en: "Pending" },
  "review.approved": { de: "Genehmigt", en: "Approved" },
  "review.rejected": { de: "Abgelehnt", en: "Rejected" },
  "review.export": { de: "Exportieren", en: "Export" },

  // Actions
  "action.save": { de: "Speichern", en: "Save" },
  "action.cancel": { de: "Abbrechen", en: "Cancel" },
  "action.delete": { de: "L\u00f6schen", en: "Delete" },
  "action.edit": { de: "Bearbeiten", en: "Edit" },
  "action.view": { de: "Ansehen", en: "View" },
  "action.download": { de: "Herunterladen", en: "Download" },
  "action.upload": { de: "Hochladen", en: "Upload" },
  "action.refresh": { de: "Aktualisieren", en: "Refresh" },

  // Status
  "status.loading": { de: "Wird geladen...", en: "Loading..." },
  "status.error": { de: "Fehler aufgetreten", en: "Error occurred" },
  "status.success": { de: "Erfolgreich", en: "Success" },
  "status.idle": { de: "Bereit", en: "Ready" },
  "status.running": { de: "L\u00e4uft", en: "Running" },
  "status.completed": { de: "Abgeschlossen", en: "Completed" },

  // Theme
  "theme.light": { de: "Hell", en: "Light" },
  "theme.dark": { de: "Dunkel", en: "Dark" },
  "theme.system": { de: "System", en: "System" },

  // Settings
  "settings.title": { de: "Einstellungen", en: "Settings" },
  "settings.language": { de: "Sprache", en: "Language" },
  "settings.theme": { de: "Erscheinungsbild", en: "Appearance" },
  "settings.notifications": { de: "Benachrichtigungen", en: "Notifications" },

  // Misc
  "misc.noData": { de: "Keine Daten verf\u00fcgbar", en: "No data available" },
  "misc.showMore": { de: "Mehr anzeigen", en: "Show more" },
  "misc.showLess": { de: "Weniger anzeigen", en: "Show less" },
  "misc.of": { de: "von", en: "of" },
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
