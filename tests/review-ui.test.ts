import { describe, expect, it } from "vitest";
import {
  caseWorkspaceStructure,
  aiArchitectureConcept,
  consultantReviewCopy,
  demoReviewCases,
  buildFindingReviewChecklist,
  cleanEvidenceQuote,
  decisionOptions,
  displayReviewReason,
  displayReviewReasons,
  displayReviewPackSummary,
  displayRiskStatement,
  displayReviewValue,
  displayFeedbackOutcome,
  displayFeedbackCount,
  displayCalibrationStatus,
  evidenceSourceLabel,
  findTopRiskById,
  reviewPackProgress,
  isHiddenDemoDocumentSetId,
  isVisibleReviewDocumentSet,
  normalizeReviewDecisionPayload,
  reviewDecisionRequiresHumanRationale,
  supabasePublicEnvKeys,
  hasSupabasePublicConfig,
  productHomeCopy,
  riskOrchestrationEntry,
  userFacingReviewLoadError,
  type ReviewPack
} from "@/src/lib/review-ui";
import { getReviewBackendConfig } from "@/src/lib/review-runtime-config";

describe("review UI helpers", () => {
  it("marks the backend review workbench as the replacement for legacy delta analysis", () => {
    expect(riskOrchestrationEntry.replacesLegacyDeltaAnalysis).toBe(true);
    expect(riskOrchestrationEntry.legacyDeltaRoute).toBe("/delta-analysis");
    expect(riskOrchestrationEntry.reviewWorkbenchRoute).toBe("/review-ui");
    expect(riskOrchestrationEntry.name).toBe("QA-Prüfung vorbereiten");
    expect(riskOrchestrationEntry.shortDescription).toContain("Prüfmappe");
    expect(riskOrchestrationEntry.shortDescription).toContain("Quellen");
    expect(riskOrchestrationEntry.workflow).toContain("Unterlagen hochladen");
    expect(riskOrchestrationEntry.workflow).toContain("Prüfmappe öffnen");
  });

  it("uses consultant-friendly copy for the backend review UI", () => {
    expect(consultantReviewCopy.workspaceTitle).toBe("QA-Prüfung vorbereiten");
    expect(consultantReviewCopy.workspaceDescription).toBe("Unterlagen rein. Prüfmappe raus. Ein Mensch entscheidet.");
    expect(consultantReviewCopy.list.title).toBe("Prüffälle");
    expect(consultantReviewCopy.list.empty).toContain("Startseite");
    expect(consultantReviewCopy.finding.title).toBe("Prüfpunkt");
    expect(consultantReviewCopy.decision.savedMessage).toContain("Bearbeitungsstand");
    expect(reviewDecisionRequiresHumanRationale).toBe(true);
    expect(consultantReviewCopy.decision.rationaleRequired).toContain("begründen");
  });

  it("states the product USP in plain QA language", () => {
    expect(productHomeCopy.title).toBe("QA-Prüfung aus GMP-Unterlagen vorbereiten");
    expect(productHomeCopy.subtitle).toContain("Change-, CAPA- oder Abweichungsunterlagen");
    expect(productHomeCopy.subtitle).toContain("Prüfpunkte");
    expect(productHomeCopy.valueLine).toBe("Unterlagen rein → Prüfmappe raus → QA entscheidet.");
    expect(productHomeCopy.decisionLine).toBe("Nicht noch ein Dashboard. Eine entscheidungsreife Prüfmappe.");
    expect(productHomeCopy.primaryAction).toBe("Prüffall vorbereiten");
    expect(productHomeCopy.workflow).toEqual([
      "Unterlagen hochladen",
      "Prüfpunkte und Quellen sehen",
      "Lücken klären",
      "QA-Entscheidung dokumentieren"
    ]);
    expect(productHomeCopy.dossierPreview.map((item) => item.label)).toEqual([
      "Fall",
      "Befund",
      "Lücke",
      "Entscheidung"
    ]);
    expect(productHomeCopy.outcomeChecks).toContain("Was muss QA entscheiden?");
    expect(productHomeCopy.exampleTitle).toBe("Beispiele für typische QA-Prüfungen");
  });

  it("keeps demo triage cards connected to concrete demo detail routes", () => {
    expect(demoReviewCases).toHaveLength(3);
    expect(demoReviewCases.map((demoCase) => demoCase.href)).toEqual([
      "/review-ui/demo/dev-2025-014",
      "/review-ui/demo/capa-2025-082",
      "/review-ui/demo/cc-2025-211"
    ]);
    expect(demoReviewCases.map((demoCase) => demoCase.noteLabel)).toEqual([
      "Prüfhinweis",
      "Prüfhinweis",
      "Prüfhinweis"
    ]);
    expect(demoReviewCases[0].nextStep).toContain("Quelle prüfen");
    expect(demoReviewCases[0].whyItMatters).toContain("Warum dieser Fall wichtig ist");
    expect(demoReviewCases[0].findings).toHaveLength(3);
    expect(demoReviewCases[0].missingEvidence[0]).toContain("Nachweis");
    expect(demoReviewCases[0].decisionActions).toEqual([
      "Bestätigen",
      "Weitere Unterlagen anfordern",
      "An QA eskalieren"
    ]);
  });

  it("turns backend configuration failures into user-facing review list copy", () => {
    const message = userFacingReviewLoadError(
      "Backend nicht verbunden. Prüfe QRM_BACKEND_URL und QRM_BACKEND_API_KEY."
    );

    expect(message.title).toBe("Prüffälle gerade nicht verfügbar");
    expect(message.message).toContain("Backend");
    expect(message.message).not.toContain("QRM_BACKEND_URL");
    expect(message.message).not.toContain("QRM_BACKEND_API_KEY");
  });

  it("hides the retired public demo case from the review UI", () => {
    const demoCase = {
      document_set_id: "ds_demo_avi_threshold",
      tenant_id: "tenant_demo_pharma",
      requirement_set_id: "rset_demo",
      upload_timestamp: "2026-01-01T00:00:00Z",
      document_ids: [],
      declared_document_type: "change_control",
      declared_process_area: "aseptic_filling",
      uploaded_by: "demo",
      status: "needs_human_review"
    };

    expect(isHiddenDemoDocumentSetId(demoCase.document_set_id)).toBe(true);
    expect(isVisibleReviewDocumentSet(demoCase)).toBe(false);
    expect(isVisibleReviewDocumentSet({ ...demoCase, document_set_id: "ds_real_case" })).toBe(true);
  });

  it("shows backend codes as plain German labels", () => {
    expect(displayReviewValue("needs_human_review")).toBe("Menschliche Prüfung nötig");
    expect(displayReviewValue("change_control")).toBe("Geplante Änderung");
    expect(displayReviewValue("blocked_due_to_model_failure")).toBe("Prüfung notwendig");
    expect(displayReviewReason("human review required for high/critical risk")).toContain("Mensch");
  });

  it("shows review pack summaries without backend decision jargon", () => {
    expect(
      displayReviewPackSummary({
        decision: "blocked_due_to_model_failure",
        findingCount: 4,
        maxSeverity: "high"
      })
    ).toBe("Prüfung notwendig. 4 Prüfpunkte gefunden. höchste Einstufung: Hoch.");
  });

  it("calculates human review progress for a review pack", () => {
    const pack = {
      review_progress_percent: 50,
      reviewed_finding_count: 1,
      total_finding_count: 2,
      top_risks: []
    };

    expect(reviewPackProgress(pack)).toEqual({
      percent: 50,
      reviewed: 1,
      total: 2,
      label: "50% bearbeitet (1 von 2 Prüfpunkten)"
    });
  });

  it("shows human feedback outcomes as compact German labels", () => {
    expect(displayFeedbackOutcome("confirmed_risk")).toBe("Bestätigt");
    expect(displayFeedbackOutcome("severity_overstated")).toBe("Herabgestuft");
    expect(displayFeedbackOutcome("false_positive")).toBe("Fehlalarm");
    expect(displayFeedbackOutcome("missing_information")).toBe("Mehr Infos");
    expect(displayFeedbackOutcome("evidence_issue")).toBe("Quelle falsch");
    expect(displayFeedbackOutcome("requirement_issue")).toBe("Regelwerk falsch");
    expect(displayFeedbackOutcome("missed_finding")).toBe("Fehlender Befund");
  });

  it("shows missing human feedback counters as zero", () => {
    expect(displayFeedbackCount(undefined)).toBe("0");
    expect(displayFeedbackCount(null)).toBe("0");
    expect(displayFeedbackCount(4)).toBe("4");
  });

  it("shows calibration status as reviewer-facing labels", () => {
    expect(displayCalibrationStatus("raw_feedback")).toBe("Rohfeedback");
    expect(displayCalibrationStatus("approved_gold")).toBe("Gold-Beispiel");
    expect(displayCalibrationStatus("active")).toBe("Aktiv");
  });

  it("hides internal reviewer routing failures from human review reasons", () => {
    const reasons = displayReviewReasons(
      "single high/critical finding is sufficient for human review; relevant reviewer role failed: GMPDataIntegrityReviewer; missing required reviewer role: ContradictionHunter; finding lacks requirement reference: finding 1; adversarial challenge involves possible high/critical risk; verifier did not pass all deterministic checks"
    );

    expect(reasons).toContain("Eine Gegenprüfung sieht möglicherweise ein hohes oder kritisches Risiko.");
    expect(reasons).toContain("Die automatische Quellenprüfung konnte nicht alles sicher bestätigen.");
    expect(reasons.join(" ")).not.toContain("Ein einzelner hoher oder kritischer Prüfpunkt reicht aus");
    expect(reasons.join(" ")).not.toContain("reviewer role failed");
    expect(reasons.join(" ")).not.toContain("finding lacks requirement reference");
  });

  it("shows adversarial finding statements and review prompts as concrete German copy", () => {
    expect(displayRiskStatement("Adversarial review found required evidence missing or not clearly present in the claim ledger.")).toBe(
      "Erforderliche Nachweise fehlen oder sind in den Quellen nicht klar belegt."
    );

    const checklist = buildFindingReviewChecklist({
      riskStatement: "Adversarial review found required evidence missing or not clearly present in the claim ledger.",
      requirementReferences: [],
      verifierStatus: "none",
      evidenceRows: [
        {
          document_id: "CC-SYN-005",
          page: 4,
          chunk_id: "chunk_12",
          quote: "The validation addendum is deferred pending annual supplier review."
        }
      ],
      missingInformation: ["current validation report", "approved validation addendum"]
    });

    expect(checklist).toContain("Prüfe den Befund: Erforderliche Nachweise fehlen oder sind in den Quellen nicht klar belegt.");
    expect(checklist).toContain("Fehlender Nachweis: aktueller Validierungsbericht.");
    expect(checklist).toContain("Fehlender Nachweis: genehmigter Validierungsnachtrag.");
    expect(checklist).toContain("Regelwerksbezug prüfen oder nachtragen.");
    expect(checklist.join(" ")).toContain("Belegstelle prüfen: CC-SYN-005, Seite 4.");
    expect(checklist.join(" ")).not.toContain("chunk_12");
  });

  it("shows evidence references without internal document and chunk ids", () => {
    const row = {
      document_id: "doc_978d9cfbc03c4111964a97eee05a2055",
      page: 1,
      chunk_id: "chunk_978d9cfbc03c4111964a97eee05a2055_p1",
      quote:
        '0 **Datum:** 2026-04-16 **Dokumenttyp:** Baseline Risk Assessment **Prozessbereich:** Supplier Change / Aseptische Verarbeitung **Seiten-/Abschnittsplatzhalter:** S.'
    };

    expect(evidenceSourceLabel(row)).toBe("Baseline Risk Assessment, Seite 1");
    expect(cleanEvidenceQuote(row.quote)).toBe(
      "Datum: 2026-04-16 Dokumenttyp: Baseline Risk Assessment Prozessbereich: Supplier Change / Aseptische Verarbeitung Seiten-/Abschnittsplatzhalter: S."
    );
  });

  it("keeps finding review checklists short when many global missing items exist", () => {
    const checklist = buildFindingReviewChecklist({
      riskStatement: "Adversarial review found required evidence missing or not clearly present in the claim ledger.",
      requirementReferences: [],
      verifierStatus: "none",
      evidenceRows: [],
      missingInformation: [
        "first",
        "second",
        "third",
        "fourth",
        "fifth",
        "sixth"
      ]
    });

    expect(checklist.filter((item) => item.startsWith("Fehlender Nachweis:"))).toHaveLength(4);
  });

  it("trims backend runtime environment values", () => {
    const config = getReviewBackendConfig({
      QRM_BACKEND_URL: " https://backend.example.com \n",
      QRM_BACKEND_API_KEY: " key-123\n",
      QRM_BACKEND_TENANT_ID: "tenant_demo_pharma\n",
      QRM_DEFAULT_REQUIREMENT_SET_ID: "rset_demo_gmp_qrm_2026_1\n"
    });

    expect(config).toEqual({
      backendUrl: "https://backend.example.com",
      apiKey: "key-123",
      tenantId: "tenant_demo_pharma",
      requirementSetId: "rset_demo_gmp_qrm_2026_1"
    });
  });

  it("removes literal escaped newlines from backend runtime environment values", () => {
    const config = getReviewBackendConfig({
      QRM_BACKEND_URL: "https://backend.example.com\\n",
      QRM_BACKEND_TENANT_ID: "tenant_demo_pharma\\n",
      QRM_DEFAULT_REQUIREMENT_SET_ID: "rset_demo_gmp_qrm_2026_1\\n"
    });

    expect(config.backendUrl).toBe("https://backend.example.com");
    expect(config.tenantId).toBe("tenant_demo_pharma");
    expect(config.requirementSetId).toBe("rset_demo_gmp_qrm_2026_1");
  });

  it("defines a simpler case workspace structure for consultants", () => {
    expect(caseWorkspaceStructure.route).toBe("/case-workspace");
    expect(caseWorkspaceStructure.primaryTabs.map((tab) => tab.label)).toEqual([
      "Status",
      "Quellen",
      "Deltas",
      "Review",
      "Export"
    ]);
    expect(caseWorkspaceStructure.hiddenTechnicalPages).toContain("source-snippets");
    expect(caseWorkspaceStructure.hiddenTechnicalPages).toContain("plausibility-checks");
    expect(caseWorkspaceStructure.hiddenTechnicalPages).toContain("red-team-findings");
  });

  it("documents the AI architecture as a controlled review chain, not model voting", () => {
    expect(aiArchitectureConcept.title).toBe("Wie die Prüfmappe entsteht");
    expect(aiArchitectureConcept.subtitle).toContain("Jeder Schritt bleibt nachvollziehbar");
    expect(aiArchitectureConcept.subtitle).toContain("Freigaben bleiben menschlich");
    expect(aiArchitectureConcept.subtitle).not.toContain("Multi-Agent");
    expect(aiArchitectureConcept.subtitle).not.toContain("Regelkarten");
    expect(aiArchitectureConcept.flow.map((step) => step.description).join(" ")).not.toContain("Claim Ledger");
    expect(aiArchitectureConcept.flow.map((step) => step.description).join(" ")).not.toContain("Requirement Cards");
    expect(aiArchitectureConcept.flow.map((step) => step.id)).toEqual([
      "source",
      "scope-router",
      "reviewer-agents",
      "evidence-verifier",
      "risk-fusion",
      "human-review"
    ]);
    expect(aiArchitectureConcept.nonNegotiables).toContain("Keine Mehrheitsabstimmung.");
    expect(aiArchitectureConcept.nonNegotiables).toContain("Fehlende Knowledge Packs blockieren Auto-Clear.");
    expect(aiArchitectureConcept.nonNegotiables).toContain("Firmenspezifische SOPs können geladen werden; die Agenten ziehen daraus rollenbezogen passende Regelkarten und Textstellen.");
    expect(aiArchitectureConcept.nonNegotiables).toContain("QA/SME bleibt letzter Schritt.");
    expect(aiArchitectureConcept.aiRoles.map((role) => role.role)).toContain("Evidence Verifier");
    expect(aiArchitectureConcept.aiRoles.map((role) => role.role)).toContain("7 Reviewer Agents");
  });

  it("exposes the reviewer decisions required by the workflow", () => {
    expect(decisionOptions.map((option) => option.value)).toEqual([
      "confirm",
      "downgrade",
      "reject_false_positive",
      "severity_incorrect",
      "evidence_incorrect",
      "requirement_incorrect",
      "missed_finding",
      "request_more_information",
      "escalate_to_qa"
    ]);
    expect(decisionOptions.map((option) => option.label)).toEqual([
      "Befund bestätigen",
      "Bewertung herabstufen",
      "Als Fehlalarm markieren",
      "Schweregrad korrigieren",
      "Quelle passt nicht",
      "Regelwerk passt nicht",
      "Fehlenden Befund melden",
      "Weitere Unterlagen anfordern",
      "An QA eskalieren"
    ]);
  });

  it("finds a risk inside a review pack by finding id", () => {
    const pack: ReviewPack = {
      review_pack_id: "rpack_sample",
      document_set_id: "ds_sample",
      decision: { decision: "human_review_required" },
      summary: "Human review required.",
      top_risks: [
        {
          finding_id: "finding_sample",
          risk_statement: "Potential QA approval gap.",
          severity: "high",
          risk_category: "qa_approval",
          requirement_references: ["req_sample"],
          evidence_quotes: [],
          found_by_agents: [],
          contradicted_by_agents: [],
          no_issue_agents: [],
          verifier_status: "partial",
          human_review_reason: "High severity requires review."
        }
      ],
      finding_clusters: [],
      evidence_table: [],
      model_positions: [],
      verifier_results: [],
      ood_reasons: [],
      coverage_gap_reasons: [],
      missing_information: [],
      recommended_reviewer_actions: [],
      audit_references: []
    };

    expect(findTopRiskById(pack, "finding_sample")?.risk_statement).toContain("QA");
    expect(findTopRiskById(pack, "finding_missing")).toBeUndefined();
  });

  it("normalizes reviewer decision payloads for the backend", () => {
    expect(
      normalizeReviewDecisionPayload({
        reviewerId: "qa_1",
        decision: "confirm",
        rationale: " Evidence and requirement basis reviewed. "
      })
    ).toEqual({
      reviewer_id: "reviewer_qa_1",
      decision: "confirm",
      rationale: "Evidence and requirement basis reviewed."
    });
  });

  it("documents the public Supabase env names used by the frontend helpers", () => {
    expect(supabasePublicEnvKeys).toEqual({
      url: "NEXT_PUBLIC_SUPABASE_URL",
      publishableKey: "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"
    });
    expect(
      hasSupabasePublicConfig({
        NEXT_PUBLIC_SUPABASE_URL: "https://example.supabase.co",
        NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "sb_publishable_example"
      })
    ).toBe(true);
    expect(hasSupabasePublicConfig({ NEXT_PUBLIC_SUPABASE_URL: "" })).toBe(false);
  });
});
