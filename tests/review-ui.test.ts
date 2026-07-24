import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { NextRequest } from "next/server";
import {
  caseWorkspaceStructure,
  aiArchitectureConcept,
  consultantReviewCopy,
  demoReviewCases,
  buildFindingReviewChecklist,
  cleanEvidenceQuote,
  decisionOptions,
  demoDecisionStorageKey,
  displayReviewReason,
  displayReviewReasons,
  displayReviewPackSummary,
  reviewPackRiskPresentation,
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
import {
  isProtectedReviewPath,
  isReviewAuthRequired
} from "@/utils/supabase/review-auth";
import { updateSession } from "@/utils/supabase/middleware";

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

  it("states the start screen as a guided work surface", () => {
    expect(productHomeCopy.title).toBe("Unterlagen hochladen. Prüfmappe zurückbekommen.");
    expect(productHomeCopy.subtitle).toContain("Change, CAPA oder Abweichung rein");
    expect(productHomeCopy.subtitle).toContain("Prüfpunkte");
    expect(productHomeCopy.primaryAction).toBe("Prüffall vorbereiten");
    expect(productHomeCopy.workflow).toEqual([
      "Unterlagen hochladen",
      "Prüfpunkte und Quellen sehen",
      "Lücken klären",
      "Entscheidung dokumentieren"
    ]);
    expect(productHomeCopy.dossierPreview.map((item) => item.label)).toEqual([
      "Der Fall",
      "Der Befund",
      "Die Lücke",
      "Ihre Entscheidung"
    ]);
    expect(productHomeCopy.dossierPreview[3].value).toContain("bestätigen");
    expect(productHomeCopy.exampleTitle).toBe("Drei Beispiele: So sieht eine fertige Prüfmappe aus.");
    expect(productHomeCopy.exampleDescription).toContain("Klicken Sie sich durch");
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
    expect(demoReviewCases[0].criticNote).toContain("Für die Aussage");
    expect(demoReviewCases[0].nextStep).toContain("Passt die zitierte Stelle wirklich");
    expect(demoReviewCases[1].criticNote).toContain("Zu entscheiden");
    expect(demoReviewCases[1].nextStep).toContain("muss die Wirksamkeit vor Freigabe belegt sein");
    expect(demoReviewCases[2].criticNote).toContain("wartet auf Freigabe");
    expect(demoReviewCases[0].whyItMatters).toContain("Warum dieser Fall wichtig ist");
    expect(demoReviewCases[0].findings).toHaveLength(3);
    expect(demoReviewCases[0].missingEvidence[0]).toContain("Nachweis");
    expect(demoReviewCases[0].decisionActions).toEqual([
      "Bestätigen",
      "Weitere Unterlagen anfordern",
      "An QA eskalieren"
    ]);
  });

  it("uses a versioned, case-specific browser key for demo decisions", () => {
    expect(demoDecisionStorageKey("DEV-2025-014")).toBe(
      "pharmaqrm:demo-decision:v1:DEV-2025-014"
    );
  });

  it("uses reviewer-friendly upload guidance on the start form", () => {
    const appShell = readFileSync(join(process.cwd(), "src/components/app-shell.tsx"), "utf8");
    const intakeUploader = readFileSync(
      join(process.cwd(), "src/components/review-ui/intake-uploader.tsx"),
      "utf8"
    );

    expect(appShell).toContain("Change, CAPA, Abweichung oder Audit-Finding hochladen.");
    expect(appShell).toContain("Mehrere Dokumente sind möglich");
    expect(intakeUploader).toContain("Was ist der Auslöser?");
    expect(intakeUploader).toContain("Wo passiert es?");
    expect(intakeUploader).toContain("optional, fürs Protokoll");
    expect(intakeUploader).toContain("Audit-Finding");
    expect(intakeUploader).toContain("QC-Labor");
    expect(intakeUploader).toContain("Lieferant/Material");
  });

  it("explains which rule sources belong in the rule library import", () => {
    const requirementLibrary = readFileSync(
      join(process.cwd(), "src/components/review-ui/requirement-library-manager.tsx"),
      "utf8"
    );

    expect(requirementLibrary).toContain("Welche Regelwerke gehören hier rein?");
    expect(requirementLibrary).toContain("Unternehmens-SOPs");
    expect(requirementLibrary).toContain("EU GMP Annex 1");
    expect(requirementLibrary).toContain("Annex 11");
    expect(requirementLibrary).toContain("21 CFR Part 11");
    expect(requirementLibrary).toContain("Change-Control-, Abweichungs- und CAPA-Vorgaben");
    expect(requirementLibrary).toContain("Nicht hochladen:");
    expect(requirementLibrary).toContain("Original-PDFs oder Word-SOPs");
    expect(requirementLibrary).toContain("strukturierte JSON- oder YAML-Datei");
  });

  it("turns backend configuration failures into user-facing review list copy", () => {
    const message = userFacingReviewLoadError(
      "Backend nicht verbunden. Prüfe QRM_BACKEND_URL und QRM_BACKEND_API_KEY."
    );

    expect(message.title).toBe("Prüfdienst gerade nicht erreichbar");
    expect(message.message).toContain("Prüfdienst");
    expect(message.message).not.toContain("QRM_BACKEND_URL");
    expect(message.message).not.toContain("QRM_BACKEND_API_KEY");
  });

  it("does not convert a missing backend route into an empty case list", () => {
    const reviewListPage = readFileSync(join(process.cwd(), "app/review-ui/page.tsx"), "utf8");

    expect(reviewListPage).not.toContain("caught instanceof ReviewApiError && caught.status === 404");
    expect(reviewListPage).toContain("loadState = userFacingReviewLoadError(error)");
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
    expect(displayReviewValue("ready_for_orchestration")).toBe("Bereit zur Analyse");
    expect(displayReviewValue("change_control_package")).toBe("Change-Control-Paket");
    expect(displayReviewValue("change_control")).toBe("Geplante Änderung");
    expect(displayReviewValue("blocked_due_to_model_failure")).toBe("Prüfung notwendig");
    expect(displayReviewReason("human review required for high/critical risk")).toContain("Mensch");
    expect(displayReviewReason("unusually few claims")).toContain("wenige prüfbare Aussagen");
    expect(
      displayReviewReason("requirement_id is not applicable to document/process area: req_demo")
    ).toContain("Regelwerksbezug passt nicht");
    expect(
      displayRiskStatement("Deviation impact needs human review against documented requirements.")
    ).toContain("Abweichung");
    expect(
      displayRiskStatement("CAPA reference requires effectiveness evidence if linked to quality risk.")
    ).toContain("Wirksamkeitsnachweis");
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

  it("presents a human decision summary with root risks and supporting finding count", () => {
    const presentation = reviewPackRiskPresentation({
      decision: {
        decision: "needs_human_review"
      },
      decision_summary: "QA muss die Chargenauswirkung vor der Freigabe bewerten.",
      top_risks: [
        {
          finding_id: "root-risk",
          risk_statement: "Die Chargenbewertung ist nicht belegt.",
          severity: "high",
          requirement_references: [],
          evidence_quotes: [],
          found_by_agents: [],
          contradicted_by_agents: [],
          no_issue_agents: [],
          verifier_status: "verified",
          human_review_reason: "Charge prüfen",
          supporting_finding_ids: ["support-1", "support-2"],
          supporting_finding_count: 2
        },
        {
          finding_id: "support-1",
          risk_statement: "Ein einzelnes Teilsignal stützt die Chargenprüfung.",
          severity: "medium",
          requirement_references: [],
          evidence_quotes: [],
          found_by_agents: [],
          contradicted_by_agents: [],
          no_issue_agents: [],
          verifier_status: "verified",
          human_review_reason: ""
        }
      ],
      raw_finding_count: 3
    });

    expect(presentation.summary).toBe("QA muss die Chargenauswirkung vor der Freigabe bewerten.");
    expect(presentation.rootRisks.map((risk) => risk.finding_id)).toEqual(["root-risk"]);
    expect(presentation.supportingFindingCount).toBe(2);
  });

  it("keeps technical coverage blockers separate from the QA outcome", () => {
    const presentation = reviewPackRiskPresentation({
      decision: {
        decision: "needs_human_review",
        operational_blockers: ["model coverage incomplete"],
        model_coverage_status: "partial"
      },
      decision_summary: "",
      top_risks: [],
      operational_warnings: ["Ein Prüfschritt konnte technisch nicht vollständig abgedeckt werden."],
      raw_finding_count: 0
    });

    expect(presentation.summary).toBe("Menschliche Prüfung nötig.");
    expect(presentation.operationalWarnings).toEqual([
      "Ein Prüfschritt konnte technisch nicht vollständig abgedeckt werden.",
      "model coverage incomplete"
    ]);
    expect(presentation.modelCoverageStatus).toBe("Teilweise belegt");
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

  it("does not present an empty review pack as fully reviewed", () => {
    expect(
      reviewPackProgress({
        review_progress_percent: 100,
        reviewed_finding_count: 0,
        total_finding_count: 0,
        top_risks: []
      })
    ).toEqual({
      percent: 0,
      reviewed: 0,
      total: 0,
      label: "Keine Prüfpunkte zur Bearbeitung"
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

    expect(checklist).toContain("Prüfen Sie den Befund: Erforderliche Nachweise fehlen oder sind in den Quellen nicht klar belegt.");
    expect(checklist).toContain("Fehlender Nachweis: aktueller Validierungsbericht.");
    expect(checklist).toContain("Fehlender Nachweis: genehmigter Validierungsnachtrag.");
    expect(checklist).toContain("Regelwerksbezug prüfen oder nachtragen.");
    expect(checklist.join(" ")).toContain("Belegstelle prüfen: CC-SYN-005, Seite 4.");
    expect(checklist.join(" ")).not.toContain("chunk_12");
  });

  it("uses only trusted document metadata for evidence source labels", () => {
    const row = {
      document_id: "doc_978d9cfbc03c4111964a97eee05a2055",
      page: 1,
      chunk_id: "chunk_978d9cfbc03c4111964a97eee05a2055_p1",
      quote:
        '0 **Datum:** 2026-04-16 **Dokumenttyp:** Gefälschte Quelle.pdf **Prozessbereich:** Supplier Change / Aseptische Verarbeitung **Seiten-/Abschnittsplatzhalter:** S.'
    };

    expect(
      evidenceSourceLabel({
        ...row,
        document_name: "Change Control Ä-17.pdf"
      })
    ).toBe("Change Control Ä-17.pdf, Seite 1");
    expect(evidenceSourceLabel(row)).toBe("Hochgeladene Unterlage, Seite 1");
    expect(evidenceSourceLabel({ ...row, document_id: "CC-SYN-005" })).toBe(
      "CC-SYN-005, Seite 1"
    );
    expect(evidenceSourceLabel(row)).not.toContain("Gefälschte Quelle.pdf");
    expect(cleanEvidenceQuote(row.quote)).toBe(
      "Datum: 2026-04-16 Dokumenttyp: Gefälschte Quelle.pdf Prozessbereich: Supplier Change / Aseptische Verarbeitung Seiten-/Abschnittsplatzhalter: S."
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
    const appShell = readFileSync(join(process.cwd(), "src/components/app-shell.tsx"), "utf8");

    expect(aiArchitectureConcept.title).toBe("Der Weg eines Befunds — und sechs Stellen, an denen geprüft wird.");
    expect(aiArchitectureConcept.subtitle).toContain("wie aus einem hochgeladenen Dokument ein belegter Befund wird");
    expect(aiArchitectureConcept.subtitle).toContain("der letzte Schritt gehört immer einem Menschen");
    expect(aiArchitectureConcept.subtitle).not.toContain("Multi-Agent");
    expect(aiArchitectureConcept.subtitle).not.toContain("Regelkarten");
    expect(aiArchitectureConcept.flow).toHaveLength(6);
    expect(aiArchitectureConcept.flow.map((step) => step.title)).toEqual([
      "Aussagen herauslesen",
      "Den Fall einordnen",
      "Fachlich prüfen",
      "Quellen abgleichen",
      "Risiken bündeln",
      "Entscheidung dokumentieren"
    ]);
    expect(aiArchitectureConcept.flow.every((step) => step.safeguard.startsWith("Sicherung:"))).toBe(true);
    expect(aiArchitectureConcept.flow.map((step) => step.description).join(" ")).toContain("Diese Prüfung macht fester Programmcode, keine KI");
    expect(aiArchitectureConcept.flow.map((step) => step.description).join(" ")).not.toContain("Claim Ledger");
    expect(aiArchitectureConcept.flow.map((step) => step.description).join(" ")).not.toContain("Evidence Verifier");
    expect(aiArchitectureConcept.flow.map((step) => step.description).join(" ")).not.toContain("Risk Fusion");
    expect(aiArchitectureConcept.nonNegotiables).toContain("Keine Mehrheitsabstimmung.");
    expect(aiArchitectureConcept.nonNegotiables).toContain("Fehlt ein nötiges Regelpaket, blockiert das die Freigabe.");
    expect(aiArchitectureConcept.nonNegotiables).toContain("Eigene SOPs lassen sich laden; die Prüfer ziehen daraus die passenden Regeln.");
    expect(aiArchitectureConcept.nonNegotiables).not.toContain("Fehlende Knowledge Packs blockieren Auto-Clear.");
    expect("aiRoles" in aiArchitectureConcept).toBe(false);
    expect(appShell).not.toContain("Human Feedback Registry");
    expect(appShell).not.toContain("<HumanFeedbackRegistryPanel");
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

  it("requires server-side auth for review workspace pages and API routes", () => {
    const appShell = readFileSync(join(process.cwd(), "src/components/app-shell.tsx"), "utf8");

    expect(appShell).toContain('["prueffaelle", "nav.backendReview", ShieldCheck]');
    expect(appShell).not.toContain('["review-ui", "nav.backendReview", ShieldCheck]');
    expect(isProtectedReviewPath("/review-ui")).toBe(true);
    expect(isProtectedReviewPath("/review-ui/document-sets/ds_demo")).toBe(true);
    expect(isProtectedReviewPath("/review-ui/demo/dev-2025-014")).toBe(false);
    expect(isProtectedReviewPath("/prueffaelle")).toBe(false);
    expect(isProtectedReviewPath("/api/review-ui/document-sets")).toBe(true);
    expect(isProtectedReviewPath("/api/review-ui/document-sets/ds_demo/pipeline-runs")).toBe(true);

    expect(isProtectedReviewPath("/ringversuch")).toBe(false);
    expect(isProtectedReviewPath("/api/ringversuch")).toBe(false);
    expect(isProtectedReviewPath("/review-uiish")).toBe(false);
  });

  it("requires review auth in production unconditionally, opt-in elsewhere", () => {
    expect(isReviewAuthRequired({ NODE_ENV: "production" })).toBe(true);
    expect(isReviewAuthRequired({ VERCEL: "1" })).toBe(true);
    expect(isReviewAuthRequired({ NODE_ENV: "test" })).toBe(false);
    expect(isReviewAuthRequired({ QRM_REVIEW_UI_AUTH_REQUIRED: "true" })).toBe(true);
    // Fail secure: a leftover "false" (e.g. from .env.example) must not
    // disable auth on a production deployment.
    expect(
      isReviewAuthRequired({
        NODE_ENV: "production",
        QRM_REVIEW_UI_AUTH_REQUIRED: "false"
      })
    ).toBe(true);
  });

  it("fails closed for protected review API routes when auth is required but not configured", async () => {
    const previous = {
      authRequired: process.env.QRM_REVIEW_UI_AUTH_REQUIRED,
      supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL,
      supabaseKey: process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
    };
    process.env.QRM_REVIEW_UI_AUTH_REQUIRED = "true";
    delete process.env.NEXT_PUBLIC_SUPABASE_URL;
    delete process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

    try {
      const response = await updateSession(
        new NextRequest("https://qrm.example.test/api/review-ui/document-sets")
      );

      expect(response.status).toBe(503);
      expect(response.headers.get("cache-control")).toBe("no-store");
      await expect(response.json()).resolves.toEqual({
        error: "Review authentication is not configured."
      });
    } finally {
      restoreEnv("QRM_REVIEW_UI_AUTH_REQUIRED", previous.authRequired);
      restoreEnv("NEXT_PUBLIC_SUPABASE_URL", previous.supabaseUrl);
      restoreEnv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", previous.supabaseKey);
    }
  });
});

function restoreEnv(key: string, value: string | undefined) {
  if (value === undefined) {
    delete process.env[key];
    return;
  }
  process.env[key] = value;
}
