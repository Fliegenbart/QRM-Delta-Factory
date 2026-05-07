import {
  demoGaps,
  demoProject,
  demoRiskLibrary,
  demoSnippets
} from "./demo-data";

export interface TriggerRecord {
  id: string;
  trigger_type: "change control" | "deviation" | "CAPA" | "audit finding" | "periodic review";
  title: string;
  summary: string;
  source_snippet_ids: string[];
}

export interface ScoringModel {
  id: string;
  name: string;
  dimensions: ["Severity", "Occurrence", "Detectability"];
  risk_formula: "S*O*D";
  scale: "1-5";
}

export interface RiskItemDraft {
  risk_id: string;
  process_step: string;
  gmp_area: string;
  failure_mode: string;
  potential_cause: string;
  potential_effect: string;
  impact_categories: string[];
  existing_controls: string[];
  proposed_additional_controls: string[];
  severity_suggestion: number;
  occurrence_suggestion: number;
  detectability_suggestion: number;
  initial_rpn_suggestion: number;
  residual_risk_rationale: string;
  status: "AI_DRAFT";
}

export interface EvidenceLink {
  id: string;
  source_snippet_id: string;
  evidence_type:
    | "CONTROL_DESCRIPTION"
    | "EXECUTION_RECORD"
    | "VERIFICATION_TEST"
    | "VALIDATION_REPORT"
    | "EFFECTIVENESS_CHECK"
    | "TRAINING_RECORD"
    | "CHANGE_CONTROL"
    | "DEVIATION_CAPA"
    | "AUDIT_FINDING"
    | "BATCH_RECORD"
    | "SOP_ONLY"
    | "UNKNOWN";
  claim_supported: string;
  quality_status: "STRONG" | "SUFFICIENT_FOR_DRAFT" | "PARTIAL" | "WEAK" | "MISSING" | "CONTRADICTORY" | "EXPERT_REVIEW_REQUIRED";
}

export interface BaselineRiskItem {
  id: string;
  risk_code: string;
  process_step: string;
  failure_mode: string;
  existing_controls: string[];
  approved_version: number;
}

export type SourceSnippet = (typeof demoSnippets)[number];
export type RiskLibraryItem = (typeof demoRiskLibrary)[number];
export type Gap = (typeof demoGaps)[number];

export interface ReviewPackage {
  id: string;
  project_id: string;
  risk_item_draft: RiskItemDraft;
  trigger_record: TriggerRecord;
  linked_source_snippets: SourceSnippet[];
  scoring_model: ScoringModel;
  evidence_links: EvidenceLink[];
  documented_gaps: Gap[];
  risk_library_reference: RiskLibraryItem | "NO_APPROVED_LIBRARY_MATCH";
  baseline_risk_item: BaselineRiskItem | "NOT_A_DELTA_UPDATE";
  package_status: "DRAFT_PACKAGE" | "INPUT_INCOMPLETE" | "READY_FOR_PLAUSIBILITY_CHECK" | "PLAUSIBILITY_CHECKED";
  created_by: "AUTHOR_AI" | "HUMAN_AUTHOR";
  created_at: string;
  missing_inputs: string[];
}

export interface PackageReviewResult {
  input_status: "COMPLETE" | "INPUT_INCOMPLETE";
  missing_inputs: string[];
  overall_result: "PASS" | "PARTIAL" | "FAIL" | "UNCLEAR" | "NOT_RUN";
  source_support: "PASS" | "PARTIAL" | "FAIL" | "UNCLEAR" | "NOT_RUN";
  risk_logic: "PASS" | "PARTIAL" | "FAIL" | "UNCLEAR" | "NOT_RUN";
  control_logic: "PASS" | "PARTIAL" | "FAIL" | "UNCLEAR" | "NOT_RUN";
  evidence_quality:
    | "SUFFICIENT_FOR_DRAFT"
    | "PARTIAL"
    | "WEAK"
    | "MISSING"
    | "CONTRADICTORY"
    | "EXPERT_REVIEW_REQUIRED"
    | "NOT_RUN";
  scoring_plausibility: "PASS" | "PARTIAL" | "FAIL" | "UNCLEAR" | "NOT_RUN";
  residual_risk_rationale: "PASS" | "PARTIAL" | "FAIL" | "UNCLEAR" | "NOT_RUN";
  contradictions_found: boolean;
  hallucination_risk: "LOW" | "MEDIUM" | "HIGH" | "NOT_ASSESSED";
  required_human_review: boolean;
  required_reviewer_type: string[];
  blocking_issues: Array<{ issue: string; reason: string; source_reference: string }>;
  non_blocking_comments: string[];
  recommended_status: "INPUT_INCOMPLETE" | "AUTHOR_REVIEWED" | "SME_REVIEW_REQUIRED" | "QA_APPROVAL_REQUIRED" | "REJECTED";
}

export type ReviewLevel =
  | "LEVEL_0_BASELINE_UNCHANGED"
  | "LEVEL_1_QUICK_CHECK"
  | "LEVEL_2_TARGETED_SME_REVIEW"
  | "LEVEL_3_FULL_SME_QA_REVIEW"
  | "INPUT_INCOMPLETE";

