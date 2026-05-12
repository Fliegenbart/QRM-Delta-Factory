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
  demoSeedRoute: "/api/review-ui/demo-seed",
  replacesLegacyDeltaAnalysis: true,
  name: "Risk Delta Review",
  shortDescription:
    "Aus GMP-Dokumenten wird ein Review Pack mit Quellen, Lücken und nächstem Prüfschritt.",
  workflow: [
    "Dokumente laden",
    "Claims und Requirements prüfen",
    "Findings verifizieren",
    "Review Pack öffnen",
    "Entscheidung dokumentieren"
  ]
} as const;

export const consultantReviewCopy = {
  productName: "Pharma QRM Delta Engine",
  workspaceTitle: "Risk Delta Review",
  workspaceDescription:
    "Quellen rein. Review Pack raus. QA entscheidet.",
  nav: {
    cockpit: "Fallakte",
    packages: "Review Packs"
  },
  list: {
    title: "Review Packs",
    empty:
      "Noch kein Fall. Starte die Demo und öffne das Review Pack.",
    loadErrorPrefix: "Backend nicht erreichbar",
    columns: {
      package: "Paket",
      trigger: "Anlass",
      area: "Bereich",
      status: "Status",
      sources: "Quellen"
    },
    open: "Öffnen"
  },
  seed: {
    idle: "Demo starten",
    seeding: "Pipeline läuft...",
    created: "Review Pack bereit.",
    refreshed: "Review Pack aktualisiert.",
    error: "Demo konnte nicht starten."
  },
  detail: {
    title: "Fall",
    openReviewPack: "Review Pack öffnen",
    sourcesTitle: "Quellen",
    noSources: "Keine Quellen verknüpft.",
    loadErrorPrefix: "Prüfpaket konnte nicht geladen werden",
    labels: {
      packageId: "Paket-ID",
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
    title: "Review Pack",
    humanNotice:
      "Draft. Nur Entscheidungsunterstützung.",
    humanReasons: "Warum Review nötig ist",
    missingInformation: "Fehlt noch",
    findingsTitle: "Findings",
    emptyFindings: "Keine Findings.",
    requirement: "Regelwerk",
    notLinked: "nicht verknüpft",
    openFinding: "Ansehen",
    noEntries: "Keine Einträge.",
    loadError:
      "Review Pack nicht verfügbar. Starte zuerst die Demo."
  },
  finding: {
    backToPack: "Zurück",
    title: "Finding",
    notFound: "Finding nicht gefunden.",
    humanReason: "Review-Grund",
    evidenceTitle: "Evidenz",
    noEvidence: "Keine Evidenz verknüpft.",
    document: "Dokument",
    page: "Seite",
    chunk: "Chunk",
    modelPositions: "Modellpositionen",
    foundBy: "Gefunden durch",
    contradictedBy: "Widerspruch von",
    noIssueAgents: "Ohne Befund gemeldet",
    decisionForm: "Entscheidung",
    loadErrorPrefix: "Finding konnte nicht geladen werden",
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
  title: "KI als Prüfteam. Nicht als Entscheider.",
  subtitle:
    "Mehrere Modelle prüfen arbeitsteilig. Jede Aussage braucht Evidenz. Risk Fusion eskaliert konservativ.",
  flow: [
    {
      id: "source",
      title: "Quellen",
      description: "Dokumente, Chunks, Claims, Requirements."
    },
    {
      id: "primary-reviewers",
      title: "Reviewer-KIs",
      description: "OpenAI, Claude und Gemini prüfen getrennte Risikobereiche."
    },
    {
      id: "evidence-verifier",
      title: "Verifier",
      description: "Zitat, Seite, Chunk und Requirement müssen passen."
    },
    {
      id: "adversarial",
      title: "Adversarial Review",
      description: "Sucht blinde Flecken und falsche Entwarnungen."
    },
    {
      id: "risk-fusion",
      title: "Risk Fusion",
      description: "Kein Voting. High/Critical bleibt bei Menschen."
    },
    {
      id: "human-review",
      title: "Human Review",
      description: "SME/QA entscheidet mit Begründung."
    }
  ],
  aiRoles: [
    {
      role: "Claim Extractor",
      purpose: "Extrahiert zitierte Aussagen.",
      guardrail: "Kein Claim ohne Quelle."
    },
    {
      role: "Primary Reviewer Agents",
      purpose: "Suchen fachliche Risiken.",
      guardrail: "Kein Finding ohne Evidenz oder Gap."
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
    "Keine Aussage ohne Quelle oder Gap.",
    "High/Critical wird nicht automatisch geschlossen.",
    "QA/SME bleibt letzter Schritt."
  ]
} as const;

export const caseWorkspaceStructure = {
  route: "/case-workspace",
  title: "Fallakte",
  description:
    "Ein Fall. Quellen, Findings, Review und Export.",
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

export type DemoSeedResponse = {
  created: boolean;
  document_set: DocumentSet;
  pipeline_run: PipelineRun;
  review_pack: ReviewPack;
};

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
