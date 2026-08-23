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


const technicalErrorSignals = [
  "QRM_BACKEND",
  "Backend nicht verbunden",
  "Not Found",
  '{"detail"',
  "fetch failed",
  "ECONNREFUSED",
  "HTTP 5",
  "502",
  "503",
];

export function userFacingReviewLoadError(error: string): { title: string; message: string } {
  if (technicalErrorSignals.some((signal) => error.includes(signal))) {
    return {
      title: "Prüfdienst gerade nicht erreichbar",
      message:
        "Die Verbindung zum Prüfdienst ist unterbrochen. Sie können trotzdem einen neuen Prüffall auf der Startseite vorbereiten oder die Demo-Prüfmappe öffnen. Bitte versuchen Sie es in ein paar Minuten erneut."
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
    empty: "Noch kein echter Prüffall vorhanden. Laden Sie oben Unterlagen hoch, dann erscheint hier der Fall.",
    loadErrorPrefix: "Fallliste konnte nicht geladen werden",
    columns: {
      package: "Prüffall",
      trigger: "Anlass",
      area: "Bereich",
      status: "Status",
      sources: "Unterlagen"
    },
    open: "Öffnen",
    examplesTitle: "Drei Beispiele: So sieht eine fertige Prüfmappe aus.",
    examplesDescription:
      "Echte Prüfläufe über synthetische Unterlagen aus dem Ringversuch — jedes Urteil mit Zitat, nichts nachbearbeitet. Klicken Sie sich durch, bevor Sie eigene Unterlagen hochladen.",
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
      "Prüfmappe nicht verfügbar. Laden Sie zuerst Unterlagen hoch und starten Sie die Prüfung."
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
    "Erforderliche Nachweise fehlen oder sind in den Quellen nicht klar belegt.",
  "Deviation impact needs human review against documented requirements.":
    "Die Auswirkungen der Abweichung müssen anhand der dokumentierten Anforderungen geprüft werden.",
  "Batch-linked deviation requires documented batch impact trace.":
    "Für die chargenbezogene Abweichung fehlt eine dokumentierte Bewertung der Chargenauswirkung.",
  "CAPA reference requires effectiveness evidence if linked to quality risk.":
    "Für die CAPA-Verknüpfung fehlt ein Wirksamkeitsnachweis zum Qualitätsrisiko.",
  "QA approval appears pending and should not be treated as closed.":
    "Die QA-Freigabe ist noch offen und darf nicht als abgeschlossen behandelt werden."
};

export const aiArchitectureConcept = {
  title: "Der Weg eines Befunds — und acht Stellen, an denen geprüft wird.",
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
      id: "facts",
      title: "Fakten erfassen",
      description:
        "Messwerte, Grenzwerte, Daten, Unterschriften und Maßnahmen werden als strukturierte Fakten erfasst — jeder mit dem wörtlichen Zitat, aus dem er stammt. Das Modell schreibt ab; es bewertet hier nichts.",
      safeguard:
        "Sicherung: Jedes Zitat wird Zeichen für Zeichen im Quelltext gesucht. Ein Fakt, der sich dort nicht wiederfindet, wird verworfen und gezählt."
    },
    {
      id: "rules",
      title: "Regeln rechnen",
      description:
        "Feste Prüfregeln entscheiden ohne Modell: Messwert gegen Grenze, Datumsfolge, Vier-Augen-Prinzip, Wirksamkeitsprüfung, leere Pflichtfelder. Jede Regel nennt, was sie prüft und auf welcher regulatorischen Grundlage — der Katalog steht im Regelwerk.",
      safeguard: "Sicherung: Ein Regelbefund hebt eine Anforderung auf „verletzt“. Er senkt nie."
    },
    {
      id: "scope-router",
      title: "Den Fall einordnen",
      description:
        "Dokumenttyp, Prozessbereich und fachliche Signale bestimmen, welche Regelpakete für diesen Fall überhaupt gelten.",
      safeguard: "Sicherung: Die Prüfer bekommen nur die Regeln, die zum Fall passen — kein Streuschuss."
    },
    {
      id: "requirements",
      title: "Anforderung für Anforderung urteilen",
      description:
        "Für jede Anforderung des Regelwerks sucht das Modell zuerst die Belegstellen und urteilt dann allein über diese Zitate: erfüllt, verletzt oder unklar. Zwei kleine Fragen statt einer großen — so trägt auch ein lokal laufendes Modell die Prüfung. Sieben Fachprüfer ergänzen die Befundsicht.",
      safeguard:
        "Sicherung: Kein Urteil ohne Zitat. Fehlt der Beleg, wird noch einmal gesucht; bleibt er aus, steht „unklar“ statt „erfüllt“."
    },
    {
      id: "evidence-verifier",
      title: "Quellen abgleichen",
      description:
        "Jeder Befund wird gegen seinen Beleg geprüft: Stimmt das Zitat? Passt die Seite? Trägt die Textstelle die Aussage? Diese Prüfung macht fester Programmcode, keine KI — Zeichen für Zeichen. Danach prüft eine zweite Modellinstanz nur noch, ob das Zitat die Begründung wirklich trägt.",
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
    "Fehlt ein nötiges Regelpaket, blockiert das die Freigabe.",
    "Die Modelle sind austauschbar, die Prüfkette nicht: Sie läuft mit Cloud-Modellen oder komplett auf eigener Hardware."
  ]
} as const;

export type ModelRoles = {
  stack: string;
  finding_reviewers: string;
  requirement_assessor: string;
  requirement_assessor_mode: string;
  entailment_checker: string;
  critics: string;
};

export type BackendHealth = {
  status: string;
  app_name: string;
  app_version: string;
  environment: string;
  model_roles?: ModelRoles;
};

const PROVIDER_LABELS: Record<string, string> = {
  anthropic: "Claude (Anthropic)",
  openai: "GPT (OpenAI)",
  hetzner: "Qwen auf dem EU-/Kundenserver",
  mock: "Offline-Stellvertreter (kein Modell)",
  none: "keiner"
};

export function describeProvider(name: string): string {
  const key = name.trim().toLowerCase();
  if (key in PROVIDER_LABELS) return PROVIDER_LABELS[key];
  if (key.startsWith("per-role mix")) return "Claude und GPT, nach Rolle verteilt";
  return name
    .split(",")
    .map((part) => PROVIDER_LABELS[part.trim().toLowerCase()] ?? part.trim())
    .join(", ");
}

export function describeModelStack(roles: ModelRoles): {
  label: string;
  summary: string;
  rows: { label: string; value: string }[];
} {
  const stackLabel: Record<string, { label: string; summary: string }> = {
    cloud: {
      label: "Cloud-Stack",
      summary:
        "Claude liest, GPT prüft nach. Zwei Modellfamilien, damit der Prüfer nicht die blinden Flecken des Lesers teilt."
    },
    local: {
      label: "Lokaler Stack",
      summary:
        "Jede Anfrage geht an einen Endpunkt unter eigener Kontrolle. Kein Dokument erreicht Anthropic oder OpenAI."
    },
    cascade: {
      label: "Kaskade",
      summary:
        "Die Dokumente werden nur lokal gelesen. Nachgeprüft werden allein Zitat und Begründung — nie das Dokument — durch eine zweite Modellfamilie."
    }
  };
  const described = stackLabel[roles.stack] ?? {
    label: roles.stack,
    summary: "Unbekannter Stack — die Rollen unten zeigen, was tatsächlich läuft."
  };
  return {
    ...described,
    rows: [
      { label: "Dokumente lesen und urteilen", value: describeProvider(roles.requirement_assessor) },
      {
        label: "Prüfmodus",
        value:
          roles.requirement_assessor_mode === "narrow"
            ? "pro Anforderung: erst Belege suchen, dann urteilen"
            : "gruppiert: sechs Anforderungen je Aufruf mit allen Quellen"
      },
      { label: "Zitat trägt Begründung?", value: describeProvider(roles.entailment_checker) },
      { label: "Fachprüfer (Befundsicht)", value: describeProvider(roles.finding_reviewers) },
      { label: "Gegenprüfer", value: describeProvider(roles.critics) }
    ]
  };
}

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

/**
 * The intake vocabulary: what a reviewer can pick when creating a case.
 *
 * It lives here rather than in the uploader because the same values come back
 * out of the backend and have to be rendered as German on the case view. When
 * the two lists lived apart, seven of the twelve options had no label at all
 * and a case created as "Abweichung" read back as "deviation package".
 */
export const intakeDocumentTypes = [
  { value: "change_control_package", label: "Change Control" },
  { value: "deviation_package", label: "Abweichung" },
  { value: "capa_package", label: "CAPA" },
  { value: "audit_finding_package", label: "Audit-Finding" },
  { value: "periodic_review_package", label: "Periodic Review" }
] as const;

export const intakeProcessAreas = [
  { value: "aseptic_filling", label: "Aseptische Abfüllung" },
  { value: "automated_visual_inspection", label: "Automatische Sichtprüfung" },
  { value: "cleaning_validation", label: "Reinigung" },
  { value: "qc_lab", label: "QC-Labor" },
  { value: "data_integrity", label: "Datenintegrität" },
  { value: "supplier_quality", label: "Lieferant/Material" },
  { value: "computerized_system", label: "Computergestütztes System" }
] as const;

export type DocumentSummary = {
  document_id: string;
  filename: string;
  mime_type: string;
  page_count: number;
  parsing_status: string;
  parsing_quality_score: number;
  language: string;
};

/**
 * Documents whose text was never read.
 *
 * A case can complete and publish a review pack while every one of its
 * documents failed to parse -- the pack is then assembled from nothing. The
 * case view must say so instead of showing a green "Analyse abgeschlossen".
 */
export function unreadableDocuments(documents: DocumentSummary[]): DocumentSummary[] {
  return documents.filter((document) => document.parsing_status !== "parsed");
}

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

/** One deterministic rule, as the rulebook page shows it. */
export type RuleDescription = {
  validator_id: string;
  title: string;
  checks: string;
  inputs: string;
  severity: string;
  regulatory_basis: string;
  requirement_ids: string[];
  version: string;
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
  /** Where a running pipeline is; absent on older backends and finished runs. */
  progress?: PipelineProgress | null;
};

export type PipelineProgress = {
  step: string;
  step_index: number;
  step_count: number;
  detail?: string | null;
  updated_at: string;
};

/** The pipeline's steps in the reviewer's words, in execution order. */
export const PIPELINE_STEP_LABELS: Record<string, string> = {
  parse_document_set: "Unterlagen lesen",
  quality_gate: "Lesbarkeit prüfen",
  requirement_retrieval: "Regelwerk zuordnen",
  claim_ledger_extraction: "Aussagen herauslesen",
  primary_multi_agent_review: "Fachprüfer lesen die Unterlagen",
  evidence_verification: "Zitate gegen den Quelltext prüfen",
  adversarial_review: "Gegenprüfung",
  objective_red_flag_scan: "Objektive Warnsignale suchen",
  adversarial_evidence_verification: "Zitate der Gegenprüfung prüfen",
  risk_fusion: "Risiken bündeln",
  review_pack_generation: "Prüfmappe zusammenstellen",
  requirement_coverage_review: "Anforderung für Anforderung urteilen",
  audit_trail_completion: "Audit-Trail abschließen"
};

export function pipelineStepLabel(step: string): string {
  return PIPELINE_STEP_LABELS[step] ?? step.replaceAll("_", " ");
}

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
  supporting_finding_ids?: string[];
  supporting_finding_count?: number;
  supporting_signals?: Array<{
    finding_id: string;
    risk_statement: string;
    severity: string;
    evidence_quotes: EvidenceQuote[];
    verifier_status: string;
  }>;
};