export type ReviewBadge =
  | "INPUT_INCOMPLETE"
  | "READY_FOR_PLAUSIBILITY_CHECK"
  | "PLAUSIBILITY_PASS"
  | "PLAUSIBILITY_PARTIAL"
  | "PLAUSIBILITY_FAIL"
  | "EVIDENCE_MISSING"
  | "SME_REQUIRED"
  | "QA_REQUIRED"
  | "AUTHOR_OPS_ACTION";

export interface ReviewQueueItem {
  package_id: string;
  risk_id: string;
  failure_mode: string;
  review_level: ReviewLevel;
  badges: ReviewBadge[];
  required_reviewer_type: string[];
  reason: string;
  next_action: "complete input" | "run plausibility check" | "resolve evidence gap" | "SME review" | "QA approval" | "ready for export";
  priority_rank: number;
}

export interface EvidenceMapRow {
  package_id: string;
  risk_item_claim: string;
  source_snippet_id: string;
  document_type: string;
  evidence_type: EvidenceLink["evidence_type"];
  evidence_quality: EvidenceLink["quality_status"] | "MISSING";
  gap_status: string;
  supports: {
    process_step: boolean;
    failure_mode: boolean;
    cause: boolean;
    effect: boolean;
    existing_control: boolean;
    proposed_control: boolean;
    scoring_suggestion: boolean;
    residual_risk_rationale: boolean;
  };
  claim_supported: string;
}

export interface WorkloadSummary {
  total_packages: number;
  ready_for_review: number;
  input_incomplete: number;
  plausibility_pass: number;
  plausibility_partial: number;
  plausibility_fail: number;
  level_counts: Record<ReviewLevel, number>;
  manual_baseline_hours: number;
  assisted_review_hours: number;
  estimated_reduction_percent: number;
  assumptions: Record<string, number>;
}

const triggerRecord: TriggerRecord = {
  id: "CC-2026-014",
  trigger_type: "change control",
  title: "Automated visual inspection threshold change",
  summary:
    "Sterile injectable aseptic filling line changes the automated visual inspection rejection threshold. Validation report covers the old threshold only; new-threshold validation addendum and training record are missing.",
  source_snippet_ids: ["snip-change-1", "snip-val-1", "snip-sop-1"]
};

const scoringModel: ScoringModel = {
  id: "FMEA-SOD-1-5",
  name: "FMEA Severity, Occurrence, Detectability, RPN",
  dimensions: ["Severity", "Occurrence", "Detectability"],
  risk_formula: "S*O*D",
  scale: "1-5"
};

const baselineItems: Record<string, BaselineRiskItem> = {
  "baseline-false-accept": {
    id: "baseline-false-accept",
    risk_code: "FMEA-AVI-001",
    process_step: "Automated visual inspection",
    failure_mode: "False accept of defective container",
    existing_controls: ["Recipe verification", "Defect challenge set", "Batch review"],
    approved_version: 4
  },
  "baseline-particle": {
    id: "baseline-particle",
    risk_code: "FMEA-AVI-002",
    process_step: "Automated visual inspection",
    failure_mode: "Particulate contamination not detected",
    existing_controls: ["Particle defect standards", "AVI qualification", "Reject trend review"],
    approved_version: 3
  },
  "baseline-data-integrity": {
    id: "baseline-data-integrity",
    risk_code: "FMEA-DI-007",
    process_step: "AVI result handling",
    failure_mode: "Inspection data integrity issue",
    existing_controls: ["Role-based access", "Audit trail review", "Batch record reconciliation"],
    approved_version: 2
  }
};

function snippet(...ids: string[]) {
  return demoSnippets.filter((candidate) => ids.includes(candidate.id));
}

function approvedLibrary(id: string) {
  const item = demoRiskLibrary.find((candidate) => candidate.id === id && candidate.approvalStatus === "APPROVED" && !candidate.retired);
  return item ?? "NO_APPROVED_LIBRARY_MATCH";
}

function evidence(id: string, source_snippet_id: string, evidence_type: EvidenceLink["evidence_type"], quality_status: EvidenceLink["quality_status"], claim_supported: string): EvidenceLink {
  return { id, source_snippet_id, evidence_type, quality_status, claim_supported };
}

function draft(input: Omit<RiskItemDraft, "initial_rpn_suggestion" | "status">): RiskItemDraft {
  return {
    ...input,
    initial_rpn_suggestion: input.severity_suggestion * input.occurrence_suggestion * input.detectability_suggestion,
    status: "AI_DRAFT"
  };
}

