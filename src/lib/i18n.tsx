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
  // Navigation Categories
  "nav.category.workspace": { de: "Arbeitsbereich", en: "Workspace" },
  "nav.category.riskAnalysis": { de: "Risikoanalyse", en: "Risk Analysis" },
  "nav.category.reviewQA": { de: "Review & QA", en: "Review & QA" },
  "nav.category.evidenceGaps": { de: "Evidenz & Lücken", en: "Evidence & Gaps" },
  "nav.category.output": { de: "Ausgabe", en: "Output" },
  "nav.category.admin": { de: "Administration", en: "Admin" },

  // Navigation Items
  "nav.dashboard": { de: "Dashboard", en: "Dashboard" },
  "nav.projects": { de: "Projekte", en: "Projects" },
  "nav.documents": { de: "Dokumente", en: "Documents" },
  "nav.sourceSnippets": { de: "Quellausschnitte", en: "Source Snippets" },
  "nav.riskLibrary": { de: "Risikobibliothek", en: "Risk Library" },
  "nav.triggerInput": { de: "Change/CAPA Eingabe", en: "Change/CAPA Input" },
  "nav.deltaAnalysis": { de: "Delta-Analyse", en: "Delta Analysis" },
  "nav.qrmMatrix": { de: "QRM-Matrix", en: "QRM Matrix" },
  "nav.reviewPackages": { de: "Review-Pakete", en: "Review Packages" },
  "nav.plausibilityChecks": { de: "Plausibilitätsprüfungen", en: "Plausibility Checks" },
  "nav.redTeamFindings": { de: "Red-Team Findings", en: "Red-Team Findings" },
  "nav.reviewQueue": { de: "Review-Warteschlange", en: "Review Queue" },
  "nav.approvals": { de: "Genehmigungen", en: "Approvals" },
  "nav.evidenceMap": { de: "Evidenzkarte", en: "Evidence Map" },
  "nav.gaps": { de: "Lücken", en: "Gaps" },
  "nav.exportPackage": { de: "Export-Paket", en: "Export Package" },
  "nav.validationPack": { de: "Validierungspaket", en: "Validation Pack" },
  "nav.auditTrail": { de: "Audit-Trail", en: "Audit Trail" },
  "nav.adminUsers": { de: "Admin/Benutzer", en: "Admin/Users" },

  // Header
  "header.workspace": { de: "Arbeitsbereich", en: "Workspace" },
  "header.auditTrailActive": { de: "Audit-Trail aktiv", en: "Audit Trail Active" },
  "header.localAuth": { de: "Lokale Auth", en: "Local auth" },
  "header.notifications": { de: "Benachrichtigungen", en: "Notifications" },
  "header.help": { de: "Hilfe", en: "Help" },
  "header.documentation": { de: "Dokumentation", en: "Documentation" },

  // Brand
  "brand.name": { de: "Pharma QRM", en: "Pharma QRM" },
  "brand.subtitle": { de: "Delta Factory", en: "Delta Factory" },
  "brand.tagline": { de: "Quellenverknüpfte Entwurfs-Risikopakete für qualifizierte menschliche Prüfung.", en: "Source-linked draft risk packages for qualified human review." },

  // Dashboard
  "dashboard.openHighGaps": { de: "Offene kritische Lücken", en: "Open high gaps" },
  "dashboard.level3Review": { de: "Level 3 Review", en: "Level 3 review" },
  "dashboard.aiDraftItems": { de: "KI-Entwurfspositionen", en: "AI draft items" },
  "dashboard.sourceSnippets": { de: "Quellausschnitte", en: "Source snippets" },
  "dashboard.riskBasedQueue": { de: "Risikobasierte Review-Warteschlange", en: "Risk-based human review queue" },
  "dashboard.openQueue": { de: "Warteschlange öffnen", en: "Open queue" },
  "dashboard.runMockAI": { de: "Mock-KI-Sicherheitsebenen ausführen", en: "Run mock AI safety layers" },
  "dashboard.runAuthorDelta": { de: "Author-KI Delta ausführen", en: "Run Author AI delta" },
  "dashboard.runPlausibility": { de: "Unabhängige Plausibilitätsprüfung", en: "Run independent plausibility check" },
  "dashboard.runRedTeam": { de: "Red-Team Risikofinder", en: "Run Red-Team missing-risk finder" },
  "dashboard.mockNote": { de: "Jeder Durchlauf nutzt nur MockLLMAdapter. Keine externe KI-API wird aufgerufen.", en: "Each run uses MockLLMAdapter only. No external AI API is called." },
  "dashboard.deltaSummary": { de: "Delta-Zusammenfassung", en: "Delta summary" },
  "dashboard.trigger": { de: "Auslöser", en: "Trigger" },
  "dashboard.mainConcern": { de: "Hauptbedenken", en: "Main concern" },
  "dashboard.routing": { de: "Routing", en: "Routing" },

  // Multi-Agent Analysis
  "agent.title": { de: "Multi-Agent Analyse", en: "Multi-Agent Analysis" },
  "agent.collaboration": { de: "GPT-4o + Claude Zusammenarbeit", en: "GPT-4o + Claude Collaboration" },
  "agent.description": { de: "Zwei KI-Systeme arbeiten zusammen: GPT-4o erstellt Risk-Drafts, Claude prüft kritisch auf Lücken und Fehler, dann überarbeitet GPT-4o basierend auf dem Feedback.", en: "Two AI systems work together: GPT-4o creates risk drafts, Claude critically reviews for gaps and errors, then GPT-4o revises based on feedback." },
  "agent.start": { de: "Multi-Agent Analyse starten", en: "Start Multi-Agent Analysis" },
  "agent.running": { de: "Agents arbeiten...", en: "Agents working..." },
  "agent.completed": { de: "Analyse abgeschlossen", en: "Analysis completed" },
  "agent.openPackages": { de: "Review Packages öffnen", en: "Open Review Packages" },
  "agent.error": { de: "Fehler", en: "Error" },
  "agent.author": { de: "Autor", en: "Author" },
  "agent.authorModel": { de: "GPT-4o", en: "GPT-4o" },
  "agent.authorRole": { de: "Erstellt Risk-Drafts", en: "Creates Risk Drafts" },
  "agent.authorDesc": { de: "Analysiert Quelldokumente, identifiziert Risiken, verlinkt Evidenz", en: "Analyzes source documents, identifies risks, links evidence" },
  "agent.critic": { de: "Kritiker", en: "Critic" },
  "agent.criticModel": { de: "Claude", en: "Claude" },
  "agent.criticRole": { de: "Prüft kritisch", en: "Reviews critically" },
  "agent.criticDesc": { de: "Verifiziert Claims, findet Lücken, hinterfragt Bewertungen", en: "Verifies claims, finds gaps, questions assessments" },
  "agent.resolver": { de: "Vermittler", en: "Resolver" },
  "agent.resolverModel": { de: "GPT-4o", en: "GPT-4o" },
  "agent.resolverRole": { de: "Mediiert & überarbeitet", en: "Mediates & revises" },
  "agent.resolverDesc": { de: "Bewertet Kritik, implementiert Änderungen oder eskaliert", en: "Evaluates criticism, implements changes or escalates" },
  "agent.conversation": { de: "Agent-Konversation", en: "Agent Conversation" },
  "agent.iterations": { de: "Iteration(en)", en: "Iteration(s)" },
  "agent.tokens": { de: "Tokens", en: "tokens" },
  "agent.criticFindings": { de: "Critic Findings", en: "Critic Findings" },
  "agent.recommendation": { de: "Empfehlung", en: "Recommendation" },
  "agent.generatedItems": { de: "Generierte Risk Items", en: "Generated Risk Items" },
  "agent.confidence": { de: "Konfidenz", en: "confidence" },
  "agent.verifiedClaims": { de: "Verifizierte Claims", en: "Verified Claims" },
  "agent.identifiedGaps": { de: "Identifizierte Gaps", en: "Identified Gaps" },
  "agent.legacyMock": { de: "Legacy: Mock AI Delta (Demo)", en: "Legacy: Mock AI Delta (Demo)" },
  "agent.legacyNote": { de: "Fallback zu Demo-Daten ohne echte KI-Analyse. Nutze den Multi-Agent-Button oben für echte GPT-4o + Claude Analyse.", en: "Fallback to demo data without real AI analysis. Use the Multi-Agent button above for real GPT-4o + Claude analysis." },
  "agent.runMockDelta": { de: "Mock Delta ausführen", en: "Run Mock Delta" },

  // Risk Items
  "risk.title": { de: "Risiko-Items", en: "Risk Items" },
  "risk.riskItems": { de: "Risk Items", en: "Risk Items" },
  "risk.findings": { de: "Findings", en: "Findings" },
  "risk.gapsIdentified": { de: "Gaps identifiziert", en: "Gaps identified" },
  "risk.escalated": { de: "Eskaliert", en: "Escalated" },
  "risk.rpn": { de: "RPN", en: "RPN" },

  // Gaps
  "gaps.title": { de: "Identifizierte Lücken", en: "Identified Gaps" },
  "gaps.id": { de: "ID", en: "ID" },
  "gaps.priority": { de: "Priorität", en: "Priority" },
  "gaps.category": { de: "Kategorie", en: "Category" },
  "gaps.description": { de: "Beschreibung", en: "Description" },
  "gaps.identifiedBy": { de: "Identifiziert von", en: "Identified by" },

  // Documents
  "docs.title": { de: "Quelldokumente", en: "Source documents" },
  "docs.type": { de: "Dokumenttyp", en: "Document type" },
  "docs.file": { de: "Datei", en: "File" },
  "docs.format": { de: "Unterstütztes Format", en: "Supported format" },
  "docs.excerpt": { de: "Inhaltsauszug", en: "Content excerpt" },
  "docs.placeholder": { de: "TODO Platzhalter: PDF, DOCX, XLSX, OCR, SharePoint/Teams, Veeva, TrackWise, Documentum Ingestion.", en: "TODO placeholders: PDF, DOCX, XLSX, OCR, SharePoint/Teams, Veeva, TrackWise, Documentum ingestion." },

  // Review Packages
  "review.packages": { de: "Review-Pakete", en: "Review Packages" },
  "review.riskBasedQueue": { de: "Risikobasierte Review-Warteschlange", en: "Risk-Based Review Queue" },
  "review.generatePackages": { de: "Pakete generieren", en: "Generate Packages" },
  "review.runAllChecks": { de: "Alle Prüfungen ausführen", en: "Run All Checks" },
  "review.generateExport": { de: "Export generieren", en: "Generate Export" },
  "review.downloadJson": { de: "JSON herunterladen", en: "Download JSON" },

  // Notice
  "notice.draft": { de: "DRAFT Sicherheitshinweis:", en: "DRAFT safety notice:" },
  "notice.text": { de: "Alle KI-generierten Inhalte sind als ENTWURF gekennzeichnet. Die App bereitet prüfbare Arbeitspakete vor; sie ersetzt keine qualifizierte menschliche Risikobewertung, QA-Verantwortung oder regulatorische Entscheidungen.", en: "All AI-generated content is labeled DRAFT. The app prepares reviewable work products; it does not replace qualified human risk assessment, QA responsibility, or regulatory decisions." },

  // Actions
  "action.save": { de: "Speichern", en: "Save" },
  "action.cancel": { de: "Abbrechen", en: "Cancel" },
  "action.delete": { de: "Löschen", en: "Delete" },
  "action.edit": { de: "Bearbeiten", en: "Edit" },
  "action.view": { de: "Ansehen", en: "View" },
  "action.download": { de: "Herunterladen", en: "Download" },
  "action.upload": { de: "Hochladen", en: "Upload" },
  "action.refresh": { de: "Aktualisieren", en: "Refresh" },
  "action.run": { de: "Ausführen", en: "Run" },
  "action.generate": { de: "Generieren", en: "Generate" },

  // Status
  "status.loading": { de: "Wird geladen...", en: "Loading..." },
  "status.error": { de: "Fehler aufgetreten", en: "Error occurred" },
  "status.success": { de: "Erfolgreich", en: "Success" },
  "status.idle": { de: "Bereit", en: "Ready" },
  "status.running": { de: "Läuft", en: "Running" },
  "status.completed": { de: "Abgeschlossen", en: "Completed" },
  "status.done": { de: "Fertig", en: "Done" },

  // Theme
  "theme.light": { de: "Hell", en: "Light" },
  "theme.dark": { de: "Dunkel", en: "Dark" },
  "theme.system": { de: "System", en: "System" },

  // Table Headers
  "table.artifact": { de: "Artefakt", en: "Artifact" },
  "table.status": { de: "Status", en: "Status" },
  "table.purpose": { de: "Zweck", en: "Purpose" },

  // Misc
  "misc.noData": { de: "Keine Daten verfügbar", en: "No data available" },
  "misc.showMore": { de: "Mehr anzeigen", en: "Show more" },
  "misc.showLess": { de: "Weniger anzeigen", en: "Show less" },
  "misc.of": { de: "von", en: "of" },
  "misc.all": { de: "Alle", en: "All" },
  "misc.filter": { de: "Filter", en: "Filter" },
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