export type ReviewPackEvidenceRow = {
  finding_id: string;
  risk_statement: string;
  document_id: string;
  document_name?: string | null;
  page: number;
  chunk_id: string;
  quote: string;
  requirement_references: string[];
  verifier_status: string;
};

export type FindingReviewChecklistEvidenceRow = Pick<
  ReviewPackEvidenceRow,
  "document_id" | "document_name" | "page" | "chunk_id" | "quote"
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
    operational_blockers?: string[];
    model_coverage_status?: string;
  };
  summary: string;
  decision_summary?: string;
  operational_warnings?: string[];
  raw_finding_count?: number;
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
  auto_clear_candidate: "Keine auffälligen Prüfpunkte",
  batch_impact_assessment: "Chargenauswirkung",
  batch_record: "Chargenprotokoll",
  blocked_due_to_model_failure: "Prüfung notwendig",
  blocked_due_to_unverified_high_risk: "Blockiert: hohes Risiko noch nicht geprüft",
  capa: "CAPA / Korrekturmaßnahme",
  capa_plan: "CAPA-Plan",
  change_control: "Geplante Änderung",
  complete: "Vollständig",
  completed: "Analyse abgeschlossen",
  confirm: "Befund bestätigt",
  critical: "Kritisch",
  data_integrity: "Datenintegrität",
  deviation_management: "Abweichungsmanagement",
  downgrade: "Herabgestuft",
  escalate_to_qa: "An QA eskaliert",
  failed: "Fehlgeschlagen",
  high: "Hoch",
  deviation: "Abweichung",
  human_review_required: "Menschliche Prüfung nötig",
  incomplete: "Unvollständig",
  informational: "Informativ",
  // RiskDecisionClass.INSUFFICIENT_DOCUMENT_QUALITY. Without this entry the raw
  // English enum was rendered as a badge on the customer's Prüfmappe.
  insufficient_document_quality: "Unterlagen zu unvollständig für ein Urteil",
  medium: "Mittel",
  missed_critical_risk: "Mögliches übersehenes Risiko",
  missing_required_evidence: "Pflichtnachweis fehlt",
  needs_human_review: "Menschliche Prüfung nötig",
  needs_more_information: "Weitere Unterlagen nötig",
  none: "Nicht belegt",
  out_of_scope: "Außerhalb des Regelbereichs",
  partial: "Teilweise belegt",
  qa_approval: "QA-Freigabe",
  ready: "Bereit",
  ready_for_orchestration: "Bereit zur Analyse",
  ready_for_review: "Bereit zur Prüfung",
  reject_false_positive: "Als Fehlalarm markiert",
  request_more_information: "Weitere Unterlagen angefordert",
  reviewed: "Geprüft",
  running: "Läuft",
  strong: "Belegt",
  weak: "Schwach belegt"
};