export function buildDemoReviewPackages(now = "2026-05-07T12:00:00.000Z"): ReviewPackage[] {
  const packages: ReviewPackage[] = [
    basePackage({
      id: "pkg-false-accept",
      risk_item_draft: draft({
        risk_id: "risk-pkg-001",
        process_step: "Automated visual inspection",
        gmp_area: "sterile manufacturing",
        failure_mode: "False accept of defective container after threshold change",
        potential_cause: "Modified rejection threshold is not yet supported by new-threshold effectiveness evidence",
        potential_effect: "Defective container could remain in accepted batch population",
        impact_categories: ["patient safety", "product quality", "GMP compliance"],
        existing_controls: ["Recipe verification", "Qualified defect challenge set", "Batch review"],
        proposed_additional_controls: ["Execute new-threshold challenge set before routine batch disposition"],
        severity_suggestion: 5,
        occurrence_suggestion: 2,
        detectability_suggestion: 3,
        residual_risk_rationale: "DRAFT only: residual risk cannot be considered ready until validation addendum is attached and reviewed."
      }),
      linked_source_snippets: snippet("snip-change-1", "snip-val-1", "snip-fmea-1"),
      evidence_links: [evidence("ev-false-accept-1", "snip-val-1", "VALIDATION_REPORT", "PARTIAL", "Old-threshold validation coverage only")],
      documented_gaps: [demoGaps[0]],
      risk_library_reference: approvedLibrary("lib-false-accept"),
      baseline_risk_item: baselineItems["baseline-false-accept"],
      created_at: now
    }),
    basePackage({
      id: "pkg-particle",
      risk_item_draft: draft({
        risk_id: "risk-pkg-002",
        process_step: "Automated visual inspection",
        gmp_area: "sterile manufacturing",
        failure_mode: "Particulate contamination not detected",
        potential_cause: "Threshold change may alter sensitivity for visible particle reject decisions",
        potential_effect: "Particulate container could pass inspection and remain available for batch disposition",
        impact_categories: ["patient safety", "product quality", "process control"],
        existing_controls: ["AVI particle detection", "Defect standards", "Reject trend monitoring"],
        proposed_additional_controls: ["Add particle challenge coverage to new-threshold verification"],
        severity_suggestion: 3,
        occurrence_suggestion: 2,
        detectability_suggestion: 3,
        residual_risk_rationale: "DRAFT only: validation SME must confirm challenge coverage for particle classes."
      }),
      linked_source_snippets: snippet("snip-process-1", "snip-change-1", "snip-val-1"),
      evidence_links: [evidence("ev-particle-old-val-1", "snip-val-1", "VALIDATION_REPORT", "PARTIAL", "Old-threshold validation is related but not current-version evidence")],
      documented_gaps: [],
      risk_library_reference: approvedLibrary("lib-false-accept"),
      baseline_risk_item: baselineItems["baseline-particle"],
      created_at: now
    }),
    basePackage({
      id: "pkg-closure-defect",
      risk_item_draft: draft({
        risk_id: "risk-pkg-003",
        process_step: "Automated visual inspection",
        gmp_area: "sterile manufacturing",
        failure_mode: "Container closure defect not detected",
        potential_cause: "Threshold change may alter rejection behavior for closure-defect signals",
        potential_effect: "Container closure defect could remain undetected before batch disposition",
        impact_categories: ["patient safety", "product quality", "sterility assurance"],
        existing_controls: ["AVI closure inspection", "Batch review"],
        proposed_additional_controls: ["Confirm closure-defect challenge set is included in threshold verification"],
        severity_suggestion: 5,
        occurrence_suggestion: 2,
        detectability_suggestion: 3,
        residual_risk_rationale: "DRAFT only: baseline mapping must be completed before critic review."
      }),
      linked_source_snippets: snippet("snip-process-1", "snip-change-1", "snip-val-1"),
      evidence_links: [],
      documented_gaps: [
        {
          id: "gap-closure-baseline",
          riskItemId: "risk-pkg-003",
          priority: "HIGH",
          status: "OPEN",
          description: "Baseline FMEA item for container closure defect detection was not mapped into the package.",
          question: "Which approved baseline FMEA row covers container closure defect detection?"
        }
      ],
      risk_library_reference: approvedLibrary("lib-false-accept"),
      baseline_risk_item: undefined as unknown as BaselineRiskItem,
      created_at: now
    }),
    basePackage({
      id: "pkg-data-integrity",
      risk_item_draft: draft({
        risk_id: "risk-pkg-004",
        process_step: "AVI result handling",
        gmp_area: "data integrity",
        failure_mode: "Inspection data integrity issue",
        potential_cause: "Audit trail review scope may not explicitly include threshold configuration changes",
        potential_effect: "Batch decision record may not fully support the threshold used for inspection",
        impact_categories: ["data integrity", "GMP compliance", "product quality"],
        existing_controls: ["Role-based access", "Audit trail review", "Batch record reconciliation"],
        proposed_additional_controls: [],
        severity_suggestion: 3,
        occurrence_suggestion: 2,
        detectability_suggestion: 3,
        residual_risk_rationale: "DRAFT only: data integrity SME must confirm audit trail review scope and evidence."
      }),
      linked_source_snippets: snippet("snip-sop-1", "snip-change-1", "snip-batch-1"),
      evidence_links: [
        evidence("ev-di-sop-1", "snip-sop-1", "SOP_ONLY", "WEAK", "SOP describes recipe and threshold verification"),
        evidence("ev-di-batch-1", "snip-batch-1", "BATCH_RECORD", "SUFFICIENT_FOR_DRAFT", "Batch record supports result reconciliation fields")
      ],
      documented_gaps: [],
      risk_library_reference: approvedLibrary("lib-data-integrity"),
      baseline_risk_item: baselineItems["baseline-data-integrity"],
      created_at: now
    }),
    basePackage({
      id: "pkg-training-gap",
      risk_item_draft: draft({
        risk_id: "risk-pkg-005",
        process_step: "Training and procedure rollout",
        gmp_area: "sterile manufacturing",
        failure_mode: "Operator use of outdated SOP or missing training for threshold verification",
        potential_cause: "Updated SOP expectations are present, but training record is not linked to the package",
        potential_effect: "Operator may apply threshold verification inconsistently before batch inspection",
        impact_categories: ["GMP compliance", "process control", "product quality"],
        existing_controls: ["SOP revision", "Training matrix"],
        proposed_additional_controls: ["Attach training completion record before routine use"],
        severity_suggestion: 3,
        occurrence_suggestion: 2,
        detectability_suggestion: 3,
        residual_risk_rationale: "DRAFT only: author must obtain or document the missing training record."
      }),
      linked_source_snippets: snippet("snip-sop-1", "snip-change-1"),
      evidence_links: [],
      documented_gaps: [demoGaps[1]],
      risk_library_reference: "NO_APPROVED_LIBRARY_MATCH",
      baseline_risk_item: "NOT_A_DELTA_UPDATE",
      created_at: now
    })
  ];

  return packages.map((pkg) => {
    const gate = inputCompletenessGate(pkg);
    return { ...pkg, package_status: gate.package_status, missing_inputs: gate.missing_inputs };
  });
}

