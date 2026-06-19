export type ReviewDecisionValue =
  | "confirm"
  | "downgrade"
  | "reject_false_positive"
  | "severity_incorrect"
  | "evidence_incorrect"
  | "requirement_incorrect"
  | "missed_finding"
  | "request_more_information"
  | "escalate_to_qa";

export const supabasePublicEnvKeys = {
  url: "NEXT_PUBLIC_SUPABASE_URL",
  publishableKey: "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"
} as const;

export function hasSupabasePublicConfig(
  env: Record<string, string | undefined> = process.env
): boolean {
  return Boolean(
    env[supabasePublicEnvKeys.url] && env[supabasePublicEnvKeys.publishableKey]
  );
}

export const riskOrchestrationEntry = {
  legacyDeltaRoute: "/delta-analysis",
  reviewWorkbenchRoute: "/review-ui",
  replacesLegacyDeltaAnalysis: true,
  name: "QA-Prüfung vorbereiten",
  shortDescription:
    "Aus GMP-Unterlagen wird eine Prüfmappe mit Quellen, offenen Fragen und nächstem Schritt.",
  workflow: [
    "Unterlagen hochladen",
    "Aussagen und Anforderungen prüfen",
    "Nachweise abgleichen",
    "Prüfmappe öffnen",
    "Menschliche Entscheidung dokumentieren"
  ]
} as const;

export const productHomeCopy = {
  title: "Unterlagen hochladen. Prüfmappe zurückbekommen.",
  subtitle:
    "Change, CAPA oder Abweichung rein — das Tool zeigt Prüfpunkte, Quellen, fehlende Nachweise und den nächsten QA-Schritt. Die Originaldateien bleiben die Quelle.",
  primaryAction: "Prüffall vorbereiten",
  workflow: [
    "Unterlagen hochladen",
    "Prüfpunkte und Quellen sehen",
    "Lücken klären",
    "Entscheidung dokumentieren"
  ],
  dossierPreview: [
    { label: "Der Fall", value: "worum es geht (Abweichung, CAPA, Change)" },
    { label: "Der Befund", value: "was auffällt, mit Quelle belegt" },
    { label: "Die Lücke", value: "welcher Nachweis fehlt" },
    { label: "Ihre Entscheidung", value: "bestätigen, nachfordern oder eskalieren" }
  ],
  exampleTitle: "Drei Beispiele: So sieht eine fertige Prüfmappe aus.",
  exampleDescription:
    "Der Fall, die Quellen, die Lücken — und der nächste Entscheidungsschritt. Klicken Sie sich durch, bevor Sie eigene Unterlagen hochladen."
} as const;

export type DemoReviewCase = {
  id: string;
  severity: "critical" | "major" | "minor" | "ready";
  severityLabel: string;
  area: string;
  title: string;
  noteLabel: string;
  criticNote: string;
  ageLabel: string;
  sources: string;
  regulation: string;
  primaryAction: "open" | "approve";
  href: string;
  summary: string;
  whyItMatters: string;
  nextStep: string;
  findings: string[];
  evidence: string[];
  missingEvidence: string[];
  openQuestions: string[];
  decisionActions: string[];
};