const reasonLabels: Record<string, string> = {
  "adversarial challenge involves possible high/critical risk":
    "Eine Gegenprüfung sieht möglicherweise ein hohes oder kritisches Risiko.",
  "adversarial challenge names missing evidence":
    "Eine Gegenprüfung benennt fehlende Nachweise.",
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
  "high/critical finding has weak or partial evidence":
    "Ein hoher oder kritischer Prüfpunkt ist nur schwach oder teilweise belegt.",
  "missing information must be resolved by reviewer":
    "Fehlende Informationen müssen in der Prüfung geklärt werden.",
  "no matching requirements found":
    "Für diesen Fall wurde kein passendes Regelwerk gefunden.",
  "root cause claim": "Dokumentierte Ursachenanalyse.",
  "CAPA effectiveness check evidence": "Nachweis der CAPA-Wirksamkeitsprüfung.",
  "missing required document: training record for revised AVI SOP":
    "Pflichtunterlage fehlt: Trainingsnachweis zur geänderten AVI-SOP.",
  "missing required document: validation addendum for new rejection threshold":
    "Pflichtunterlage fehlt: Validierungsnachtrag zum neuen Ausschleuse-Grenzwert.",
  "model disagreement on possible high/critical severity":
    "Die Prüfhelfer sind sich bei einem möglichen hohen oder kritischen Risiko nicht einig.",
  "single high/critical finding is sufficient for human review":
    "Ein einzelner hoher oder kritischer Prüfpunkt reicht aus, damit ein Mensch prüfen muss.",
  "unusually few claims":
    "Aus dem Dokument wurden ungewöhnlich wenige prüfbare Aussagen extrahiert.",
  "unusually many unclear claims":
    "Ungewöhnlich viele Aussagen im Dokument sind unklar oder nicht eindeutig.",
  "verifier did not pass all deterministic checks":
    "Die automatische Quellenprüfung konnte nicht alles sicher bestätigen."
};