function basePackage(input: Omit<ReviewPackage, "project_id" | "trigger_record" | "scoring_model" | "package_status" | "created_by" | "missing_inputs">): ReviewPackage {
  return {
    project_id: demoProject.id,
    trigger_record: triggerRecord,
    scoring_model: scoringModel,
    package_status: "DRAFT_PACKAGE",
    created_by: "AUTHOR_AI",
    missing_inputs: [],
    ...input
  };
}

export function inputCompletenessGate(pkg: ReviewPackage) {
  const missing_inputs: string[] = [];

  if (!pkg.risk_item_draft) missing_inputs.push("risk_item_draft");
  if (!pkg.trigger_record) missing_inputs.push("trigger_record");
  if (!pkg.linked_source_snippets || pkg.linked_source_snippets.length === 0) missing_inputs.push("linked_source_snippets");
  if (!pkg.scoring_model) missing_inputs.push("scoring_model");
  if ((!pkg.evidence_links || pkg.evidence_links.length === 0) && (!pkg.documented_gaps || pkg.documented_gaps.length === 0)) {
    missing_inputs.push("evidence_links or documented_gaps");
  }
  if (!pkg.risk_library_reference) missing_inputs.push("risk_library_reference or NO_APPROVED_LIBRARY_MATCH");
  if (!pkg.baseline_risk_item) missing_inputs.push("baseline_risk_item");

  return {
    package_status: missing_inputs.length === 0 ? ("READY_FOR_PLAUSIBILITY_CHECK" as const) : ("INPUT_INCOMPLETE" as const),
    missing_inputs
  };
}

export function canRunPlausibilityCheck(pkg: ReviewPackage) {
  const gate = inputCompletenessGate(pkg);
  return pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK" && gate.missing_inputs.length === 0;
}

