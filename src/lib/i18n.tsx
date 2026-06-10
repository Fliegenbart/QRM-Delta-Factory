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
  "nav.category.workspace": { de: "Arbeiten", en: "Work" },
  "nav.category.riskAnalysis": { de: "Analyse vorbereiten", en: "Prepare Analysis" },
  "nav.category.reviewQA": { de: "Prüfung steuern", en: "Steer Review" },
  "nav.category.evidenceGaps": { de: "Quellen & Lücken", en: "Sources & Gaps" },
  "nav.category.output": { de: "Lieferpakete", en: "Deliverables" },
  "nav.category.admin": { de: "Setup", en: "Setup" },
  "nav.category.howItWorks": { de: "Funktionsweise", en: "How it works" },

  // Navigation Items
  "nav.dashboard": { de: "Start", en: "Start" },
  "nav.caseWorkspace": { de: "Prüffälle", en: "Review cases" },
  "nav.aiArchitecture": { de: "Wie die Prüfmappe entsteht", en: "How the review pack is built" },
  "nav.backendReview": { de: "Prüffälle", en: "Review cases" },
  "nav.projects": { de: "Projekte", en: "Projects" },
  "nav.documents": { de: "Dokumente", en: "Documents" },
  "nav.sourceSnippets": { de: "Quellausschnitte", en: "Source Snippets" },
  "nav.riskLibrary": { de: "Regelwerk", en: "Rule set" },
  "nav.ringversuch": { de: "Ringversuch", en: "Proficiency test" },
  "nav.triggerInput": { de: "Change/CAPA Eingabe", en: "Change/CAPA Input" },
  "nav.deltaAnalysis": { de: "Delta-Prozess", en: "Delta Process" },
  "nav.qrmMatrix": { de: "QRM-Matrix", en: "QRM Matrix" },
  "nav.reviewPackages": { de: "Prüfmappen", en: "Review Packages" },
  "nav.plausibilityChecks": { de: "Plausibilitätscheck", en: "Plausibility Check" },
  "nav.redTeamFindings": { de: "Blind-Spot-Prüfung", en: "Blind-Spot Review" },
  "nav.reviewQueue": { de: "Review-Prioritäten", en: "Review Priorities" },
  "nav.approvals": { de: "QA-Entscheidungen", en: "QA Decisions" },
  "nav.evidenceMap": { de: "Quellenkarte", en: "Evidence Map" },
  "nav.gaps": { de: "Lücken", en: "Gaps" },
  "nav.exportPackage": { de: "Prüfmappe exportieren", en: "Review Pack Export" },
  "nav.validationPack": { de: "Validierungsunterlagen", en: "Validation Documents" },
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
  "brand.tagline": { de: "Unterlagen rein. Prüfmappe raus. QA entscheidet.", en: "Documents in. Review pack out. QA decides." },

  // Dashboard
  "dashboard.openHighGaps": { de: "High/Critical offen", en: "High/Critical open" },
  "dashboard.level3Review": { de: "Vollreview", en: "Full review" },
  "dashboard.aiDraftItems": { de: "Draft Items", en: "Draft items" },
  "dashboard.sourceSnippets": { de: "Quellen", en: "Sources" },
  "dashboard.riskBasedQueue": { de: "Nächste Prüfung", en: "Next review" },
  "dashboard.openQueue": { de: "Queue öffnen", en: "Open queue" },
  "dashboard.deltaSummary": { de: "Der Nutzen", en: "The point" },
  "dashboard.trigger": { de: "Auslöser", en: "Trigger" },
  "dashboard.triggerText": { de: "Change Control für geänderte automatisierte visuelle Inspektions-Ablehnungsschwelle.", en: "Change control for modified automated visual inspection rejection threshold." },
  "dashboard.mainConcern": { de: "Top-Lücke", en: "Top gap" },
  "dashboard.mainConcernText": { de: "Validierung deckt die alte Schwelle ab. Die neue Schwelle braucht Evidenz.", en: "Validation covers the old threshold. The new threshold needs evidence." },
  "dashboard.routing": { de: "Nächster Schritt", en: "Next step" },
  "dashboard.routingText": { de: "Unvollständiges zurück an Author/Ops. Relevantes zu SME/QA.", en: "Incomplete input goes to Author/Ops. Relevant risk goes to SME/QA." },

  // Document Upload
  "upload.title": { de: "Dokumente für Analyse", en: "Documents for Analysis" },

  // Risk Items
  "risk.title": { de: "Risiko-Items", en: "Risk Items" },
  "risk.riskItems": { de: "Risk Items", en: "Risk Items" },
  "risk.findings": { de: "Prüfpunkte", en: "Findings" },
  "risk.gapsIdentified": { de: "Lücken gefunden", en: "Gaps identified" },
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
  "review.packages": { de: "Prüfmappen", en: "Review Packages" },
  "review.riskBasedQueue": { de: "Prüfung nach Dringlichkeit", en: "Risk-Based Review Queue" },
  "review.generatedPackages": { de: "Erstellte Prüfmappen", en: "Generated packages" },
  "review.readyForReview": { de: "Bereit für Quellencheck", en: "Ready for source check" },
  "review.inputIncomplete": { de: "Zurück an Author/Ops", en: "Back to Author/Ops" },
  "review.total": { de: "Gesamt", en: "Total" },
  "review.ready": { de: "Bereit", en: "Ready" },
  "review.incomplete": { de: "Unvollständig", en: "Incomplete" },
  "review.pass": { de: "Bestanden", en: "Pass" },
  "review.partial": { de: "Teilweise", en: "Partial" },
  "review.fail": { de: "Fehlgeschlagen", en: "Fail" },
  "review.reduction": { de: "Reduktion", en: "Reduction" },
  "review.generatePackages": { de: "Prüfmappen erstellen", en: "Build Review Packages" },
  "review.runAllChecks": { de: "Plausibilität prüfen", en: "Run Plausibility Checks" },
  "review.generateExport": { de: "Prüfmappe als Entwurf erzeugen", en: "Generate Draft Review Pack" },
  "review.downloadJson": { de: "JSON herunterladen", en: "Download JSON" },

  // Notice
  "notice.draft": { de: "DRAFT", en: "DRAFT" },
  "notice.text": { de: "KI bereitet vor. QA entscheidet.", en: "AI prepares. QA decides." },

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

  // Validation Pack
  "validation.title": { de: "Validierungspaket", en: "Validation Pack" },
  "validation.description": { de: "Entwurfsunterlagen für eine spätere Validierungsplanung im Kundensystem.", en: "Draft documents for later validation planning in the customer's quality system." },

  // Projects
  "projects.title": { de: "Projekte", en: "Projects" },
  "projects.createProject": { de: "QRM-Projekt erstellen", en: "Create QRM project" },
  "projects.createDraft": { de: "Entwurfsprojekt erstellen", en: "Create draft project" },
  "projects.selectProject": { de: "Projekt auswählen", en: "Select a project" },

  // Snippets
  "snippets.title": { de: "Quellausschnitte mit Hashes", en: "Source snippets with hashes" },
  "snippets.snippet": { de: "Ausschnitt", en: "Snippet" },
  "snippets.document": { de: "Dokument", en: "Document" },
  "snippets.section": { de: "Abschnitt", en: "Section" },
  "snippets.lineRef": { de: "Zeilen-/Seitenreferenz", en: "Line/page placeholder" },
  "snippets.hash": { de: "Hash", en: "Hash" },

  // Risk Library
  "riskLib.title": { de: "Genehmigtes Regelwerk", en: "Approved rule set" },
  "riskLib.libraryId": { de: "Bibliotheks-ID", en: "Library ID" },
  "riskLib.gmpArea": { de: "GMP-Bereich", en: "GMP area" },
  "riskLib.processStep": { de: "Prozessschritt", en: "Process step" },
  "riskLib.failureMode": { de: "Fehlermodus / Gefährdung", en: "Failure mode / hazard" },
  "riskLib.status": { de: "Status", en: "Status" },
  "riskLib.version": { de: "Version", en: "Version" },
  "riskLib.sme": { de: "SME", en: "SME" },
  "riskLib.note": { de: "Nicht genehmigte Bibliothekseinträge können nicht als genehmigte Basis verwendet werden. Wenn keine Übereinstimmung existiert, wird das Risiko als NEU_ODER_UNGEPRÜFT markiert und zum SME-Review weitergeleitet.", en: "Unapproved library items cannot be used as an approved basis. If no match exists, the risk is marked NEW_OR_UNVERIFIED and routed to SME review." },

  // Trigger Section
  "trigger.title": { de: "Change/Abweichung/CAPA/Finding Eingabe", en: "Change/deviation/CAPA/finding input" },
  "trigger.changeControl": { de: "Change Control", en: "Change control" },
  "trigger.changeText": { de: "Geänderte AVI-Ablehnungsschwelle zur Reduzierung falscher Ablehnungen bei Beibehaltung der Erkennungsfähigkeit.", en: "Modified AVI rejection threshold to reduce false rejects while maintaining detection capability." },
  "trigger.deviation": { de: "Abweichung", en: "Deviation" },
  "trigger.deviationText": { de: "Formulierung der Chargenprotokoll-Abstimmung für AVI-Ablehnungszahlen ist unklar.", en: "Batch record reconciliation wording for AVI reject counts is unclear." },
  "trigger.capa": { de: "CAPA", en: "CAPA" },
  "trigger.capaText": { de: "Synthetische Nachverfolgung für Schwellenevidenz, Schulungsabschluss und Abstimmungsklarstellung.", en: "Synthetic follow-up for threshold evidence, training completion, and reconciliation clarification." },
  "trigger.auditFinding": { de: "Audit-Finding", en: "Audit finding" },
  "trigger.auditText": { de: "Prüfung, ob der Audit-Trail-Umfang explizit die Schwellenkonfiguration abdeckt.", en: "Review whether audit trail scope explicitly covers threshold configuration." },

  // Run Button
  "runButton.processing": { de: "Verarbeitung...", en: "Processing..." },
  "runButton.complete": { de: "Abgeschlossen", en: "Complete" },

  // Documents Section (additional keys for DocumentsSection component)
  "docs.sourceDocuments": { de: "Quelldokumente", en: "Source documents" },
  "docs.documentType": { de: "Dokumenttyp", en: "Document type" },
  "docs.fileName": { de: "Datei", en: "File" },
  "docs.supportedFormat": { de: "Unterstütztes Format", en: "Supported format" },
  "docs.contentExcerpt": { de: "Inhaltsauszug", en: "Content excerpt" },
  "docs.todoPlaceholder": { de: "TODO Platzhalter: PDF, DOCX, XLSX, OCR, SharePoint/Teams, Veeva, TrackWise, Documentum Anbindung.", en: "TODO placeholders: PDF, DOCX, XLSX, OCR, SharePoint/Teams, Veeva, TrackWise, Documentum ingestion." },

  // Premium Review Hero
  "premium.reviewPackages": { de: "Prüfmappen", en: "Review packages" },
  "premium.headline": { de: "Unterlagen rein. Prüfmappe raus.", en: "Change control in. Review pack out." },
  "premium.subline": { de: "Das System findet relevante Deltas, zeigt Quellen und blockiert unvollständige Pakete.", en: "The system finds relevant deltas, shows sources, and blocks incomplete packages." },
  "premium.generatePackages": { de: "Prüfmappen erstellen", en: "Build review packages" },
  "premium.runAllChecks": { de: "Plausibilität prüfen", en: "Run plausibility checks" },
  "premium.draftNote": { de: "Draft. Quellen sichtbar. Mensch entscheidet.", en: "Draft. Sources visible. Human decides." },
  "premium.architecture": { de: "Quellen", en: "Sources" },
  "premium.architectureText": { de: "Change Control, FMEA, SOP, Validierung.", en: "Change control, FMEA, SOP, validation." },
  "premium.completenessGate": { de: "Gate", en: "Gate" },
  "premium.completenessText": { de: "Fehlt Evidenz, stoppt der Check.", en: "Missing evidence stops the check." },
  "premium.sterileNote": { de: "Sterile Injektion • AVI-Schwellen-Review", en: "Sterile injectable • AVI threshold review" },

  // Executive Risk Summary
  "executive.reviewSummary": { de: "Review-Aufwand", en: "Review workload" },
  "executive.total": { de: "Gesamt", en: "Total" },
  "executive.ready": { de: "Bereit", en: "Ready" },
  "executive.incomplete": { de: "Unvollständig", en: "Incomplete" },
  "executive.pass": { de: "Bestanden", en: "Pass" },
  "executive.partial": { de: "Teilweise", en: "Partial" },
  "executive.fail": { de: "Fehlgeschlagen", en: "Fail" },
  "executive.reduction": { de: "Reduktion", en: "Reduction" },
  "executive.manualBaseline": { de: "Geschätzter manueller Basisaufwand", en: "Estimated manual baseline" },
  "executive.manualBaselineDesc": { de: "Klassische Suche und Vorstrukturierung.", en: "Classic search and pre-structuring." },
  "executive.assistedReview": { de: "Geschätzte unterstützte Prüfung", en: "Estimated assisted review" },
  "executive.assistedReviewDesc": { de: "Indikative Schätzung. Keine regulatorische Aussage.", en: "Indicative estimate. Not a regulatory statement." },

  // Evidence Confidence Panel
  "evidence.confidence": { de: "Wie belastbar sind die Quellen?", en: "How strong is the evidence?" },
  "evidence.confidenceDesc": { de: "Orientierung für die Review-Planung. Das ist keine Freigabe und kein regulatorisches Urteil.", en: "Guidance for review planning. This is not approval and not a regulatory judgement." },
  "evidence.sourceCoverage": { de: "Quellenabdeckung", en: "Source coverage" },
  "evidence.plausibilityChecked": { de: "Plausibilität geprüft", en: "Plausibility checked" },
  "evidence.evidenceLinked": { de: "Evidenz verknüpft", en: "Evidence linked" },
  "evidence.openGapsVisible": { de: "Offene Lücken sichtbar", en: "Open gaps visible" },
  "evidence.evidenceLinks": { de: "Evidenzverknüpfungen", en: "Evidence links" },
  "evidence.gapsInputs": { de: "Lücken / Eingaben", en: "Gaps / inputs" },

  // Progress Wizard
  "wizard.generate": { de: "Prüfmappen", en: "Packages" },
  "wizard.generateDesc": { de: "Prüfmappen erstellen", en: "Build review packages" },
  "wizard.plausibility": { de: "Quellencheck", en: "Source check" },
  "wizard.plausibilityDesc": { de: "Plausibilität prüfen", en: "Check plausibility" },
  "wizard.smeReview": { de: "Fachreview", en: "Expert review" },
  "wizard.smeDesc": { de: "SME-Fragen klären", en: "Resolve SME questions" },
  "wizard.qaApproval": { de: "QA-Entscheid", en: "QA decision" },
  "wizard.qaDesc": { de: "Menschlich dokumentieren", en: "Document human decision" },
  "wizard.export": { de: "Lieferpaket", en: "Deliverable" },
  "wizard.exportDesc": { de: "Prüfmappe als Entwurf exportieren", en: "Export draft review pack" },
  "wizard.navigation": { de: "Wo steht der Fall?", en: "Where does the case stand?" },
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
