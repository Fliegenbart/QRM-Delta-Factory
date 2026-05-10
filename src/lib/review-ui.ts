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
  name: "Prüfbare Risiko-Deltas",
  shortDescription:
    "Für Berater und QA-Teams: Dokumente, Anforderungen, Quellenzitate und Modellbefunde werden zu prüfbaren Review Packs zusammengeführt. Die Entscheidung bleibt beim Menschen.",
  workflow: [
    "1. Demo-Fall oder Kundendokumente bereitstellen",
    "2. Quellen und Anforderungen prüfen lassen",
    "3. Review Pack für SME/QA öffnen",
    "4. Evidenz, Lücken und Modellpositionen nachvollziehen",
    "5. Menschliche Review-Entscheidung dokumentieren"
  ]
} as const;

export const consultantReviewCopy = {
  productName: "Pharma QRM Delta Engine",
  workspaceTitle: "Prüfbare Risiko-Deltas",
  workspaceDescription:
    "Aus Change Controls, FMEAs und GMP-Dokumenten entstehen quellenbasierte Prüfpakete. Das System sortiert vor, zeigt Lücken und bereitet Entscheidungen für SME/QA vor. Es entscheidet nicht selbst.",
  nav: {
    cockpit: "Demo-Cockpit",
    packages: "Prüfpakete"
  },
  list: {
    title: "Vorbereitete Prüfpakete",
    empty:
      "Noch kein Prüfpaket vorhanden. Lege den synthetischen AVI-Demo-Fall an, um Quellen, Pipeline und Review Pack zu sehen.",
    loadErrorPrefix: "Backend nicht erreichbar oder noch nicht konfiguriert",
    columns: {
      package: "Paket",
      trigger: "Anlass",
      area: "Bereich",
      status: "Status",
      sources: "Quellen"
    },
    open: "Paket öffnen"
  },
  seed: {
    idle: "Demo-Fall anlegen",
    seeding: "Demo-Fall wird aufgebaut...",
    created: "Demo-Fall angelegt: Quellen, Pipeline und Prüfmappe sind bereit.",
    refreshed: "Demo-Fall war vorhanden. Pipeline und Prüfmappe wurden aktualisiert.",
    error: "Demo-Fall konnte nicht angelegt werden."
  },
  detail: {
    title: "Paket-Übersicht",
    openReviewPack: "Prüfmappe öffnen",
    sourcesTitle: "Quellen im Paket",
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
    title: "Prüfmappe",
    humanNotice:
      "Menschliche Prüfung bleibt erforderlich. Diese Ansicht zeigt nur die relevanten Zitate und Prüfpunkte, nicht das vollständige Quelldokument.",
    humanReasons: "Warum menschliche Prüfung nötig ist",
    missingInformation: "Offene Unterlagen oder Fragen",
    findingsTitle: "Prüfpunkte",
    emptyFindings: "Diese Prüfmappe enthält aktuell keine Prüfpunkte.",
    requirement: "Regelwerk",
    notLinked: "nicht verknüpft",
    openFinding: "Prüfpunkt ansehen",
    noEntries: "Keine Einträge.",
    loadError:
      "Prüfmappe konnte nicht geladen werden. Starte vorher den Demo-Fall oder die Backend-Pipeline."
  },
  finding: {
    backToPack: "Zurück zur Prüfmappe",
    title: "Prüfpunkt mit Quelle",
    notFound: "Prüfpunkt wurde in der Prüfmappe nicht gefunden.",
    humanReason: "Warum menschliche Prüfung nötig ist",
    evidenceTitle: "Quellenzitate",
    noEvidence: "Keine Quellenzitate in der Prüfmappe verknüpft.",
    document: "Dokument",
    page: "Seite",
    chunk: "Chunk",
    modelPositions: "Systemeinschätzung",
    foundBy: "Gefunden durch",
    contradictedBy: "Widerspruch von",
    noIssueAgents: "Ohne Befund gemeldet",
    decisionForm: "Review-Entscheidung erfassen",
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
      "Dokumentiere kurz, warum du den Befund bestätigst, herabstufst, zurückweist oder weitere Unterlagen brauchst. Nicht allein auf die Modellantwort stützen.",
    rationaleRequired: "Bitte dokumentiere eine kurze menschliche Begründung, bevor du die Entscheidung speicherst.",
    savedMessage: "Review-Entscheidung wurde im Backend-Audit Trail gespeichert."
  }
} as const;

