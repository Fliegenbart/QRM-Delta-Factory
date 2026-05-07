import { createSourceSnippet, sortReviewQueue, type RiskItemLike } from "./qrm-engine";

export const demoUsers = [
  { id: "user-admin", name: "Alex Admin", email: "admin@demo.local", role: "ADMIN" as const },
  { id: "user-author", name: "Mira QRM Author", email: "author@demo.local", role: "QRM_AUTHOR" as const },
  { id: "user-sme", name: "Dr. Sam SME", email: "sme@demo.local", role: "SME_REVIEWER" as const },
  { id: "user-qa", name: "Quinn QA Approver", email: "qa@demo.local", role: "QA_APPROVER" as const },
  { id: "user-auditor", name: "Riley Inspector", email: "audit@demo.local", role: "AUDITOR" as const }
];

export const demoProject = {
  id: "project-avi-threshold",
  name: "AVI rejection threshold delta QRM",
  productProcessSystem: "Sterile injectable drug product: aseptic filling and automated visual inspection",
  gmpArea: "sterile manufacturing",
  scopeStatement:
    "Assess quality-risk impact of a modified automated visual inspection rejection threshold for filled sterile injectable containers.",
  outOfScopeStatement: "Manual visual inspection program, formulation process, and upstream aseptic filling parameters are outside this delta.",
  triggerType: "change control",
  methodology: "FMEA",
  scoringModel: "Severity, Occurrence, Detectability, RPN with risk-based review levels",
  requiredSmeReviewers: ["Visual inspection SME", "Validation SME", "Data integrity SME"],
  requiredQaApprover: "Sterile manufacturing QA Approver"
};

export const demoDocuments = [
  {
    id: "doc-process",
    documentType: "process description",
    fileName: "SYNTH_Process_Description_AVI.md",
    content:
      "Automated visual inspection evaluates filled containers for visible particles, fill level, and container closure defects before batch disposition."
  },
  {
    id: "doc-sop",
    documentType: "SOP",
    fileName: "SYNTH_SOP_AVI_Operation.md",
    content:
      "Operators verify active AVI recipe and rejection threshold before batch start. Training completion is required before independent operation."
  },
  {
    id: "doc-fmea",
    documentType: "existing FMEA / risk assessment",
    fileName: "SYNTH_Existing_FMEA_AVI.csv",
    content:
      "False accept of defective container; controls include recipe verification, challenge set, audit trail review, and batch reconciliation."
  },
  {
    id: "doc-change",
    documentType: "change-control record",
    fileName: "SYNTH_CC_042_AVI_Threshold.md",
    content:
      "Change control proposes a modified rejection threshold to reduce false rejects while maintaining detection capability. Validation addendum is planned."
  },
  {
    id: "doc-deviation",
    documentType: "deviation record",
    fileName: "SYNTH_DEV_118_Reconciliation.md",
    content:
      "Deviation notes unclear batch record reconciliation wording for AVI reject counts during threshold confirmation batch."
  },
  {
    id: "doc-validation",
    documentType: "validation protocol/report",
    fileName: "SYNTH_VAL_AVI_2025.md",
    content:
      "Validation report covers the previous rejection threshold. New threshold performance evidence is not yet attached to this package."
  },
  {
    id: "doc-batch",
    documentType: "batch-record excerpt",
    fileName: "SYNTH_BR_23001_AVI.md",
    content: "Batch record records accepted, rejected, and manually inspected unit counts. Reconciliation acceptance wording requires clarification."
  }
];

export const demoSnippets = [
  createSourceSnippet({
    id: "snip-process-1",
    documentId: "doc-process",
    documentType: "process description",
    sectionTitle: "AVI purpose",
    lineReference: "lines 1-3",
    text: demoDocuments[0].content
  }),
  createSourceSnippet({
    id: "snip-sop-1",
    documentId: "doc-sop",
    documentType: "SOP",
    sectionTitle: "Recipe and threshold verification",
    lineReference: "lines 8-12",
    text: demoDocuments[1].content
  }),
  createSourceSnippet({
    id: "snip-fmea-1",
    documentId: "doc-fmea",
    documentType: "existing FMEA / risk assessment",
    sectionTitle: "Baseline risk controls",
    lineReference: "row 4",
    text: demoDocuments[2].content
  }),
  createSourceSnippet({
    id: "snip-change-1",
    documentId: "doc-change",
    documentType: "change-control record",
    sectionTitle: "Proposed threshold change",
    lineReference: "section 2.1",
    text: demoDocuments[3].content
  }),
  createSourceSnippet({
    id: "snip-dev-1",
    documentId: "doc-deviation",
    documentType: "deviation record",
    sectionTitle: "Reconciliation wording",
    lineReference: "summary",
    text: demoDocuments[4].content
  }),
  createSourceSnippet({
    id: "snip-val-1",
    documentId: "doc-validation",
    documentType: "validation protocol/report",
    sectionTitle: "Validation coverage limitation",
    lineReference: "conclusion",
    text: demoDocuments[5].content
  }),
  createSourceSnippet({
    id: "snip-batch-1",
    documentId: "doc-batch",
    documentType: "batch-record excerpt",
    sectionTitle: "AVI reconciliation fields",
    lineReference: "page placeholder 14",
    text: demoDocuments[6].content
  })
];