export const demoReviewCases: DemoReviewCase[] = [
  {
    id: "DEV-2025-014",
    severity: "critical",
    severityLabel: "Kritisch",
    area: "Aseptische Abfüllung",
    title: "Abweichung im Klima-Monitoring, Bezug zum Sterilfilter unklar",
    noteLabel: "Prüfhinweis",
    criticNote:
      "Für die Aussage, der HEPA-Vorlauf sei entkoppelt, fehlt eine Quelle. Annex 1 §8.123 ist zitiert, aber das Zitat passt nicht zur Textstelle auf Seite 14.",
    ageLabel: "vor 12 min",
    sources: "3 Quellen · 1 fehlt",
    regulation: "ICH Q9 §5.3.2",
    primaryAction: "open",
    href: "/review-ui/demo/dev-2025-014",
    summary:
      "Die Abweichung kann kritisch sein, weil ein Klima-Signal und die Sterilfilter-Bewertung noch nicht sauber zusammengeführt sind.",
    whyItMatters:
      "Warum dieser Fall wichtig ist: Eine unklare Quelle kann dazu führen, dass ein Sterilitätsrisiko zu früh als abgedeckt gilt.",
    nextStep: "Passt die zitierte Stelle wirklich zur Aussage über den HEPA-Vorlauf?",
    findings: [
      "HEPA-Vorlauf wird als entkoppelt beschrieben, die zitierte Textstelle belegt das aber nicht klar.",
      "Klima-Monitoring und Sterilfilter-Bewertung sind fachlich verbunden, aber noch nicht sauber abgegrenzt.",
      "Der Fall braucht eine menschliche QA-Entscheidung, bevor er geschlossen werden kann."
    ],
    evidence: [
      "Abweichungsbericht mit Klima-Monitoring-Verlauf",
      "Annex-1-Referenz zur Sterilfilter-Bewertung",
      "Chargenbezug und Reinraum-Bereich"
    ],
    missingEvidence: [
      "Nachweis, dass Klima-Signal und HEPA-Vorlauf fachlich getrennt bewertet wurden.",
      "Passende Textstelle zur Aussage über den HEPA-Vorlauf.",
      "SME-Einschätzung, ob das Gap freigaberelevant ist."
    ],
    openQuestions: [
      "Ist die zitierte Textstelle fachlich passend?",
      "Fehlt ein Nachweis zur Trennung von Klima- und Sterilfilter-Risiko?",
      "Muss QA sofort entscheiden oder zuerst SME nachfordern?"
    ],
    decisionActions: [
      "Bestätigen",
      "Weitere Unterlagen anfordern",
      "An QA eskalieren"
    ]
  },
  {
    id: "CAPA-2025-082",
    severity: "major",
    severityLabel: "Hoch",
    area: "Reinigung",
    title: "Wirksamkeitsprüfung Reinigungsmittel nach 30 Tagen offen",
    noteLabel: "Prüfhinweis",
    criticNote:
      "Die Maßnahmen sind dokumentiert, die Wirksamkeit aber noch nicht bewertet. Zu entscheiden: blockierendes Gap für die Freigabe oder nicht?",
    ageLabel: "vor 1 Std.",
    sources: "5 Quellen · vollständig",
    regulation: "SOP-CLN-04 §4.2",
    primaryAction: "open",
    href: "/review-ui/demo/capa-2025-082",
    summary:
      "Die CAPA ist formal angelegt, aber der wichtigste Wirksamkeitsnachweis ist noch offen.",
    whyItMatters:
      "Warum dieser Fall wichtig ist: Ohne Wirksamkeitsbewertung bleibt unklar, ob die Korrekturmaßnahme wirklich abgeschlossen ist.",
    nextStep: "Reicht der Maßnahmenstand, oder muss die Wirksamkeit vor Freigabe belegt sein?",
    findings: [
      "Maßnahmen sind dokumentiert, die Wirksamkeit ist aber noch nicht bewertet.",
      "Die Frist von 30 Tagen ist im Prüfkontext sichtbar und muss bewertet werden.",
      "Der Fall kann ohne klare Wirksamkeitsbewertung nicht sauber freigegeben werden."
    ],
    evidence: [
      "CAPA-Aktionsliste",
      "Reinigungsprotokoll Charge R-1183",
      "SOP-CLN-04 §4.2"
    ],
    missingEvidence: [
      "Nachweis der Wirksamkeitsprüfung nach 30 Tagen.",
      "Begründung, falls die Freigabe vor Abschluss der Bewertung möglich sein soll.",
      "Fachliche Bestätigung durch SME oder QA."
    ],
    openQuestions: [
      "Ist die 30-Tage-Frist verbindlich oder nur geplant?",
      "Gibt es einen dokumentierten Zwischenstatus?",
      "Wer muss die Wirksamkeit fachlich bestätigen?"
    ],
    decisionActions: [
      "Bestätigen",
      "Weitere Unterlagen anfordern",
      "An QA eskalieren"
    ]
  },
  {
    id: "CC-2025-211",
    severity: "ready",
    severityLabel: "Bereit für QA",
    area: "QC-Labor",
    title: "Methodenänderung Gradient-Profil, SME hat abgezeichnet",
    noteLabel: "Prüfhinweis",
    criticNote:
      "Quellen vollständig, Risiken belegt, keine Widersprüche. Die SME-Abzeichnung vom 18.05. wartet auf Freigabe.",
    ageLabel: "seit gestern",
    sources: "8 Quellen · vollständig",
    regulation: "ICH Q2 R2",
    primaryAction: "approve",
    href: "/review-ui/demo/cc-2025-211",
    summary:
      "Der Fall ist vorbereitet: Quellen, SME-Abzeichnung und Regelwerksbezug sind sichtbar.",
    whyItMatters:
      "Warum dieser Fall wichtig ist: Die Prüfmappe zeigt, dass die wichtigsten Nachweise sichtbar sind und QA zur Entscheidung übergehen kann.",
    nextStep: "Final prüfen und Entscheidung dokumentieren.",
    findings: [
      "SME-Abzeichnung ist vorhanden und datiert.",
      "Regelwerksbezug zur Methodenänderung ist sichtbar.",
      "Keine offenen Widersprüche in den angezeigten Quellen."
    ],
    evidence: [
      "SME-Abzeichnung vom 18.05.",
      "Methodenänderung Gradient-Profil",
      "Validierungsbezug ICH Q2 R2"
    ],
    missingEvidence: [
      "Keine kritische Lücke in der Demo sichtbar.",
      "QA-Begründung muss vor Freigabe dokumentiert werden.",
      "Betroffene Chargen müssen final bestätigt bleiben."
    ],
    openQuestions: [
      "Ist die Begründung für QA ausreichend kurz dokumentiert?",
      "Sind alle betroffenen Chargen ausgeschlossen oder bewertet?",
      "Soll die Entscheidung als Freigabe oder als Rückfrage gespeichert werden?"
    ],
    decisionActions: [
      "Bestätigen",
      "Weitere Unterlagen anfordern",
      "An QA eskalieren"
    ]
  }
];