export const reviewDecisionRequiresHumanRationale = true;

export const aiArchitectureConcept = {
  title: "So wird KI im System eingesetzt",
  subtitle:
    "Die KI arbeitet nicht als Entscheider, sondern als kontrollierte Prüfkette: extrahieren, prüfen, widersprechen, verifizieren und für Menschen aufbereiten.",
  flow: [
    {
      id: "source",
      title: "1. Quellen & Anforderungen",
      description: "Dokumente, Chunks, Claims und versionierte Requirements bilden die einzige erlaubte Arbeitsbasis."
    },
    {
      id: "primary-reviewers",
      title: "2. Fachliche Reviewer-KIs",
      description: "Spezialisierte Reviewer suchen parallel nach Risiken in Data Integrity, Deviation, CAPA, Batch Impact und Regulatory Consistency."
    },
    {
      id: "evidence-verifier",
      title: "3. Evidence Verifier",
      description: "Findings werden gegen Dokument-ID, Seite, Chunk, Zitat und Requirement-Anwendbarkeit geprüft."
    },
    {
      id: "adversarial",
      title: "4. Adversarial Review",
      description: "Eine separate KI sucht gezielt nach übersehenen Risiken, Widersprüchen und falschen Entwarnungen."
    },
    {
      id: "risk-fusion",
      title: "5. Conservative Risk Fusion",
      description: "Das System aggregiert konservativ. Ein plausibles High/Critical-Risiko reicht für Human Review."
    },
    {
      id: "human-review",
      title: "6. Menschliche Review-Entscheidung",
      description: "SME, QA oder Regulatory prüfen das Review Pack und dokumentieren die Entscheidung mit Begründung."
    }
  ],
  aiRoles: [
    {
      role: "Claim Extractor",
      purpose: "Macht aus Dokumentstellen zitierte Claims.",
      guardrail: "Kein Claim ohne Quote, Dokument, Seite und Chunk."
    },
    {
      role: "Primary Reviewer Agents",
      purpose: "Suchen fachbereichsspezifische Risiken.",
      guardrail: "Findings brauchen EvidenceItems oder benannte fehlende Information."
    },
    {
      role: "Evidence Verifier",
      purpose: "Prüft, ob die zitierte Stelle die konkrete Aussage wirklich trägt.",
      guardrail: "Schwache, fehlende oder falsche Evidenz wird nicht still geschlossen."
    },
    {
      role: "Adversarial Reviewer",
      purpose: "Sucht nach blinden Flecken und falschen Entwarnungen.",
      guardrail: "Darf Findings nicht schließen, nur neue Fragen oder Challenges erzeugen."
    },
    {
      role: "Risk Fusion",
      purpose: "Bündelt Findings, Verifier-Ergebnisse, OOD und Coverage.",
      guardrail: "Kein simples Mehrheitsvoting; High/Critical bleibt konservativ."
    }
  ],
  nonNegotiables: [
    "Keine regulatorische Entscheidung durch KI.",
    "Kein simples Modell-Mehrheitsvoting.",
    "Keine Aussage ohne Quelle oder klar markierte fehlende Evidenz.",
    "High/Critical Findings werden nicht automatisch geschlossen.",
    "Menschliche QA-/SME-Entscheidung bleibt der letzte Schritt."
  ]
} as const;

export const caseWorkspaceStructure = {
  route: "/case-workspace",
  title: "Fallakte",
  description:
    "Ein zentraler Arbeitsbereich für den gesamten Risiko-Delta-Fall: Überblick, Quellen, Risiko-Deltas, Review Queue und Export.",
  primaryTabs: [
    {
      id: "overview",
      label: "Übersicht",
      helper: "Status, Blocker, Aufwand und nächster Schritt"
    },
    {
      id: "sources",
      label: "Quellen & Anforderungen",
      helper: "Dokumente, Zitate, Risikobibliothek und Regelwerk"
    },
    {
      id: "risk-deltas",
      label: "Risiko-Deltas",
      helper: "Betroffene Risiken, neue Prüfpunkte und Plausibilitätscheck"
    },
    {
      id: "review-queue",
      label: "Review Queue",
      helper: "Priorisierte Arbeit für Author/Ops, SME und QA"
    },
    {
      id: "export",
      label: "Export",
      helper: "Draft Review Pack, CSV/JSON und Audit-Zusammenfassung"
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