export const demoRiskLibrary = [
  {
    id: "lib-false-accept",
    libraryId: "AVI-LIB-001",
    gmpArea: "sterile manufacturing",
    processStep: "Automated visual inspection",
    failureMode: "False accept of defective container",
    typicalCauses: "Threshold not challenged, recipe mismatch, inadequate defect set coverage",
    patientSafetyEffect: "Potential administration of container with visible defect",
    productQualityEffect: "Defective unit remains in accepted batch population",
    dataIntegrityEffect: "Incorrect threshold metadata may obscure batch decision basis",
    gmpComplianceEffect: "Batch disposition may rely on incomplete verification evidence",
    commonExistingControls: "Recipe verification, qualified defect standards, audit trail review",
    typicalAdditionalControls: "Threshold challenge set, independent review, validation addendum",
    typicalEvidence: "Validation report, challenge-set execution record, audit trail review record",
    defaultScoringGuidance: "Severity 4-5, occurrence 1-3, detectability 2-4 depending on controls",
    requiredSmeDiscipline: "Visual inspection / validation SME",
    approvalStatus: "APPROVED",
    approvedBy: "Synthetic QA Council",
    approvedDate: "2026-01-15",
    version: 2,
    retired: false
  },
  {
    id: "lib-data-integrity",
    libraryId: "AVI-LIB-002",
    gmpArea: "data integrity",
    processStep: "AVI result handling",
    failureMode: "Audit trail review does not detect threshold or recipe changes",
    typicalCauses: "Review scope unclear, user access not periodically checked",
    patientSafetyEffect: "Indirect risk through unreliable inspection decision record",
    productQualityEffect: "Batch decision record may be incomplete",
    dataIntegrityEffect: "Attributable, legible, contemporaneous, original, accurate record expectations may not be met",
    gmpComplianceEffect: "Audit trail controls may be insufficient for GMP record review",
    commonExistingControls: "Role-based access, audit trail, batch review checklist",
    typicalAdditionalControls: "Focused threshold-change audit trail review step",
    typicalEvidence: "Audit trail review record and user access review",
    defaultScoringGuidance: "Severity 3-4, occurrence 2-3, detectability 2-4",
    requiredSmeDiscipline: "Data integrity SME",
    approvalStatus: "APPROVED",
    approvedBy: "Synthetic QA Council",
    approvedDate: "2026-01-15",
    version: 1,
    retired: false
  },
  {
    id: "lib-unapproved",
    libraryId: "AVI-LIB-DRAFT-003",
    gmpArea: "packaging",
    processStep: "Label inspection",
    failureMode: "Draft label mix-up risk",
    typicalCauses: "Synthetic draft item",
    patientSafetyEffect: "Requires SME assessment",
    productQualityEffect: "Requires SME assessment",
    dataIntegrityEffect: "Requires SME assessment",
    gmpComplianceEffect: "Requires SME assessment",
    commonExistingControls: "Draft only",
    typicalAdditionalControls: "Draft only",
    typicalEvidence: "Draft only",
    defaultScoringGuidance: "Draft only",
    requiredSmeDiscipline: "Packaging SME",
    approvalStatus: "DRAFT",
    approvedBy: null,
    approvedDate: null,
    version: 1,
    retired: false
  }
];