export function findDemoReviewCase(id: string): DemoReviewCase | undefined {
  return demoReviewCases.find((demoCase) => demoCase.href.endsWith(`/${id}`));
}

export function userFacingReviewLoadError(error: string): { title: string; message: string } {
  if (error.includes("QRM_BACKEND") || error.includes("Backend nicht verbunden")) {
    return {
      title: "Prüffälle gerade nicht verfügbar",
      message:
        "Echte Prüffälle brauchen eine Backend-Verbindung. Du kannst trotzdem einen neuen Prüffall auf der Startseite vorbereiten oder die Demo-Prüfmappe öffnen."
    };
  }

  return {
    title: "Fallliste konnte nicht geladen werden",
    message: error
  };
}

export const consultantReviewCopy = {
  productName: "Pharma QRM",
  workspaceTitle: "QA-Prüfung vorbereiten",
  workspaceDescription:
    "Unterlagen rein. Prüfmappe raus. Ein Mensch entscheidet.",
  nav: {
    cockpit: "Prüffälle",
    packages: "Prüffälle"
  },
  list: {
    title: "Prüffälle",
    empty:
      "Noch kein echter Prüffall vorhanden. Lade auf der Startseite Unterlagen hoch, dann erscheint hier der Fall.",
    loadErrorPrefix: "Fallliste konnte nicht geladen werden",
    columns: {
      package: "Prüffall",
      trigger: "Anlass",
      area: "Bereich",
      status: "Status",
      sources: "Unterlagen"
    },
    open: "Öffnen"
  },
  detail: {
    title: "Prüffall",
    openReviewPack: "Prüfmappe öffnen",
    sourcesTitle: "Hochgeladene Unterlagen",
    noSources: "Keine Unterlagen verknüpft.",
    loadErrorPrefix: "Prüffall konnte nicht geladen werden",
    labels: {
      packageId: "Interne Fall-ID",
      tenant: "Mandant",
      requirementSet: "Regelwerk-Version",
      uploadedBy: "Angelegt durch",
      documentType: "Anlass/Dokumenttyp",
      processArea: "Prozessbereich",
      uploaded: "Angelegt am",
      status: "Status"
    }
  },
  pack: {
    title: "Prüfmappe",
    humanReasons: "Prüfung notwendig",
    missingInformation: "Was noch fehlt",
    findingsTitle: "Prüfpunkte",
    emptyFindings: "Keine Prüfpunkte.",
    requirement: "Regelwerk",
    notLinked: "nicht verknüpft",
    openFinding: "Prüfpunkt ansehen",
    noEntries: "Keine Einträge.",
    loadError:
      "Prüfmappe nicht verfügbar. Lade zuerst Unterlagen hoch und starte die Prüfung."
  },
  finding: {
    backToPack: "Zurück zur Prüfmappe",
    title: "Prüfpunkt",
    notFound: "Prüfpunkt nicht gefunden.",
    humanReason: "Prüfung notwendig",
    evidenceTitle: "Nachweise",
    noEvidence: "Keine Nachweise verknüpft.",
    document: "Dokument",
    page: "Seite",
    chunk: "Textstelle",
    modelPositions: "Was die Prüfhelfer gemeldet haben",
    foundBy: "Hat ein Problem gesehen",
    contradictedBy: "Hat widersprochen",
    noIssueAgents: "Hat kein Problem gesehen",
    decisionForm: "Entscheidung",
    loadErrorPrefix: "Prüfpunkt konnte nicht geladen werden",
    labels: {
      findingId: "Prüfpunkt-ID",
      riskCategory: "Risikobereich",
      requirementReference: "Regelwerk-Referenz",
      verifierResult: "Evidenzprüfung"
    }
  },
  decision: {
    reviewerId: "Reviewer-ID",
    rationale: "Begründung",
    placeholder:
      "Kurz begründen. Nicht allein auf das Modell stützen.",
    rationaleRequired: "Bitte kurz begründen.",
    savedMessage: "Entscheidung gespeichert. Der Bearbeitungsstand wurde aktualisiert."
  }
} as const;