export async function runPackagePlausibilityCheck(pkg: ReviewPackage): Promise<PackageReviewResult> {
  const gate = inputCompletenessGate(pkg);
  if (pkg.package_status !== "READY_FOR_PLAUSIBILITY_CHECK" || gate.missing_inputs.length > 0) {
    return {
      input_status: "INPUT_INCOMPLETE",
      missing_inputs: gate.missing_inputs,
      overall_result: "NOT_RUN",
      source_support: "NOT_RUN",
      risk_logic: "NOT_RUN",
      control_logic: "NOT_RUN",
      evidence_quality: "NOT_RUN",
      scoring_plausibility: "NOT_RUN",
      residual_risk_rationale: "NOT_RUN",
      contradictions_found: false,
      hallucination_risk: "NOT_ASSESSED",
      required_human_review: false,
      required_reviewer_type: [],
      blocking_issues: [
        {
          issue: "Review package input is incomplete.",
          reason: "The Independent Plausibility Reviewer must not run until the package passes the completeness gate.",
          source_reference: "Input Completeness Gate"
        }
      ],
      non_blocking_comments: [],
      recommended_status: "INPUT_INCOMPLETE"
    };
  }

  const hasEvidenceGap = pkg.documented_gaps.length > 0;
  const hasOnlyWeakEvidence = pkg.evidence_links.length > 0 && pkg.evidence_links.every((link) => link.quality_status === "WEAK" || link.evidence_type === "SOP_ONLY");
  const hasPartialOldValidation = pkg.evidence_links.some((link) => link.evidence_type === "VALIDATION_REPORT" && (link.quality_status === "PARTIAL" || link.quality_status === "WEAK"));
  const noLibraryMatch = pkg.risk_library_reference === "NO_APPROVED_LIBRARY_MATCH";
  const highSeverity = pkg.risk_item_draft.severity_suggestion >= 4;
  const sourceSupport = pkg.linked_source_snippets.length >= 2 ? "PASS" : "PARTIAL";
  const evidenceQuality = hasEvidenceGap || hasPartialOldValidation ? "PARTIAL" : hasOnlyWeakEvidence ? "WEAK" : "SUFFICIENT_FOR_DRAFT";
  const reviewerTypes = new Set<string>(["QA"]);

  if (highSeverity) reviewerTypes.add("Process SME");
  if (pkg.risk_item_draft.failure_mode.toLowerCase().includes("data integrity")) reviewerTypes.add("Data Integrity");
  if (pkg.risk_item_draft.failure_mode.toLowerCase().includes("operator")) reviewerTypes.add("Process SME");
  if (pkg.documented_gaps.some((gap) => gap.description.toLowerCase().includes("validation"))) reviewerTypes.add("Validation");
  if (noLibraryMatch) reviewerTypes.add("Process SME");

  return {
    input_status: "COMPLETE",
    missing_inputs: [],
    overall_result: hasEvidenceGap || hasOnlyWeakEvidence || noLibraryMatch || hasPartialOldValidation ? "PARTIAL" : "PASS",
    source_support: sourceSupport,
    risk_logic: "PASS",
    control_logic: "PASS",
    evidence_quality: evidenceQuality,
    scoring_plausibility: noLibraryMatch ? "UNCLEAR" : "PASS",
    residual_risk_rationale: pkg.risk_item_draft.residual_risk_rationale ? "PARTIAL" : "FAIL",
    contradictions_found: false,
    hallucination_risk: noLibraryMatch ? "MEDIUM" : "LOW",
    required_human_review: highSeverity || noLibraryMatch || hasEvidenceGap || hasPartialOldValidation,
    required_reviewer_type: Array.from(reviewerTypes),
    blocking_issues: hasEvidenceGap
      ? pkg.documented_gaps.map((gap) => ({
          issue: gap.description,
          reason: "The package is complete because the gap is documented, but the gap must be resolved or accepted through the human review workflow before downstream QA decisions.",
          source_reference: gap.id
        }))
      : [],
    non_blocking_comments: [
      "PASS or PARTIAL from this reviewer is not an approval.",
      `Package ${pkg.id} was assembled by ${pkg.created_by} and remains an AI_DRAFT work product.`
    ],
    recommended_status: highSeverity || noLibraryMatch || hasEvidenceGap || hasPartialOldValidation ? "SME_REVIEW_REQUIRED" : "AUTHOR_REVIEWED"
  };
}

export function calculateReviewLevel(
  pkg: ReviewPackage,
  plausibilityResult?: PackageReviewResult,
  _gates: unknown[] = [],
  gaps = pkg.documented_gaps
): ReviewLevel {
  const gate = inputCompletenessGate(pkg);
  if (pkg.package_status === "INPUT_INCOMPLETE" || gate.missing_inputs.length > 0) return "INPUT_INCOMPLETE";

  const result = plausibilityResult?.overall_result ?? "NOT_RUN";
  const noApprovedLibrary = pkg.risk_library_reference === "NO_APPROVED_LIBRARY_MATCH";
  const highSeverity = pkg.risk_item_draft.severity_suggestion >= 4;
  const hasMissingEvidence = gaps.some((gap) => gap.status === "OPEN" && (gap.priority === "HIGH" || gap.priority === "CRITICAL"));
  const hasSufficientEvidence = pkg.evidence_links.some((link) => link.quality_status === "STRONG" || link.quality_status === "SUFFICIENT_FOR_DRAFT");
  const evidencePartialOrWeak = pkg.evidence_links.some((link) => link.quality_status === "PARTIAL" || link.quality_status === "WEAK" || link.evidence_type === "SOP_ONLY") && !hasSufficientEvidence;
  const hasNewControl = pkg.risk_item_draft.proposed_additional_controls.length > 0;

  if (result === "FAIL" || result === "UNCLEAR" || highSeverity || hasMissingEvidence || noApprovedLibrary) {
    return "LEVEL_3_FULL_SME_QA_REVIEW";
  }

  if (result === "PARTIAL" || evidencePartialOrWeak || hasNewControl) return "LEVEL_2_TARGETED_SME_REVIEW";

  if (
    pkg.risk_library_reference !== "NO_APPROVED_LIBRARY_MATCH" &&
    pkg.linked_source_snippets.length >= 2 &&
    pkg.risk_item_draft.proposed_additional_controls.length === 0 &&
    (result === "PASS" || result === "NOT_RUN")
  ) {
    return "LEVEL_1_QUICK_CHECK";
  }

  return "LEVEL_0_BASELINE_UNCHANGED";
}