export const demoRiskItems: RiskItemLike[] = [
  {
    id: "risk-001",
    projectId: demoProject.id,
    processStep: "Automated visual inspection",
    gmpArea: "sterile manufacturing",
    failureMode: "False accept of defective container",
    potentialCause: "Modified rejection threshold is not supported by new-threshold performance evidence",
    potentialEffect: "Defective container could remain in accepted batch population",
    impactCategories: ["PATIENT_SAFETY", "PRODUCT_QUALITY", "GMP_COMPLIANCE"],
    existingControls: ["Recipe verification", "Qualified defect challenge set", "Batch review"],
    sourceLinks: ["snip-change-1", "snip-val-1", "snip-fmea-1"],
    libraryItemId: "lib-false-accept",
    libraryApprovalStatus: "APPROVED",
    severity: 5,
    occurrence: 2,
    detectability: 3,
    humanSeverity: 5,
    humanOccurrence: 2,
    humanDetectability: 3,
    residualRiskRationale: "DRAFT rationale: hold for SME confirmation until new-threshold effectiveness evidence is attached.",
    proposedControls: ["Execute new-threshold challenge set before use in routine batch disposition"],
    requiredEvidence: ["Validation addendum covering modified threshold", "Challenge-set execution record"],
    evidenceStatus: "MISSING",
    confidence: "MEDIUM",
    priority: "CRITICAL",
    deterministicGateResult: "BLOCKED_MISSING_EVIDENCE",
    plausibilityResult: "PARTIAL",
    redTeamResult: "MISSING_RISK_WITH_SOURCE",
    reviewLevel: 3,
    reviewStatus: "SME_REVIEW_REQUIRED",
    status: "AI_DRAFT",
    version: 1
  },
  {
    id: "risk-002",
    projectId: demoProject.id,
    processStep: "Automated visual inspection",
    gmpArea: "sterile manufacturing",
    failureMode: "False reject and batch yield impact",
    potentialCause: "Threshold setting rejects acceptable containers at higher rate",
    potentialEffect: "Yield loss may threaten supply continuity and trigger extra handling",
    impactCategories: ["SUPPLY_CONTINUITY", "PROCESS_CONTROL", "PRODUCT_QUALITY"],
    existingControls: ["Reject trend monitoring", "Batch record reconciliation"],
    sourceLinks: ["snip-change-1", "snip-batch-1"],
    libraryItemId: "lib-false-accept",
    libraryApprovalStatus: "APPROVED",
    severity: 3,
    occurrence: 3,
    detectability: 2,
    humanSeverity: 3,
    humanOccurrence: 3,
    humanDetectability: 2,
    residualRiskRationale: "DRAFT rationale: SME to confirm acceptable reject trend limits.",
    proposedControls: ["Define temporary enhanced reject-trend review"],
    requiredEvidence: ["Batch reconciliation record", "Trend review evidence"],
    evidenceStatus: "PARTIAL",
    confidence: "HIGH",
    priority: "HIGH",
    deterministicGateResult: "PASS_WITH_SME_REVIEW",
    plausibilityResult: "PASS",
    redTeamResult: "NO_ADDITIONAL_RISK_IDENTIFIED",
    reviewLevel: 2,
    reviewStatus: "SME_REVIEW_REQUIRED",
    status: "AI_DRAFT",
    version: 1
  },
  {
    id: "risk-003",
    projectId: demoProject.id,
    processStep: "AVI result handling",
    gmpArea: "data integrity",
    failureMode: "Audit trail review misses threshold configuration change",
    potentialCause: "Audit trail review checklist does not explicitly include threshold field",
    potentialEffect: "Batch decision may rely on insufficiently reviewed electronic record",
    impactCategories: ["DATA_INTEGRITY", "GMP_COMPLIANCE", "PRODUCT_QUALITY"],
    existingControls: ["Role-based access", "Audit trail review"],
    sourceLinks: ["snip-sop-1", "snip-change-1"],
    libraryItemId: "lib-data-integrity",
    libraryApprovalStatus: "APPROVED",
    severity: 4,
    occurrence: 2,
    detectability: 3,
    humanSeverity: 4,
    humanOccurrence: 2,
    humanDetectability: 3,
    residualRiskRationale: "DRAFT rationale: needs data integrity SME confirmation of review checklist scope.",
    proposedControls: ["Add threshold field to audit trail review checklist for impacted batches"],
    requiredEvidence: ["Audit trail review record", "Access review"],
    evidenceStatus: "WEAK",
    confidence: "MEDIUM",
    priority: "HIGH",
    deterministicGateResult: "PASS_WITH_SME_REVIEW",
    plausibilityResult: "PARTIAL",
    redTeamResult: "UNSUPPORTED_HYPOTHESIS_REVIEW_REQUIRED",
    reviewLevel: 3,
    reviewStatus: "SME_REVIEW_REQUIRED",
    status: "AI_DRAFT",
    version: 1
  },
  {
    id: "risk-004",
    projectId: demoProject.id,
    processStep: "Training and procedure rollout",
    gmpArea: "sterile manufacturing",
    failureMode: "Operator uses updated SOP without documented training record",
    potentialCause: "SOP update occurred but training evidence is missing from package",
    potentialEffect: "Operator may apply threshold verification step inconsistently",
    impactCategories: ["GMP_COMPLIANCE", "PROCESS_CONTROL"],
    existingControls: ["SOP revision", "Training matrix"],
    sourceLinks: ["snip-sop-1"],
    libraryItemId: undefined,
    libraryApprovalStatus: undefined,
    severity: 3,
    occurrence: 2,
    detectability: 3,
    humanSeverity: 3,
    humanOccurrence: 2,
    humanDetectability: 3,
    residualRiskRationale: "DRAFT rationale: training record gap requires owner response.",
    proposedControls: ["Attach training completion record before routine use"],
    requiredEvidence: ["Training record"],
    evidenceStatus: "MISSING",
    confidence: "LOW",
    priority: "HIGH",
    deterministicGateResult: "BLOCKED_NEW_OR_UNVERIFIED",
    plausibilityResult: "UNCLEAR",
    redTeamResult: "UNSUPPORTED_HYPOTHESIS_REVIEW_REQUIRED",
    reviewLevel: 3,
    reviewStatus: "SME_REVIEW_REQUIRED",
    status: "AI_DRAFT",
    version: 1
  }
];