export const reviewDecisionRequiresHumanRationale = true;

const riskStatementLabels: Record<string, string> = {
  "Adversarial review found required evidence missing or not clearly present in the claim ledger.":
    "Erforderliche Nachweise fehlen oder sind in den Quellen nicht klar belegt."
};

export const aiArchitectureConcept = {
  title: "Der Weg eines Befunds — und sechs Stellen, an denen geprüft wird.",
  subtitle:
    "Hier sehen Sie genau, wie aus einem hochgeladenen Dokument ein belegter Befund wird. Jeder Schritt ist nachvollziehbar, jeder hat eine eingebaute Sicherung, und der letzte Schritt gehört immer einem Menschen.",
  flow: [
    {
      id: "source",
      title: "Aussagen herauslesen",
      description:
        "Das Dokument wird in einzelne, zitierfähige Aussagen zerlegt — jede mit Dokument, Seite, Textstelle und wörtlichem Zitat.",
      safeguard: "Sicherung: Keine Aussage ohne Quelle. Was sich nicht belegen lässt, geht nicht weiter."
    },
    {
      id: "scope-router",
      title: "Den Fall einordnen",
      description:
        "Dokumenttyp, Prozessbereich und fachliche Signale bestimmen, welche Regelpakete für diesen Fall überhaupt gelten.",
      safeguard: "Sicherung: Die Prüfer bekommen nur die Regeln, die zum Fall passen — kein Streuschuss."
    },
    {
      id: "reviewer-agents",
      title: "Fachlich prüfen",
      description:
        "Sieben unabhängige Prüfinstanzen gehen den Fall durch — Datenintegrität, Abweichung, CAPA, Chargenbezug, Validierung und Sterilität, regulatorische Konsistenz, Widersprüche.",
      safeguard:
        "Sicherung: Jede Instanz arbeitet mit den passenden Regeln und Quellen. Was eine übersieht, fällt einer anderen auf."
    },
    {
      id: "evidence-verifier",
      title: "Quellen abgleichen",
      description:
        "Jeder Befund wird gegen seinen Beleg geprüft: Stimmt das Zitat? Passt die Seite? Trägt die Textstelle die Aussage? Diese Prüfung macht fester Programmcode, keine KI — Zeichen für Zeichen.",
      safeguard: "Sicherung: Schwache oder fehlende Belege bleiben offen, statt durchzurutschen."
    },
    {
      id: "risk-fusion",
      title: "Risiken bündeln",
      description:
        "Eine Gegenprüfung fasst die Befunde zusammen — bewusst konservativ. Ein einmal gefundener Befund wird nie per Mehrheitsentscheid weggestimmt.",
      safeguard:
        "Sicherung: Hohe und kritische Risiken werden nie automatisch geschlossen. Fehlt ein nötiges Regelpaket, blockiert das System die Freigabe."
    },
    {
      id: "human-review",
      title: "Entscheidung dokumentieren",
      description: "QA oder SME prüft die offenen Punkte und dokumentiert die finale Entscheidung.",
      safeguard: "Sicherung: Die KI bereitet vor. Sie gibt nicht frei. Dieser Schritt ist nicht abschaltbar."
    }
  ],
  nonNegotiables: [
    "Die KI entscheidet nicht. Der letzte Schritt gehört QA oder SME.",
    "Keine Mehrheitsabstimmung.",
    "Jeder Prüfpunkt braucht Quelle oder klar benannte Nachweislücke.",
    "Jeder Lauf protokolliert Modell, Prüfauftrag und Regelpakete.",
    "Eigene SOPs lassen sich laden; die Prüfer ziehen daraus die passenden Regeln.",
    "Hohe und kritische Risiken werden nie automatisch geschlossen.",
    "Fehlt ein nötiges Regelpaket, blockiert das die Freigabe."
  ]
} as const;