/**
 * The wording the reviewer chose at intake, keyed by the value the backend
 * stores. Derived rather than hand-copied so a case can never read back in
 * different words than the dropdown offered.
 */
const intakeLabels: Record<string, string> = Object.fromEntries(
  [...intakeDocumentTypes, ...intakeProcessAreas].map((option) => [
    option.value,
    option.label
  ])
);

export function displayReviewValue(value?: string | null): string {
  if (!value) return "nicht angegeben";
  return intakeLabels[value] ?? plainGermanLabels[value] ?? value.replaceAll("_", " ");
}

export function displayReviewReason(reason: string): string {
  if (reason.startsWith("required knowledge pack not retrieved:")) {
    return "Ein benötigtes Regelpaket wurde für diese Analyse nicht geladen.";
  }
  if (reason.startsWith("missing required document:")) {
    const document = reason.replace("missing required document:", "").trim();
    return `Pflichtunterlage fehlt: ${displayReviewValue(document)}.`;
  }
  const inapplicableRequirementPrefix = [
    "requirement id is not applicable to document/process area:",
    "requirement_id is not applicable to document/process area:"
  ].find((prefix) => reason.startsWith(prefix));
  if (inapplicableRequirementPrefix) {
    const requirementId = reason.replace(inapplicableRequirementPrefix, "").trim();
    return `Regelwerksbezug passt nicht zum Dokumenttyp oder Prozessbereich: ${displayReviewValue(requirementId)}.`;
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

export type ReviewPackRiskPresentation = {
  summary: string;
  rootRisks: ReviewPackTopRisk[];
  supportingFindingCount: number;
  operationalWarnings: string[];
  modelCoverageStatus?: string;
};

export function reviewPackRiskPresentation(
  input: Pick<
    ReviewPack,
    "decision" | "decision_summary" | "operational_warnings" | "raw_finding_count" | "top_risks"
  >
): ReviewPackRiskPresentation {
  const supportingIds = new Set(
    input.top_risks.flatMap((risk) => risk.supporting_finding_ids ?? [])
  );
  const rootRisks = input.top_risks.filter((risk) => !supportingIds.has(risk.finding_id));
  const rootRiskCount = rootRisks.length;
  const supportingById = supportingIds.size;
  const supportingByCount = rootRisks.reduce(
    (total, risk) => total + Math.max(0, risk.supporting_finding_count ?? 0),
    0
  );
  const supportingByRawCount = Math.max(0, (input.raw_finding_count ?? 0) - rootRiskCount);

  return {
    summary:
      input.decision_summary?.trim() || `${displayReviewValue(input.decision.decision)}.`,
    rootRisks,
    supportingFindingCount: Math.max(supportingById, supportingByCount, supportingByRawCount),
    operationalWarnings: uniqueReviewMessages([
      ...(input.operational_warnings ?? []),
      ...(input.decision.operational_blockers ?? [])
    ]),
    modelCoverageStatus: input.decision.model_coverage_status
      ? displayReviewValue(input.decision.model_coverage_status)
      : undefined
  };
}

function uniqueReviewMessages(values: string[]): string[] {
  return [...new Set(values.map((value) => value.trim()).filter(Boolean))];
}

export function reviewPackProgress(input: ReviewPackProgressInput): {
  percent: number;
  reviewed: number;
  total: number;
  label: string;
} {
  const total = Math.max(0, input.total_finding_count ?? input.top_risks.length);
  const reviewed = Math.min(
    total,
    Math.max(
      0,
      input.reviewed_finding_count ??
        input.top_risks.filter((risk) => risk.review_status === "reviewed").length
    )
  );

  if (total === 0) {
    return { percent: 0, reviewed: 0, total: 0, label: "Keine Prüfpunkte zur Bearbeitung" };
  }

  const percent = Math.min(
    100,
    Math.max(0, input.review_progress_percent ?? Math.round((reviewed / total) * 100))
  );

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

export function displayMissingInformationList(values: string[]): string[] {
  return Array.from(
    new Set(values.map((entry) => entry.trim()).filter(Boolean).map(displayMissingInformation))
  );
}

function shortQuote(quote: string): string {
  return quote.length > 140 ? `${quote.slice(0, 137)}...` : quote;
}

export function cleanEvidenceQuote(quote: string): string {
  return quote
    .replace(/\*\*/g, "")
    .replace(/\s+/g, " ")
    .replace(/^\d+\s+(?!CFR\b|EU\b|GMP\b|ISO\b)/, "")
    .trim();
}

export function evidenceSourceLabel(row: FindingReviewChecklistEvidenceRow): string {
  const documentName = row.document_name?.trim();
  if (documentName) {
    return `${documentName}, Seite ${row.page}`;
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
    `Prüfen Sie den Befund: ${displayRiskStatement(input.riskStatement)}`
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

/**
 * The requirement coverage report: one verdict per obligation.
 *
 * Deliberately not folded into ReviewPack. The pack is organised around a
 * risk decision with findings as rows; this report is organised around the
 * requirements themselves, which is the question a QA reviewer actually
 * asks -- is every obligation met, and where is the proof. Mixing them would
 * blur exactly that distinction.
 */
export type RequirementVerdictStatus =
  | "fulfilled"
  | "violated"
  | "unclear"
  | "not_applicable";

export type RequirementReportRetry = {
  /** Rows a failed model call left as placeholders. */
  retryable: number;
  active: boolean;
  detail?: string | null;
};

export type RequirementReportEvidence = {
  document_id: string;
  chunk_id: string;
  page: number;
  quote: string;
  /** File name, filled server-side; absent on reports from older engines. */
  document_name?: string;
};

/** "Abweichungsbericht.md, Seite 3" -- where a quote can be checked. */
export function evidenceLocationLabel(item: Pick<RequirementReportEvidence, "document_name" | "page">): string {
  return item.document_name ? `${item.document_name}, Seite ${item.page}` : `Seite ${item.page}`;
}

export type RequirementVerdictRow = {
  requirement_id: string;
  requirement_title: string | null;
  requirement_text: string;
  source_name: string;
  section: string;
  model_status: RequirementVerdictStatus;
  published_status: RequirementVerdictStatus;
  severity: string | null;
  rationale: string;
  evidence: RequirementReportEvidence[];
  dropped_evidence_count: number;
  dropped_evidence_reasons: string[];
  provenance_ok: boolean;
  entailment: "supports" | "partial" | "none" | null;
  entailment_reason: string | null;
  evidence_type: string | null;
  evidence_reference: string | null;
  evidence_sufficiency: "sufficient" | "partial" | "insufficient" | null;
  independent_support: boolean | null;
  challenge_sustained: boolean | null;
  challenge_reason: string | null;
  sample_disagreement: boolean;
  validator_flags: string[];
  validator_statements: string[];
  server_authored: boolean;
  /** A model call behind this row failed; the row can be re-run on its own. */
  needs_retry?: boolean;
};

export type RequirementCoverageReport = {
  document_set_id: string;
  engine_version: string;
  created_at: string;
  verdicts: RequirementVerdictRow[];
  status_counts: Record<string, number>;
  model_calls: {
    purpose: string;
    provider: string;
    model_id: string;
    requirement_ids: string[];
    status: string;
    error_type: string | null;
    error_summary: string | null;
    input_tokens: number;
    output_tokens: number;
  }[];
  failed_model_call_count: number;
  validator_findings: Record<string, unknown>[];
  extracted_evidence?: {
    counts: Record<string, number>;
    dropped_unverifiable: Record<string, number>;
    rows: Record<string, unknown[]>;
  } | null;
};

/**
 * What the deterministic layer did, in the reviewer's words.
 *
 * The model reads; rules decide what rules can decide -- a value against its
 * limit, a step dated before the event it concerns, a CAPA with no
 * effectiveness check. Showing the reviewer how many typed rows were
 * extracted and how many rules fired is what makes that layer something a
 * QA department can validate, instead of a black box with a percentage.
 */
export function deterministicCheckSummary(report: RequirementCoverageReport): {
  rows: { label: string; count: number }[];
  findings: number;
  dropped: number;
} | null {
  const extracted = report.extracted_evidence;
  if (!extracted) return null;
  const labels: Record<string, string> = {
    signatures: "Signaturfelder",
    measurements: "Messwerte",
    specifications: "Grenzwerte",
    action_items: "Maßnahmen",
    events: "Datierte Schritte"
  };
  const rows = Object.entries(labels)
    .map(([key, label]) => ({ label, count: extracted.counts[key] ?? 0 }))
    .filter((row) => row.count > 0);
  const dropped = Object.values(extracted.dropped_unverifiable ?? {}).reduce((a, b) => a + b, 0);
  return { rows, findings: report.validator_findings.length, dropped };
}

export const REQUIREMENT_STATUS_LABELS: Record<RequirementVerdictStatus, string> = {
  violated: "Verletzt",
  unclear: "Unklar",
  fulfilled: "Erfüllt",
  not_applicable: "Nicht anwendbar"
};

/** Reviewer order: what needs action first, what needs nothing last. */
export const REQUIREMENT_STATUS_ORDER: RequirementVerdictStatus[] = [
  "violated",
  "unclear",
  "fulfilled",
  "not_applicable"
];

/**
 * What a reviewer can lean on, and where they must look themselves.
 *
 * Derived only from recorded facts -- provenance, entailment, the adversarial
 * second look, sample disagreement -- never from the model's own confidence.
 */
export function requirementConfidenceNotes(row: RequirementVerdictRow): string[] {
  const notes: string[] = [];
  if (row.server_authored) {
    notes.push("Vom Server beantwortet, ohne Modellaufruf");
  }
  if (!row.provenance_ok && !row.server_authored) {
    notes.push(
      row.dropped_evidence_count > 0
        ? `${row.dropped_evidence_count} Zitat(e) nicht im Quelltext auffindbar`
        : "Belegprüfung nicht vollständig bestanden"
    );
  }
  if (row.entailment === "partial") {
    notes.push("Zweitmodell: Belege tragen die Aussage nur teilweise");
  }
  if (row.entailment === "supports") {
    notes.push("Zweitmodell bestätigt: Belege tragen die Aussage");
  }
  if (row.challenge_sustained === true) {
    notes.push("Skeptische Zweitprüfung hat Einwände bestätigt");
  }
  if (row.challenge_sustained === false) {
    notes.push("Skeptische Zweitprüfung ohne Einwand");
  }
  if (row.sample_disagreement) {
    notes.push("Unabhängige Durchgänge waren uneins — vorsichtigere Bewertung gewählt");
  }
  if (row.independent_support === false && row.published_status === "fulfilled") {
    notes.push("Nachweis stützt sich auf Selbstauskunft des Vorgangs");
  }
  if (row.evidence_sufficiency === "partial") {
    notes.push("Nachweis nur teilweise ausreichend");
  }
  // The same breach is often found in several places -- a value quoted in
  // the deviation report, the batch record and the summary fires the rule
  // three times with one statement. Say it once; the evidence list carries
  // every location.
  for (const statement of new Set(row.validator_statements)) {
    notes.push(`Deterministische Prüfung: ${statement}`);
  }
  return notes;
}

/** Coverage in one line: how much of the obligation set is settled. */
export function requirementCoverageProgress(report: RequirementCoverageReport): {
  answered: number;
  total: number;
  needsAttention: number;
  percent: number;
} {
  const total = report.verdicts.length;
  const needsAttention = report.verdicts.filter(
    (row) => row.published_status === "violated" || row.published_status === "unclear"
  ).length;
  const answered = total - needsAttention;
  return {
    answered,
    total,
    needsAttention,
    percent: total === 0 ? 0 : Math.round((answered / total) * 100)
  };
}
