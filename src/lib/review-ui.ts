export type ReviewDecisionValue =
  | "confirm"
  | "downgrade"
  | "reject_false_positive"
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

export const consultantReviewCopy = {
  productName: "Pharma QRM Delta Engine",
  workspaceTitle: "QA-Prüfung vorbereiten",
  workspaceDescription:
    "Unterlagen rein. Prüfmappe raus. Ein Mensch entscheidet.",
  nav: {
    cockpit: "Fallakte",
    packages: "Prüfmappen"
  },
  list: {
    title: "Prüfmappen",
    empty:
      "Noch kein echter Prüffall vorhanden. Lade auf der Startseite Unterlagen hoch, dann erscheint hier die Prüfmappe.",
    loadErrorPrefix: "Backend nicht erreichbar",
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
    humanNotice:
      "Entwurf. Das ist nur eine Vorbereitung für die menschliche Prüfung.",
    humanReasons: "Warum ein Mensch prüfen muss",
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
    humanReason: "Warum ein Mensch prüfen muss",
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
    savedMessage: "Entscheidung gespeichert."
  }
} as const;

export const reviewDecisionRequiresHumanRationale = true;

export const aiArchitectureConcept = {
  title: "KI hilft beim Sortieren. Sie entscheidet nicht.",
  subtitle:
    "Das System sucht Risiken, Lücken und passende Quellen. Alles Kritische bleibt bei QA oder Fachexperten.",
  flow: [
    {
      id: "source",
      title: "Quellen",
      description: "Hochgeladene Unterlagen, Textstellen, Aussagen und Regeln."
    },
    {
      id: "primary-reviewers",
      title: "Prüfhelfer",
      description: "Mehrere Prüfhelfer schauen aus unterschiedlichen Blickwinkeln auf den Fall."
    },
    {
      id: "evidence-verifier",
      title: "Quellencheck",
      description: "Zitat, Seite, Textstelle und Regel müssen zusammenpassen."
    },
    {
      id: "adversarial",
      title: "Gegenprüfung",
      description: "Sucht übersehene Risiken und falsche Entwarnungen."
    },
    {
      id: "risk-fusion",
      title: "Zusammenfassung",
      description: "Kein Mehrheitsentscheid. Hohes Risiko bleibt bei Menschen."
    },
    {
      id: "human-review",
      title: "Menschliche Prüfung",
      description: "SME/QA entscheidet mit Begründung."
    }
  ],
  aiRoles: [
    {
      role: "Claim Extractor",
      purpose: "Extrahiert zitierte Aussagen.",
      guardrail: "Keine Aussage ohne Quelle."
    },
    {
      role: "Primary Reviewer Agents",
      purpose: "Suchen fachliche Risiken.",
      guardrail: "Kein Prüfpunkt ohne Nachweis oder klare Lücke."
    },
    {
      role: "Evidence Verifier",
      purpose: "Prüft Zitat gegen Aussage.",
      guardrail: "Schwache Evidenz bleibt offen."
    },
    {
      role: "Adversarial Reviewer",
      purpose: "Sucht übersehene Risiken.",
      guardrail: "Darf nichts schließen."
    },
    {
      role: "Risk Fusion",
      purpose: "Bündelt konservativ.",
      guardrail: "Kein Mehrheitsvoting."
    }
  ],
  nonNegotiables: [
    "KI entscheidet nicht.",
    "Keine Mehrheitsabstimmung.",
    "Keine Aussage ohne Quelle oder klare Lücke.",
    "Hohe und kritische Risiken werden nicht automatisch geschlossen.",
    "QA/SME bleibt letzter Schritt."
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

export type PipelineRun = {
  pipeline_run_id: string;
  document_set_id: string;
  status: string;
  started_at: string;
  completed_at?: string | null;
  failed_step?: string | null;
  error_summary?: string | null;
  config_version: string;
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
    auto_clear_allowed?: boolean;
    auto_clear_blockers?: string[];
    required_human_review_reasons?: string[];
  };
  summary: string;
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
  blocked_due_to_unverified_high_risk: "Blockiert: hohes Risiko noch nicht geprüft",
  capa: "CAPA / Korrekturmaßnahme",
  change_control: "Geplante Änderung",
  critical: "Kritisch",
  deviation_management: "Abweichungsmanagement",
  high: "Hoch",
  medium: "Mittel",
  missed_critical_risk: "Mögliches übersehenes Risiko",
  missing_required_evidence: "Pflichtnachweis fehlt",
  needs_human_review: "Menschliche Prüfung nötig",
  none: "Nicht belegt",
  partial: "Teilweise belegt",
  qa_approval: "QA-Freigabe",
  ready: "Bereit",
  ready_for_review: "Bereit zur Prüfung"
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
  return reasonLabels[reason] ?? displayReviewValue(reason);
}

export const decisionOptions: Array<{ value: ReviewDecisionValue; label: string }> = [
  { value: "confirm", label: "Befund bestätigen" },
  { value: "downgrade", label: "Bewertung herabstufen" },
  { value: "reject_false_positive", label: "Als Fehlalarm markieren" },
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