export const caseWorkspaceStructure = {
  route: "/case-workspace",
  title: "Fallakte",
  description:
    "Ein Fall. Quellen, Prüfpunkte, Prüfung und Export.",
  primaryTabs: [
    {
      id: "overview",
      label: "Status",
      helper: "Was ist offen?"
    },
    {
      id: "sources",
      label: "Quellen",
      helper: "Worauf basiert es?"
    },
    {
      id: "risk-deltas",
      label: "Deltas",
      helper: "Was hat sich geändert?"
    },
    {
      id: "review-queue",
      label: "Review",
      helper: "Wer muss prüfen?"
    },
    {
      id: "export",
      label: "Export",
      helper: "Was wird geliefert?"
    }
  ],
  hiddenTechnicalPages: [
    "source-snippets",
    "qrm-matrix",
    "plausibility-checks",
    "red-team-findings",
    "evidence-map",
    "gaps",
    "approvals",
    "export-package"
  ]
} as const;

export type DocumentSet = {
  document_set_id: string;
  tenant_id: string;
  requirement_set_id: string;
  upload_timestamp: string;
  document_ids: string[];
  declared_document_type: string;
  declared_process_area: string;
  uploaded_by: string;
  status: string;
};

export type Requirement = {
  requirement_id: string;
  source_type: string;
  source_name: string;
  source_version: string;
  section: string;
  requirement_text: string;
  applies_to_document_types: string[];
  applies_to_process_areas: string[];
  criticality: string;
  required_evidence: string[];
  auto_close_allowed: boolean;
  effective_from: string;
  effective_to?: string | null;
};

export type RequirementSet = {
  requirement_set_id: string;
  tenant_id: string;
  name: string;
  version: string;
  imported_at: string;
  imported_by: string;
  active: boolean;
  requirements: Requirement[];
};

export type RequirementLibraryOverview = {
  configuredRequirementSetId: string;
  requirementSet: RequirementSet;
  activeRequirements: Requirement[];
};

export type HumanFeedbackRecord = {
  feedback_id: string;
  review_id: string;
  document_set_id: string;
  finding_id: string;
  tenant_id: string;
  document_type: string;
  process_area: string;
  agent_role: string;
  model_provider: string;
  model_name: string;
  model_version: string;
  prompt_version: string;
  requirement_references: string[];
  risk_category: string;
  original_severity: string;
  original_evidence_support: string;
  verifier_evidence_support?: string | null;
  human_decision: ReviewDecisionValue;
  feedback_outcome: string;
  reviewer_id: string;
  rationale: string;
  created_at: string;
  high_critical_recall_guard: boolean;
};

export type HumanFeedbackModelCard = {
  model_provider: string;
  model_name: string;
  model_version: string;
  prompt_version: string;
  agent_role: string;
  total_human_decisions: number;
  confirmed_count: number;
  downgrade_count: number;
  false_positive_count: number;
  severity_issue_count?: number;
  evidence_issue_count?: number;
  requirement_issue_count?: number;
  missed_finding_count?: number;
  more_information_count: number;
  escalation_count: number;
  confirmation_rate: number;
  downgrade_rate: number;
  false_positive_rate: number;
};

export type HumanFeedbackRegistryReport = {
  generated_at: string;
  total_feedback_records: number;
  model_card_count: number;
  records: HumanFeedbackRecord[];
  model_cards: HumanFeedbackModelCard[];
  limitations: string[];
};

export type CalibrationExampleStatus = "raw_feedback" | "approved_gold" | "active";

export type CalibrationExample = {
  calibration_example_id: string;
  source_review_id: string;
  source_feedback_id: string;
  document_set_id: string;
  finding_id: string;
  tenant_id: string;
  document_type: string;
  process_area: string;
  agent_role: string;
  model_provider: string;
  model_name: string;
  model_version: string;
  prompt_version: string;
  requirement_references: string[];
  risk_category: string;
  original_severity: string;
  human_decision: ReviewDecisionValue;
  feedback_outcome: string;
  reviewer_id: string;
  reviewer_rationale: string;
  risk_statement: string;
  evidence_quotes: string[];
  high_critical_recall_guard: boolean;
  status: CalibrationExampleStatus;
  created_at: string;
  approved_by?: string | null;
  approved_at?: string | null;
  activated_by?: string | null;
  activated_at?: string | null;
  regression_gate_report_id?: string | null;
};

export type ReviewCalibrationReport = {
  generated_at: string;
  total_examples: number;
  raw_feedback_count: number;
  approved_gold_count: number;
  active_count: number;
  examples: CalibrationExample[];
  limitations: string[];
};

export type CalibrationRegressionGateReport = {
  regression_gate_report_id: string;
  generated_at: string;
  passed: boolean;
  eval_dataset_count: number;
  failed_dataset_ids: string[];
};

export type PipelineRun = {
  pipeline_run_id: string;
  document_set_id: string;
  status: string;
  started_at: string;
  completed_at?: string | null;
  failed_step?: string | null;
  error_summary?: string | null;
  config_version: string;
  model_manifest?: PipelineModelManifestItem[];
};