export const demoGaps = [
  {
    id: "gap-001",
    riskItemId: "risk-001",
    priority: "CRITICAL" as const,
    status: "OPEN" as const,
    description: "Missing effectiveness evidence for the modified AVI rejection threshold.",
    question: "Which validation addendum or challenge-set execution record supports the new threshold?"
  },
  {
    id: "gap-002",
    riskItemId: "risk-004",
    priority: "HIGH" as const,
    status: "OPEN" as const,
    description: "SOP update is referenced, but operator training record is missing.",
    question: "Has training been completed for operators who execute threshold verification?"
  },
  {
    id: "gap-003",
    riskItemId: "risk-002",
    priority: "HIGH" as const,
    status: "OPEN" as const,
    description: "Batch record reconciliation acceptance wording is unclear.",
    question: "What exact reconciliation criterion applies to AVI reject counts?"
  }
];

export const demoPlausibilityChecks = [
  {
    id: "pc-001",
    riskItemId: "risk-001",
    result: "PARTIAL",
    requiredHumanReviewerType: "Validation SME",
    comments: "Source supports that old threshold evidence exists and new-threshold evidence is absent. Control proposal is logical but requires actual evidence.",
    issues: ["Validation report covers old threshold only", "Residual rationale remains a DRAFT placeholder"]
  },
  {
    id: "pc-002",
    riskItemId: "risk-003",
    result: "PARTIAL",
    requiredHumanReviewerType: "Data integrity SME",
    comments: "Audit trail risk is plausible, but source does not prove checklist gap. Treat as expert question.",
    issues: ["Unsupported inference requires SME confirmation"]
  }
];

export const demoRedTeamFindings = [
  {
    id: "rt-001",
    category: "MISSING_RISK_WITH_SOURCE",
    priority: "HIGH",
    description: "Batch record reconciliation risk may be under-specified because the deviation record says wording is unclear.",
    sourceBasis: "snip-dev-1",
    status: "OPEN"
  },
  {
    id: "rt-002",
    category: "UNSUPPORTED_HYPOTHESIS_REVIEW_REQUIRED",
    priority: "MEDIUM",
    description: "Alarm handling impact could exist if threshold alarm settings changed, but no source confirms an alarm change.",
    sourceBasis: "unsupported hypothesis — expert review required",
    status: "OPEN"
  }
];

export const demoAuditLogs = [
  {
    id: "audit-001",
    timestamp: "2026-05-07T08:00:00.000Z",
    userName: "Mira QRM Author",
    action: "PROJECT_CREATED",
    entityType: "Project",
    entityId: demoProject.id,
    reason: "Synthetic demo scenario seeded",
    eventPayloadHash: "demo-hash-001",
    previousEventHash: "GENESIS"
  },
  {
    id: "audit-002",
    timestamp: "2026-05-07T08:02:00.000Z",
    userName: "Mira QRM Author",
    action: "AI_GENERATION_RUN",
    entityType: "Project",
    entityId: demoProject.id,
    reason: "Mock Author AI created DRAFT delta suggestions",
    eventPayloadHash: "demo-hash-002",
    previousEventHash: "demo-hash-001"
  },
  {
    id: "audit-003",
    timestamp: "2026-05-07T08:04:00.000Z",
    userName: "System",
    action: "CRITIC_AI_CHECK_RUN",
    entityType: "Project",
    entityId: demoProject.id,
    reason: "Mock Critic AI checked support and plausibility",
    eventPayloadHash: "demo-hash-003",
    previousEventHash: "demo-hash-002"
  }
];

export const reviewQueue = sortReviewQueue(demoRiskItems);