export function buildReviewQueue(packages: ReviewPackage[], results: Record<string, PackageReviewResult> = {}) {
  const items = packages.map((pkg): ReviewQueueItem => {
    const result = results[pkg.id];
    const review_level = calculateReviewLevel(pkg, result);
    const badges: ReviewBadge[] = [];
    const reviewerTypes = new Set(result?.required_reviewer_type ?? ["QA"]);
    const hasGap = pkg.documented_gaps.some((gap) => gap.status === "OPEN");

    if (pkg.package_status === "INPUT_INCOMPLETE") badges.push("INPUT_INCOMPLETE", "AUTHOR_OPS_ACTION");
    if (pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK") badges.push("READY_FOR_PLAUSIBILITY_CHECK");
    if (result?.overall_result === "PASS") badges.push("PLAUSIBILITY_PASS");
    if (result?.overall_result === "PARTIAL") badges.push("PLAUSIBILITY_PARTIAL");
    if (result?.overall_result === "FAIL") badges.push("PLAUSIBILITY_FAIL");
    if (hasGap) badges.push("EVIDENCE_MISSING");
    if (review_level === "LEVEL_2_TARGETED_SME_REVIEW" || review_level === "LEVEL_3_FULL_SME_QA_REVIEW") badges.push("SME_REQUIRED");
    if (review_level === "LEVEL_3_FULL_SME_QA_REVIEW") badges.push("QA_REQUIRED");

    if (pkg.risk_item_draft.gmp_area === "data integrity") reviewerTypes.add("Data Integrity");
    if (pkg.documented_gaps.some((gap) => gap.description.toLowerCase().includes("validation"))) reviewerTypes.add("Validation");
    if (pkg.risk_item_draft.failure_mode.toLowerCase().includes("closure")) reviewerTypes.add("Microbiology");
    if (pkg.risk_item_draft.failure_mode.toLowerCase().includes("operator")) reviewerTypes.add("Process SME");
    if (pkg.risk_item_draft.severity_suggestion >= 4) reviewerTypes.add("Process SME");

    const reason = reviewReason(pkg, result, review_level);
    const next_action = nextAction(pkg, result, review_level);

    return {
      package_id: pkg.id,
      risk_id: pkg.risk_item_draft.risk_id,
      failure_mode: pkg.risk_item_draft.failure_mode,
      review_level,
      badges,
      required_reviewer_type: Array.from(reviewerTypes),
      reason,
      next_action,
      priority_rank: priorityRank(review_level, pkg, result)
    };
  });

  return items.sort((a, b) => a.priority_rank - b.priority_rank);
}

function reviewReason(pkg: ReviewPackage, result: PackageReviewResult | undefined, level: ReviewLevel) {
  if (level === "INPUT_INCOMPLETE") return `Missing package input: ${pkg.missing_inputs.join(", ")}`;
  if (pkg.documented_gaps.length > 0) return pkg.documented_gaps.map((gap) => gap.description).join("; ");
  if (pkg.risk_library_reference === "NO_APPROVED_LIBRARY_MATCH") return "No approved risk-library match; human confirmation required.";
  if (result?.overall_result === "PASS") return "Plausibility passed for draft review; quick human check remains required.";
  if (result?.overall_result === "PARTIAL") return "Plausibility is partial; targeted issue review required.";
  return "Package is ready for plausibility check before review routing.";
}

function nextAction(pkg: ReviewPackage, result: PackageReviewResult | undefined, level: ReviewLevel): ReviewQueueItem["next_action"] {
  if (level === "INPUT_INCOMPLETE") return "complete input";
  if (!result) return "run plausibility check";
  if (pkg.documented_gaps.length > 0) return "resolve evidence gap";
  if (level === "LEVEL_3_FULL_SME_QA_REVIEW" || level === "LEVEL_2_TARGETED_SME_REVIEW") return "SME review";
  if (result.overall_result === "PASS") return "ready for export";
  return "QA approval";
}

function priorityRank(level: ReviewLevel, pkg: ReviewPackage, result: PackageReviewResult | undefined) {
  const base: Record<ReviewLevel, number> = {
    INPUT_INCOMPLETE: 0,
    LEVEL_3_FULL_SME_QA_REVIEW: 1,
    LEVEL_2_TARGETED_SME_REVIEW: 2,
    LEVEL_1_QUICK_CHECK: 3,
    LEVEL_0_BASELINE_UNCHANGED: 4
  };
  const gapPenalty = pkg.documented_gaps.some((gap) => gap.priority === "CRITICAL" || gap.priority === "HIGH") ? -0.25 : 0;
  const failPenalty = result?.overall_result === "FAIL" || result?.overall_result === "UNCLEAR" ? -0.5 : 0;
  return base[level] + gapPenalty + failPenalty;
}

export function buildEvidenceMap(pkg: ReviewPackage): EvidenceMapRow[] {
  const evidenceBySnippet = new Map(pkg.evidence_links.map((link) => [link.source_snippet_id, link]));

  const rows = pkg.linked_source_snippets.map((snippet) => {
    const evidenceLink = evidenceBySnippet.get(snippet.id);
    const text = `${snippet.text} ${evidenceLink?.claim_supported ?? ""}`.toLowerCase();
    const gap = pkg.documented_gaps.find((candidate) => candidate.description.toLowerCase().includes("training") || candidate.description.toLowerCase().includes("validation"));

    return {
      package_id: pkg.id,
      risk_item_claim: pkg.risk_item_draft.failure_mode,
      source_snippet_id: snippet.id,
      document_type: snippet.documentType,
      evidence_type: evidenceLink?.evidence_type ?? "UNKNOWN",
      evidence_quality: evidenceLink?.quality_status ?? (gap ? "MISSING" : "EXPERT_REVIEW_REQUIRED"),
      gap_status: gap ? `${gap.priority} ${gap.status}` : "No documented gap",
      supports: {
        process_step: text.includes("automated visual inspection") || text.includes("avi"),
        failure_mode: text.includes("defect") || text.includes("particle") || text.includes("threshold") || text.includes("audit"),
        cause: text.includes("threshold") || text.includes("training") || text.includes("configuration"),
        effect: text.includes("batch") || text.includes("defective") || text.includes("reconciliation"),
        existing_control: text.includes("verification") || text.includes("review") || text.includes("controls"),
        proposed_control: Boolean(evidenceLink && evidenceLink.evidence_type !== "SOP_ONLY" && evidenceLink.quality_status !== "WEAK"),
        scoring_suggestion: false,
        residual_risk_rationale: false
      },
      claim_supported: evidenceLink?.claim_supported ?? "No direct evidence link; snippet is source context only"
    } satisfies EvidenceMapRow;
  });

  return rows;
}

export function summarizeWorkload(packages: ReviewPackage[], results: Record<string, PackageReviewResult> = {}): WorkloadSummary {
  const queue = buildReviewQueue(packages, results);
  const level_counts: Record<ReviewLevel, number> = {
    LEVEL_0_BASELINE_UNCHANGED: 0,
    LEVEL_1_QUICK_CHECK: 0,
    LEVEL_2_TARGETED_SME_REVIEW: 0,
    LEVEL_3_FULL_SME_QA_REVIEW: 0,
    INPUT_INCOMPLETE: 0
  };

  for (const item of queue) level_counts[item.review_level] += 1;

  const assumptions = {
    manual_baseline_per_package: 2,
    LEVEL_1_QUICK_CHECK: 0.25,
    LEVEL_2_TARGETED_SME_REVIEW: 0.75,
    LEVEL_3_FULL_SME_QA_REVIEW: 1,
    INPUT_INCOMPLETE: 0.5,
    LEVEL_0_BASELINE_UNCHANGED: 0
  };
  const manual_baseline_hours = packages.length * assumptions.manual_baseline_per_package;
  const assisted_review_hours =
    level_counts.LEVEL_1_QUICK_CHECK * assumptions.LEVEL_1_QUICK_CHECK +
    level_counts.LEVEL_2_TARGETED_SME_REVIEW * assumptions.LEVEL_2_TARGETED_SME_REVIEW +
    level_counts.LEVEL_3_FULL_SME_QA_REVIEW * assumptions.LEVEL_3_FULL_SME_QA_REVIEW +
    level_counts.INPUT_INCOMPLETE * assumptions.INPUT_INCOMPLETE;

  return {
    total_packages: packages.length,
    ready_for_review: packages.filter((pkg) => pkg.package_status === "READY_FOR_PLAUSIBILITY_CHECK" || pkg.package_status === "PLAUSIBILITY_CHECKED").length,
    input_incomplete: packages.filter((pkg) => pkg.package_status === "INPUT_INCOMPLETE").length,
    plausibility_pass: Object.values(results).filter((result) => result.overall_result === "PASS").length,
    plausibility_partial: Object.values(results).filter((result) => result.overall_result === "PARTIAL").length,
    plausibility_fail: Object.values(results).filter((result) => result.overall_result === "FAIL").length,
    level_counts,
    manual_baseline_hours,
    assisted_review_hours,
    estimated_reduction_percent: Math.round(((manual_baseline_hours - assisted_review_hours) / manual_baseline_hours) * 100),
    assumptions
  };
}

export function generateRiskDeltaReviewPack(input: {
  packages: ReviewPackage[];
  results?: Record<string, PackageReviewResult>;
  approvedExport?: boolean;
  generatedAt?: string;
}) {
  const results = input.results ?? {};
  const generatedAt = input.generatedAt ?? new Date().toISOString();
  const queue = buildReviewQueue(input.packages, results);
  const workload = summarizeWorkload(input.packages, results);
  const blockingErrors: string[] = [];

  if (input.approvedExport) {
    blockingErrors.push("Approved export is blocked because package-level QA approval is not implemented for all packages in this MVP.");
  }

  const disclosure =
    "This package contains AI-assisted draft content. AI output was used for extraction, structuring, gap identification, plausibility checks, and draft preparation. Final risk evaluation, scoring, residual-risk acceptance, and approval must be performed by qualified human reviewers.";

  const markdown = [
    "# Risk Delta Review Pack",
    "",
    "## 1. Cover",
    `Project name: ${demoProject.name}`,
    `Product/process/system: ${demoProject.productProcessSystem}`,
    `Trigger record: ${triggerRecord.id} - ${triggerRecord.title}`,
    `Scope: ${demoProject.scopeStatement}`,
    `Date generated: ${generatedAt}`,
    "Draft status: DRAFT REVIEW PACKAGE",
    "",
    "## 2. AI Assistance Disclosure",
    disclosure,
    "",
    "## 3. Executive Summary",
    `Total packages: ${workload.total_packages}`,
    `Ready packages: ${workload.ready_for_review}`,
    `Input incomplete packages: ${workload.input_incomplete}`,
    `Plausibility PASS/PARTIAL/FAIL: ${workload.plausibility_pass}/${workload.plausibility_partial}/${workload.plausibility_fail}`,
    `Evidence gaps: ${input.packages.reduce((sum, pkg) => sum + pkg.documented_gaps.length, 0)}`,
    `SME-required items: ${queue.filter((item) => item.badges.includes("SME_REQUIRED")).length}`,
    `QA-required items: ${queue.filter((item) => item.badges.includes("QA_REQUIRED")).length}`,
    "",
    "## 4. Human Review Workload Summary",
    `Estimated manual baseline: ${workload.manual_baseline_hours.toFixed(1)} hours`,
    `Estimated assisted review: ${workload.assisted_review_hours.toFixed(1)} hours`,
    `Estimated reduction: ${workload.estimated_reduction_percent}%`,
    "Assumptions used: manual baseline 2.0 hours/package; Level 1 0.25 hours; Level 2 0.75 hours; Level 3 demo-assisted exception review 1.0 hour; input completion 0.5 hours. These are demonstration estimates only.",
    "",
    "## 5. Review Queue",
    "| Risk ID | Failure mode | Review level | Reviewer | Reason | Next action |",
    "| --- | --- | --- | --- | --- | --- |",
    ...queue.map((item) => `| ${item.risk_id} | ${item.failure_mode} | ${item.review_level} | ${item.required_reviewer_type.join(", ")} | ${item.reason} | ${item.next_action} |`),
    "",
    "## 6. Risk Delta Matrix",
    "| Risk ID | Baseline | Proposed change | Process step | Cause | Effect | Evidence | Gaps | Plausibility | Recommended status |",
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ...input.packages.map((pkg) => {
      const baseline = pkg.baseline_risk_item === "NOT_A_DELTA_UPDATE" ? "NOT_A_DELTA_UPDATE" : pkg.baseline_risk_item ? pkg.baseline_risk_item.risk_code : "Missing";
      const result = results[pkg.id];
      return `| ${pkg.risk_item_draft.risk_id} | ${baseline} | ${pkg.risk_item_draft.failure_mode} | ${pkg.risk_item_draft.process_step} | ${pkg.risk_item_draft.potential_cause} | ${pkg.risk_item_draft.potential_effect} | ${pkg.evidence_links.map((link) => link.quality_status).join(", ") || "Gap documented"} | ${pkg.documented_gaps.map((gap) => gap.description).join("; ") || "None"} | ${result?.overall_result ?? "NOT_RUN"} | ${result?.recommended_status ?? pkg.package_status} |`;
    }),
    "",
    "## 7. Evidence Map",
    ...input.packages.flatMap((pkg) => [
      `### ${pkg.risk_item_draft.risk_id}`,
      ...buildEvidenceMap(pkg).map((row) => `- ${row.source_snippet_id} (${row.document_type}) - ${row.evidence_type}/${row.evidence_quality}: ${row.claim_supported}`)
    ]),
    "",
    "## 8. Blocking Issues",
    ...queue.filter((item) => item.review_level === "INPUT_INCOMPLETE" || item.badges.includes("EVIDENCE_MISSING")).map((item) => `- ${item.risk_id}: ${item.reason}`),
    "",
    "## 9. Open Questions for SME/QA",
    ...input.packages.flatMap((pkg) => pkg.documented_gaps.map((gap) => `- ${pkg.risk_item_draft.risk_id}: ${gap.question ?? gap.description}`)),
    "",
    "## 10. Audit Trail Summary",
    `Generated timestamp: ${generatedAt}`,
    `Package IDs: ${input.packages.map((pkg) => pkg.id).join(", ")}`,
    `Plausibility check IDs: ${Object.keys(results).map((id) => `pc-${id}`).join(", ") || "Not run"}`,
    "Status transitions: DRAFT_PACKAGE -> READY_FOR_PLAUSIBILITY_CHECK/INPUT_INCOMPLETE -> PLAUSIBILITY_CHECKED where run.",
    "",
    "## 11. Limitations",
    "- This is a draft review package.",
    "- It does not claim regulatory compliance.",
    "- It does not replace qualified SME or QA approval.",
    "- It does not guarantee authority acceptance.",
    "- Production use requires validation under the customer's quality system."
  ].join("\n");

  const csv = [
    "Risk ID,Failure Mode,Review Level,Required Reviewer,Next Action,Plausibility,Evidence Gaps",
    ...queue.map((item) =>
      [
        item.risk_id,
        item.failure_mode,
        item.review_level,
        item.required_reviewer_type.join("; "),
        item.next_action,
        results[item.package_id]?.overall_result ?? "NOT_RUN",
        input.packages.find((pkg) => pkg.id === item.package_id)?.documented_gaps.map((gap) => gap.description).join("; ") ?? ""
      ]
        .map((value) => `"${String(value).replaceAll("\"", "\"\"")}"`)
        .join(",")
    )
  ].join("\n");

  return {
    ok: blockingErrors.length === 0,
    errors: blockingErrors,
    markdown,
    csv,
    json: {
      project: demoProject,
      trigger_record: triggerRecord,
      workload,
      review_queue: queue,
      packages: input.packages,
      plausibility_results: results
    }
  };
}