export type PipelineModelManifestItem = {
  agent_id: string;
  agent_role: string;
  provider: string;
  model_name: string;
  model_version: string;
  configured_model_id: string;
  prompt_version: string;
  requirement_ids?: string[];
  requirement_package_hash?: string | null;
  knowledge_pack_ids?: string[];
  missing_knowledge_pack_ids?: string[];
  case_signals?: string[];
  status: string;
  model_run_id?: string | null;
};

export type EvidenceQuote = {
  document_id: string;
  chunk_id: string;
  page: number;
  quote: string;
  support_type: string;
};

export type ReviewPackTopRisk = {
  finding_id: string;
  risk_statement: string;
  severity: string;
  risk_category?: string;
  requirement_references: string[];
  evidence_quotes: EvidenceQuote[];
  found_by_agents: string[];
  contradicted_by_agents: string[];
  no_issue_agents: string[];
  verifier_status: string;
  human_review_reason: string;
  review_status?: "open" | "reviewed" | string;
  review_decision_count?: number;
  latest_review_decision?: ReviewDecisionValue | null;
  latest_reviewed_at?: string | null;
};

export type ReviewPackEvidenceRow = {
  finding_id: string;
  risk_statement: string;
  document_id: string;
  page: number;
  chunk_id: string;
  quote: string;
  requirement_references: string[];
  verifier_status: string;
};

export type FindingReviewChecklistEvidenceRow = Pick<
  ReviewPackEvidenceRow,
  "document_id" | "page" | "chunk_id" | "quote"
>;

export type ReviewPackModelPosition = {
  finding_id: string;
  found_by_agents: string[];
  contradicted_by_agents: string[];
  no_issue_agents: string[];
};

export type ReviewPack = {
  review_pack_id: string;
  document_set_id: string;
  decision: {
    decision: string;
    max_severity?: string;
    auto_clear_allowed?: boolean;
    auto_clear_blockers?: string[];
    required_human_review_reasons?: string[];
  };
  summary: string;
  review_progress_percent?: number;
  reviewed_finding_count?: number;
  total_finding_count?: number;
  top_risks: ReviewPackTopRisk[];
  finding_clusters: unknown[];
  evidence_table: ReviewPackEvidenceRow[];
  model_positions: ReviewPackModelPosition[];
  verifier_results: unknown[];
  ood_reasons: string[];
  coverage_gap_reasons: string[];
  missing_information: string[];
  recommended_reviewer_actions: unknown[];
  audit_references: string[];
};

export type ReviewPackProgressInput = Pick<
  ReviewPack,
  | "review_progress_percent"
  | "reviewed_finding_count"
  | "total_finding_count"
  | "top_risks"
>;

export const hiddenDemoDocumentSetIds = new Set(["ds_demo_avi_threshold"]);

export function isHiddenDemoDocumentSetId(documentSetId: string): boolean {
  return hiddenDemoDocumentSetIds.has(documentSetId);
}

export function isVisibleReviewDocumentSet(documentSet: DocumentSet): boolean {
  return !isHiddenDemoDocumentSetId(documentSet.document_set_id);
}

const plainGermanLabels: Record<string, string> = {
  aseptic_filling: "Sterile Abfüllung",
  batch_impact_assessment: "Chargenauswirkung",
  blocked_due_to_model_failure: "Prüfung notwendig",
  blocked_due_to_unverified_high_risk: "Blockiert: hohes Risiko noch nicht geprüft",
  capa: "CAPA / Korrekturmaßnahme",
  change_control: "Geplante Änderung",
  confirm: "Befund bestätigt",
  critical: "Kritisch",
  deviation_management: "Abweichungsmanagement",
  downgrade: "Herabgestuft",
  escalate_to_qa: "An QA eskaliert",
  high: "Hoch",
  medium: "Mittel",
  missed_critical_risk: "Mögliches übersehenes Risiko",
  missing_required_evidence: "Pflichtnachweis fehlt",
  needs_human_review: "Menschliche Prüfung nötig",
  none: "Nicht belegt",
  partial: "Teilweise belegt",
  qa_approval: "QA-Freigabe",
  ready: "Bereit",
  ready_for_review: "Bereit zur Prüfung",
  reject_false_positive: "Als Fehlalarm markiert",
  request_more_information: "Weitere Unterlagen angefordert",
  reviewed: "Geprüft"
};

