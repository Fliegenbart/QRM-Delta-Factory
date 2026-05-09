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
  "dashboard.triggerText": { de: "Change Control für geänderte automatisierte visuelle Inspektions-Ablehnungsschwelle.", en: "Change control for modified automated visual inspection rejection threshold." },
  "dashboard.mainConcern": { de: "Hauptbedenken", en: "Main concern" },
  "dashboard.mainConcernText": { de: "Evidenzpaket deckt alte Schwelle ab; Wirksamkeitsnachweis für neue Schwelle fehlt.", en: "Evidence package covers old threshold; new-threshold effectiveness evidence is missing." },
  "dashboard.routing": { de: "Routing", en: "Routing" },
  "dashboard.routingText": { de: "Level 3 Items gehen zuerst zum SME-Review, dann erst nach Pflichtfeld- und Gate-Prüfung zum QA-Workflow.", en: "Level 3 items go to SME review first, then QA workflow only after required fields and gates pass." },

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

  // Document Upload
  "upload.title": { de: "Dokumente für Analyse", en: "Documents for Analysis" },

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
  "review.generatedPackages": { de: "Generierte Pakete", en: "Generated packages" },
  "review.readyForReview": { de: "Bereit für Review", en: "Ready for review" },
  "review.inputIncomplete": { de: "Eingabe unvollständig", en: "Input incomplete" },
  "review.total": { de: "Gesamt", en: "Total" },
  "review.ready": { de: "Bereit", en: "Ready" },
  "review.incomplete": { de: "Unvollständig", en: "Incomplete" },
  "review.pass": { de: "Bestanden", en: "Pass" },
  "review.partial": { de: "Teilweise", en: "Partial" },
  "review.fail": { de: "Fehlgeschlagen", en: "Fail" },
  "review.reduction": { de: "Reduktion", en: "Reduction" },
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

  // Validation Pack
  "validation.title": { de: "Validierungspaket", en: "Validation Pack" },
  "validation.description": { de: "GMP-konformes Validierungspaket für regulatorische Einreichung.", en: "GMP-compliant validation package for regulatory submission." },

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
  "riskLib.title": { de: "Genehmigte Risikobibliothek", en: "Approved risk library" },
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
  "premium.reviewPackages": { de: "Review-Pakete", en: "Review packages" },
  "premium.headline": { de: "Qualitätsrisiko, auf Evidenz reduziert.", en: "Quality risk, reduced to evidence." },
  "premium.subline": { de: "Vollständige Entwurfs-Risikopakete für die AVI-Schwellenänderung. Unvollständige Eingaben werden vor der Plausibilitätsprüfung blockiert.", en: "Complete draft risk packages for the AVI threshold change. Incomplete inputs are blocked before plausibility review." },
  "premium.generatePackages": { de: "Review-Pakete generieren", en: "Generate Review Packages" },
  "premium.runAllChecks": { de: "Alle Prüfungen ausführen", en: "Run all ready checks" },
  "premium.draftNote": { de: "ENTWURF • quellenverknüpft • menschlich kontrolliert", en: "DRAFT • source-linked • human controlled" },
  "premium.architecture": { de: "Architektur", en: "Architecture" },
  "premium.architectureText": { de: "Dokumente, Auslöser, FMEA-Baseline, Ausschnitte, Bibliothek und Bewertungsmodell werden zuerst zusammengestellt.", en: "Documents, trigger, FMEA baseline, snippets, library, and scoring model are assembled first." },
  "premium.completenessGate": { de: "Vollständigkeitsgate", en: "Completeness gate" },
  "premium.completenessText": { de: "Fehlende technische Eingaben gehen zurück an Author/Ops. Der Critic wird nicht bei unvollständigen Paketen aufgerufen.", en: "Missing technical input goes back to Author/Ops. The Critic is not called on partial packages." },
  "premium.demoScenario": { de: "Demo-Szenario", en: "Demo scenario" },
  "premium.demoText": { de: "CC-2026-014, nur Validierung alter Schwelle, fehlender Schulungsnachweis, fehlendes Validierungsaddendum.", en: "CC-2026-014, old-threshold validation only, missing training record, missing validation addendum." },
  "premium.sterileNote": { de: "Sterile Injektion • AVI-Schwellen-Review", en: "Sterile injectable • AVI threshold review" },

  // Executive Risk Summary
  "executive.reviewSummary": { de: "Review-Zusammenfassung", en: "Review summary" },
  "executive.total": { de: "Gesamt", en: "Total" },
  "executive.ready": { de: "Bereit", en: "Ready" },
  "executive.incomplete": { de: "Unvollständig", en: "Incomplete" },
  "executive.pass": { de: "Bestanden", en: "Pass" },
  "executive.partial": { de: "Teilweise", en: "Partial" },
  "executive.fail": { de: "Fehlgeschlagen", en: "Fail" },
  "executive.reduction": { de: "Reduktion", en: "Reduction" },
  "executive.manualBaseline": { de: "Geschätzter manueller Basisaufwand", en: "Estimated manual baseline" },
  "executive.manualBaselineDesc": { de: "Klassische Dokumentensuche und breite manuelle Risikobewertungsschätzung.", en: "Classic document search and broad manual risk review estimate." },
  "executive.assistedReview": { de: "Geschätzte unterstützte Prüfung", en: "Estimated assisted review" },
  "executive.assistedReviewDesc": { de: "Nur indikative MVP-Schätzung. Dies ist keine regulatorische oder Einreichungsaussage.", en: "Indicative MVP estimate only. It is not a regulatory or submission claim." },

  // Evidence Confidence Panel
  "evidence.confidence": { de: "Evidenz-Konfidenz", en: "Evidence confidence" },
  "evidence.confidenceDesc": { de: "Signale für die Review-Planung, keine Genehmigung.", en: "Signals for review planning, not approval." },
  "evidence.sourceCoverage": { de: "Quellenabdeckung", en: "Source coverage" },
  "evidence.plausibilityChecked": { de: "Plausibilität geprüft", en: "Plausibility checked" },
  "evidence.evidenceLinked": { de: "Evidenz verknüpft", en: "Evidence linked" },
  "evidence.openGapsVisible": { de: "Offene Lücken sichtbar", en: "Open gaps visible" },
  "evidence.evidenceLinks": { de: "Evidenzverknüpfungen", en: "Evidence links" },
  "evidence.gapsInputs": { de: "Lücken / Eingaben", en: "Gaps / inputs" },

  // Progress Wizard
  "wizard.generate": { de: "Generieren", en: "Generate" },
  "wizard.generateDesc": { de: "Review-Pakete erstellen", en: "Build review packages" },
  "wizard.plausibility": { de: "Plausibilität", en: "Plausibility" },
  "wizard.plausibilityDesc": { de: "KI-Prüfungen ausführen", en: "Run AI checks" },
  "wizard.smeReview": { de: "SME-Review", en: "SME Review" },
  "wizard.smeDesc": { de: "Technische Prüfung", en: "Technical review" },
  "wizard.qaApproval": { de: "QA-Freigabe", en: "QA Approval" },
  "wizard.qaDesc": { de: "Qualitätsfreigabe", en: "Quality sign-off" },
  "wizard.export": { de: "Export", en: "Export" },
  "wizard.exportDesc": { de: "Paket liefern", en: "Deliver package" },
  "wizard.navigation": { de: "Review-Fortschritt", en: "Review progress" },
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