const reasonLabels: Record<string, string> = {
  "adversarial challenge involves possible high/critical risk":
    "Eine Gegenprüfung sieht möglicherweise ein hohes oder kritisches Risiko.",
  "audit trail review evidence":
    "Nachweis, dass der Audit Trail geprüft wurde.",
  "batch record reconciliation evidence":
    "Nachweis, dass der Chargenbezug abgeglichen wurde.",
  "documented QA approval decision":
    "Dokumentierte QA-Entscheidung.",
  "human assessment of whether the high-risk impact is covered":
    "Menschliche Bewertung, ob die hohe Auswirkung ausreichend abgedeckt ist.",
  "human review required for high/critical risk":
    "Bei hohem oder kritischem Risiko muss ein qualifizierter Mensch prüfen.",
  "missing information must be resolved by reviewer":
    "Fehlende Informationen müssen in der Prüfung geklärt werden.",
  "missing required document: training record for revised AVI SOP":
    "Pflichtunterlage fehlt: Trainingsnachweis zur geänderten AVI-SOP.",
  "missing required document: validation addendum for new rejection threshold":
    "Pflichtunterlage fehlt: Validierungsnachtrag zum neuen Ausschleuse-Grenzwert.",
  "model disagreement on possible high/critical severity":
    "Die Prüfhelfer sind sich bei einem möglichen hohen oder kritischen Risiko nicht einig.",
  "single high/critical finding is sufficient for human review":
    "Ein einzelner hoher oder kritischer Prüfpunkt reicht aus, damit ein Mensch prüfen muss.",
  "verifier did not pass all deterministic checks":
    "Die automatische Quellenprüfung konnte nicht alles sicher bestätigen."
};

export function displayReviewValue(value?: string | null): string {
  if (!value) return "nicht angegeben";
  return plainGermanLabels[value] ?? value.replaceAll("_", " ");
}

export function displayReviewReason(reason: string): string {
  if (reason.startsWith("required knowledge pack not retrieved:")) {
    return "Ein benötigtes Regelpaket wurde für diese Analyse nicht geladen.";
  }
  return reasonLabels[reason] ?? displayReviewValue(reason);
}

export function displayFeedbackOutcome(outcome: string): string {
  const labels: Record<string, string> = {
    confirmed_risk: "Bestätigt",
    severity_overstated: "Herabgestuft",
    false_positive: "Fehlalarm",
    missing_information: "Mehr Infos",
    linked_to_capa: "CAPA-Link",
    escalated: "Eskalation",
    severity_issue: "Schweregrad falsch",
    evidence_issue: "Quelle falsch",
    requirement_issue: "Regelwerk falsch",
    missed_finding: "Fehlender Befund"
  };
  return labels[outcome] ?? displayReviewValue(outcome);
}

export function displayFeedbackCount(value?: number | null): string {
  return String(value ?? 0);
}

export function displayCalibrationStatus(status: CalibrationExampleStatus): string {
  const labels: Record<CalibrationExampleStatus, string> = {
    raw_feedback: "Rohfeedback",
    approved_gold: "Gold-Beispiel",
    active: "Aktiv"
  };
  return labels[status];
}

export function displayRiskStatement(statement: string): string {
  return riskStatementLabels[statement] ?? statement;
}

export function displayReviewPackSummary(input: {
  decision: string;
  findingCount: number;
  maxSeverity?: string | null;
}): string {
  const parts = [
    displayReviewValue(input.decision),
    `${input.findingCount} Prüfpunkt${input.findingCount === 1 ? "" : "e"} gefunden`
  ];

  if (input.maxSeverity) {
    parts.push(`höchste Einstufung: ${displayReviewValue(input.maxSeverity)}`);
  }

  return `${parts.join(". ")}.`;
}

export function reviewPackProgress(input: ReviewPackProgressInput): {
  percent: number;
  reviewed: number;
  total: number;
  label: string;
} {
  const total = input.total_finding_count ?? input.top_risks.length;
  const reviewed = input.reviewed_finding_count ??
    input.top_risks.filter((risk) => risk.review_status === "reviewed").length;
  const percent = total === 0
    ? 100
    : input.review_progress_percent ?? Math.round((reviewed / total) * 100);

  return {
    percent,
    reviewed,
    total,
    label: `${percent}% bearbeitet (${reviewed} von ${total} Prüfpunkten)`
  };
}

const internalReviewReasonPrefixes = [
  "relevant reviewer role failed:",
  "required reviewer role failed:",
  "missing required reviewer role:",
  "finding lacks requirement reference:",
  "required knowledge pack not retrieved:"
] as const;

const internalReviewReasons = new Set([
  "finding has no requirement references",
  "single high/critical finding is sufficient for human review"
]);

function isInternalReviewReason(reason: string): boolean {
  return internalReviewReasons.has(reason) ||
    internalReviewReasonPrefixes.some((prefix) => reason.startsWith(prefix));
}

export function displayReviewReasons(reason: string): string[] {
  const readableReasons = reason
    .split(";")
    .map((entry) => entry.trim())
    .filter(Boolean)
    .filter((entry) => !isInternalReviewReason(entry))
    .map(displayReviewReason);

  const uniqueReasons = Array.from(new Set(readableReasons));
  return uniqueReasons.length > 0
    ? uniqueReasons
    : ["Analyse unvollständig. Bitte Prüfung erneut starten oder technische Details prüfen."];
}

const missingInformationLabels: Record<string, string> = {
  "approved validation addendum": "genehmigter Validierungsnachtrag",
  "current validation report": "aktueller Validierungsbericht"
};

function displayMissingInformation(value: string): string {
  return missingInformationLabels[value] ?? displayReviewValue(value);
}

function shortQuote(quote: string): string {
  return quote.length > 140 ? `${quote.slice(0, 137)}...` : quote;
}

export function cleanEvidenceQuote(quote: string): string {
  return quote
    .replace(/\*\*/g, "")
    .replace(/\s+/g, " ")
    .replace(/^\d+\s+/, "")
    .trim();
}

export function evidenceSourceLabel(row: FindingReviewChecklistEvidenceRow): string {
  const cleanedQuote = cleanEvidenceQuote(row.quote);
  const documentTypeMatch = cleanedQuote.match(/Dokumenttyp:\s*([^*]+?)(?:\s+Prozessbereich:|\s+Seiten-|$)/i);
  const readableDocument = documentTypeMatch?.[1]?.trim();

  if (readableDocument) {
    return `${readableDocument}, Seite ${row.page}`;
  }

  if (row.document_id.startsWith("doc_")) {
    return `Hochgeladene Unterlage, Seite ${row.page}`;
  }

  return `${row.document_id}, Seite ${row.page}`;
}

export function buildFindingReviewChecklist(input: {
  riskStatement: string;
  requirementReferences: string[];
  verifierStatus: string;
  evidenceRows: FindingReviewChecklistEvidenceRow[];
  missingInformation: string[];
}): string[] {
  const items = [
    `Prüfe den Befund: ${displayRiskStatement(input.riskStatement)}`
  ];

  for (const missing of input.missingInformation.slice(0, 4)) {
    items.push(`Fehlender Nachweis: ${displayMissingInformation(missing)}.`);
  }

  if (input.requirementReferences.length === 0) {
    items.push("Regelwerksbezug prüfen oder nachtragen.");
  }

  if (displayReviewValue(input.verifierStatus) === "Nicht belegt") {
    if (input.evidenceRows.length === 0) {
      items.push("Quelle und Zitat für diesen Befund prüfen oder ergänzen.");
    } else {
      for (const row of input.evidenceRows.slice(0, 2)) {
        items.push(
          `Belegstelle prüfen: ${evidenceSourceLabel(row)}.`
        );
      }
    }
  }

  return Array.from(new Set(items));
}

export const decisionOptions: Array<{ value: ReviewDecisionValue; label: string }> = [
  { value: "confirm", label: "Befund bestätigen" },
  { value: "downgrade", label: "Bewertung herabstufen" },
  { value: "reject_false_positive", label: "Als Fehlalarm markieren" },
  { value: "severity_incorrect", label: "Schweregrad korrigieren" },
  { value: "evidence_incorrect", label: "Quelle passt nicht" },
  { value: "requirement_incorrect", label: "Regelwerk passt nicht" },
  { value: "missed_finding", label: "Fehlenden Befund melden" },
  { value: "request_more_information", label: "Weitere Unterlagen anfordern" },
  { value: "escalate_to_qa", label: "An QA eskalieren" }
];

export function findTopRiskById(
  reviewPack: ReviewPack,
  findingId: string
): ReviewPackTopRisk | undefined {
  return reviewPack.top_risks.find((risk) => risk.finding_id === findingId);
}

export function evidenceRowsForFinding(
  reviewPack: ReviewPack,
  findingId: string
): ReviewPackEvidenceRow[] {
  return reviewPack.evidence_table.filter((row) => row.finding_id === findingId);
}

export function modelPositionForFinding(
  reviewPack: ReviewPack,
  findingId: string
): ReviewPackModelPosition | undefined {
  return reviewPack.model_positions.find((position) => position.finding_id === findingId);
}

export function normalizeReviewDecisionPayload(input: {
  reviewerId: string;
  decision: ReviewDecisionValue;
  rationale: string;
}) {
  return {
    reviewer_id: input.reviewerId.startsWith("reviewer_")
      ? input.reviewerId
      : `reviewer_${input.reviewerId}`,
    decision: input.decision,
    rationale: input.rationale.trim()
  };
}
