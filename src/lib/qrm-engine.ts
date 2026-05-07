export type Role = "ADMIN" | "QRM_AUTHOR" | "SME_REVIEWER" | "QA_APPROVER" | "AUDITOR";
export type RiskStatus =
  | "AI_DRAFT"
  | "AUTHOR_REVIEWED"
  | "SME_REVIEW_REQUIRED"
  | "SME_REVIEWED"
  | "QA_APPROVAL_REQUIRED"
  | "QA_APPROVED"
  | "REJECTED"
  | "SUPERSEDED";

export type Priority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type EvidenceQualityStatus =
  | "SUFFICIENT_FOR_DRAFT"
  | "PARTIAL"
  | "WEAK"
  | "MISSING"
  | "CONTRADICTORY"
  | "EXPERT_REVIEW_REQUIRED";

export type EvidenceType =
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

export type PlausibilityResult = "PASS" | "PARTIAL" | "FAIL" | "UNCLEAR";

export interface UserLike {
  id: string;
  name: string;
  role: Role;
}

export interface RiskItemLike {
  id: string;
  projectId: string;
  processStep: string;
  gmpArea: string;
  failureMode: string;
  potentialCause: string;
  potentialEffect: string;
  impactCategories: readonly string[];
  existingControls: readonly string[];
  sourceLinks: readonly string[];
  libraryItemId?: string;
  libraryApprovalStatus?: "APPROVED" | "DRAFT" | "RETIRED";
  severity: number;
  occurrence: number;
  detectability: number;
  humanSeverity?: number;
  humanOccurrence?: number;
  humanDetectability?: number;
  residualRiskRationale?: string;
  proposedControls: readonly string[];
  requiredEvidence: readonly string[];
  evidenceStatus: EvidenceQualityStatus;
  confidence: "LOW" | "MEDIUM" | "HIGH";
  priority: Priority;
  deterministicGateResult: string;
  plausibilityResult: PlausibilityResult;
  redTeamResult: string;
  reviewLevel: number;
  reviewStatus: RiskStatus;
  status: RiskStatus;
  version: number;
}

export interface GapLike {
  id: string;
  priority: Priority;
  status: "OPEN" | "RESOLVED";
  description: string;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  action: string;
  entityType: string;
  entityId: string;
  beforeValue: unknown;
  afterValue: unknown;
  reason?: string;
  eventPayloadHash: string;
  previousEventHash: string;
}

export function sha256(value: unknown) {
  const input = JSON.stringify(value);
  let a = 0x811c9dc5;
  let b = 0x01000193;
  let c = 0x9e3779b9;
  let d = 0x85ebca6b;

  for (let index = 0; index < input.length; index += 1) {
    const code = input.charCodeAt(index);
    a = Math.imul(a ^ code, 0x01000193) >>> 0;
    b = Math.imul(b + code + index, 0x85ebca6b) >>> 0;
    c = Math.imul(c ^ (code << (index % 8)), 0xc2b2ae35) >>> 0;
    d = Math.imul(d + (code ^ index), 0x27d4eb2f) >>> 0;
  }

  const words = [a, b, c, d, (a ^ c) >>> 0, (b ^ d) >>> 0, (a ^ b ^ c) >>> 0, (b ^ c ^ d) >>> 0];
  return words.map((word) => word.toString(16).padStart(8, "0")).join("");
}

export function appendAuditLog(input: {
  user: UserLike;
  action: string;
  entityType: string;
  entityId: string;
  beforeValue: unknown;
  afterValue: unknown;
  reason?: string;
  previousEventHash?: string;
}): AuditEntry {
  const payload = {
    timestamp: new Date().toISOString(),
    userId: input.user.id,
    action: input.action,
    entityType: input.entityType,
    entityId: input.entityId,
    beforeValue: input.beforeValue,
    afterValue: input.afterValue,
    reason: input.reason ?? ""
  };

  const previousEventHash = input.previousEventHash ?? sha256("GENESIS");

  return {
    id: `audit-${sha256(payload).slice(0, 12)}`,
    timestamp: payload.timestamp,
    userId: input.user.id,
    userName: input.user.name,
    action: input.action,
    entityType: input.entityType,
    entityId: input.entityId,
    beforeValue: input.beforeValue,
    afterValue: input.afterValue,
    reason: input.reason,
    eventPayloadHash: sha256(payload),
    previousEventHash
  };
}

export function runDeterministicGates(item: RiskItemLike) {
  const errors: string[] = [];

  if (item.sourceLinks.length === 0) errors.push("At least one source link is required.");
  if (item.status === "AI_DRAFT") errors.push("AI_DRAFT must be human reviewed before QA approval.");
  if (item.proposedControls.length > 0 && item.requiredEvidence.length === 0 && item.evidenceStatus !== "MISSING") {
    errors.push("Proposed controls need evidence or an explicit evidence-missing gap.");
  }
  if (item.requiredEvidence.length > 0 && item.evidenceStatus === "MISSING") {
    errors.push("Required evidence is missing.");
  }
  if (
    (item.severity !== item.humanSeverity || item.occurrence !== item.humanOccurrence || item.detectability !== item.humanDetectability) &&
    !item.residualRiskRationale
  ) {
    errors.push("Score changes need a rationale.");
  }
  if (!item.residualRiskRationale) errors.push("Residual risk acceptance rationale is required.");
  if (item.severity >= 4 && item.reviewStatus !== "SME_REVIEWED" && item.reviewStatus !== "QA_APPROVAL_REQUIRED") {
    errors.push("High-severity item requires SME review.");
  }
  if (!item.libraryItemId || item.libraryApprovalStatus === "DRAFT" || item.libraryApprovalStatus === "RETIRED") {
    errors.push("Approved risk-library basis is missing or unavailable.");
  }
  if (item.plausibilityResult === "FAIL" || item.plausibilityResult === "UNCLEAR") {
    errors.push("Plausibility check must not be FAIL or UNCLEAR.");
  }

  return {
    ok: errors.length === 0,
    errors,
    gateResult: errors.length === 0 ? "PASS" : "BLOCKED"
  };
}

export function approveRiskItem(input: { item: RiskItemLike; user: UserLike }) {
  const errors: string[] = [];

  if (input.user.role !== "QA_APPROVER") errors.push("Only a QA Approver can perform this approval step.");
  if (input.item.sourceLinks.length === 0) errors.push("At least one source link is required.");
  if (input.item.status === "AI_DRAFT") errors.push("AI_DRAFT cannot move directly to QA_APPROVED.");
  if (input.item.status !== "QA_APPROVAL_REQUIRED") errors.push("Risk item must be in QA_APPROVAL_REQUIRED status.");
  if (input.item.plausibilityResult === "FAIL" || input.item.plausibilityResult === "UNCLEAR") {
    errors.push("Plausibility check must not be FAIL or UNCLEAR.");
  }
  if (!input.item.humanSeverity || !input.item.humanOccurrence || !input.item.humanDetectability) {
    errors.push("Human-confirmed scores are required.");
  }
  if (!input.item.residualRiskRationale) errors.push("Residual risk acceptance rationale is required.");
  if (input.item.evidenceStatus === "MISSING" || input.item.evidenceStatus === "CONTRADICTORY") {
    errors.push("Evidence status blocks this approval step.");
  }

  const gates = runDeterministicGates(input.item);
  for (const error of gates.errors) {
    if (!errors.includes(error) && error !== "AI_DRAFT must be human reviewed before QA approval.") errors.push(error);
  }

  return {
    ok: errors.length === 0,
    errors,
    item: errors.length === 0 ? { ...input.item, status: "QA_APPROVED" as const, reviewStatus: "QA_APPROVED" as const } : input.item,
    auditLog:
      errors.length === 0
        ? appendAuditLog({
            user: input.user,
            action: "APPROVAL_RECORDED",
            entityType: "RiskItem",
            entityId: input.item.id,
            beforeValue: input.item.status,
            afterValue: "QA_APPROVED",
            reason: "QA approval workflow completed by qualified role."
          })
        : undefined
  };
}

export function transitionRiskStatus(input: {
  item: RiskItemLike;
  to: RiskStatus;
  user: UserLike;
  reason: string;
}) {
  const errors: string[] = [];

  if (input.item.status === "AI_DRAFT" && input.to === "QA_APPROVED") {
    errors.push("AI_DRAFT cannot move directly to QA_APPROVED.");
  }
  if (input.to === "QA_APPROVED") {
    const approval = approveRiskItem({ item: { ...input.item, status: "QA_APPROVAL_REQUIRED" }, user: input.user });
    errors.push(...approval.errors);
  }

  return {
    ok: errors.length === 0,
    errors,
    item: errors.length === 0 ? { ...input.item, status: input.to, reviewStatus: input.to } : input.item,
    auditLog:
      errors.length === 0
        ? appendAuditLog({
            user: input.user,
            action: "STATUS_CHANGED",
            entityType: "RiskItem",
            entityId: input.item.id,
            beforeValue: input.item.status,
            afterValue: input.to,
            reason: input.reason
          })
        : undefined
  };
}

export function editApprovedRiskItem(item: RiskItemLike, changes: Partial<RiskItemLike>) {
  if (item.status !== "QA_APPROVED") return { oldItem: item, newItem: { ...item, ...changes } };

  return {
    oldItem: { ...item, status: "SUPERSEDED" as const, reviewStatus: "SUPERSEDED" as const },
    newItem: {
      ...item,
      ...changes,
      id: `${item.id}-v${item.version + 1}`,
      version: item.version + 1,
      status: "AUTHOR_REVIEWED" as const,
      reviewStatus: "AUTHOR_REVIEWED" as const,
      deterministicGateResult: "RECHECK_REQUIRED"
    }
  };
}

export function exportPackage(input: {
  project: { id: string; name: string; scopeStatement: string; outOfScopeStatement: string; methodology: string };
  riskItems: RiskItemLike[];
  gaps: GapLike[];
  approvedPackage: boolean;
}) {
  const errors: string[] = [];
  const blockingGaps = input.gaps.filter((gap) => gap.status === "OPEN" && (gap.priority === "HIGH" || gap.priority === "CRITICAL"));
  const missingEvidence = input.riskItems.filter((item) => item.evidenceStatus === "MISSING");

  if (input.approvedPackage && blockingGaps.length > 0) {
    errors.push("Approved-style export is blocked while CRITICAL or HIGH gaps remain open.");
  }
  if (input.approvedPackage && missingEvidence.length > 0) {
    errors.push("Approved-style export is blocked while risk items have missing evidence.");
  }

  const disclaimer =
    "This package contains AI-assisted draft content. AI output was used for extraction, structuring, gap identification, plausibility checks, and draft preparation. Final risk evaluation, scoring, residual-risk acceptance, and approval were performed by qualified human reviewers.";

  const markdown = [
    `# ${input.project.name}`,
    "",
    "## QRM project scope",
    input.project.scopeStatement,
    "",
    "## Out of scope",
    input.project.outOfScopeStatement,
    "",
    "## Methodology",
    input.project.methodology,
    "",
    "## AI assistance disclosure",
    disclaimer,
    "",
    "## Risk assessment matrix",
    "| Risk ID | Step | Failure mode / hazard | Status | Evidence | Plausibility |",
    "| --- | --- | --- | --- | --- | --- |",
    ...input.riskItems.map(
      (item) =>
        `| ${item.id} | ${item.processStep} | ${item.failureMode} | ${item.status} | ${item.evidenceStatus} | ${item.plausibilityResult} |`
    ),
    "",
    "## Gap list",
    ...input.gaps.map((gap) => `- ${gap.priority}: ${gap.description} (${gap.status})`),
    "",
    "## Limitations statement",
    "All AI-generated entries remain reviewable draft work products until the assigned qualified personnel complete their workflow steps."
  ].join("\n");

  return { ok: errors.length === 0, errors, markdown };
}

export function createSourceSnippet(input: {
  id: string;
  documentId: string;
  documentType: string;
  sectionTitle: string;
  lineReference: string;
  text: string;
}) {
  return {
    ...input,
    snippetHash: sha256({
      documentId: input.documentId,
      documentType: input.documentType,
      sectionTitle: input.sectionTitle,
      lineReference: input.lineReference,
      text: input.text
    }),
    createdAt: new Date().toISOString()
  };
}

export function canUseLibraryItemAsApprovedBasis(item: { approvalStatus: string; retired: boolean }) {
  return item.approvalStatus === "APPROVED" && !item.retired;
}

export function classifyEvidence(type: EvidenceType, claim: "CONTROL_EFFECTIVENESS" | "CONTROL_DESCRIPTION" | "EXECUTION") {
  if (type === "UNKNOWN") return "EXPERT_REVIEW_REQUIRED" satisfies EvidenceQualityStatus;
  if (claim === "CONTROL_EFFECTIVENESS" && (type === "VALIDATION_REPORT" || type === "VERIFICATION_TEST" || type === "EFFECTIVENESS_CHECK")) {
    return "SUFFICIENT_FOR_DRAFT" satisfies EvidenceQualityStatus;
  }
  if (claim === "CONTROL_EFFECTIVENESS" && type === "SOP_ONLY") return "WEAK" satisfies EvidenceQualityStatus;
  if (claim === "EXECUTION" && type === "BATCH_RECORD") return "SUFFICIENT_FOR_DRAFT" satisfies EvidenceQualityStatus;
  if (claim === "CONTROL_DESCRIPTION" && (type === "SOP_ONLY" || type === "CONTROL_DESCRIPTION")) {
    return "SUFFICIENT_FOR_DRAFT" satisfies EvidenceQualityStatus;
  }
  if (type === "DEVIATION_CAPA") return "PARTIAL" satisfies EvidenceQualityStatus;
  return "PARTIAL" satisfies EvidenceQualityStatus;
}

export function classifyReviewLevel(item: RiskItemLike) {
  if (
    item.priority === "CRITICAL" ||
    item.severity >= 4 ||
    item.evidenceStatus === "MISSING" ||
    item.evidenceStatus === "CONTRADICTORY" ||
    item.plausibilityResult === "FAIL" ||
    item.plausibilityResult === "UNCLEAR" ||
    !item.libraryItemId ||
    item.redTeamResult.includes("MISSING_RISK")
  ) {
    return 3;
  }
  if (item.proposedControls.length > 0 || item.severity !== item.humanSeverity || item.occurrence !== item.humanOccurrence) return 2;
  if (item.libraryItemId && item.sourceLinks.length > 0 && item.priority === "LOW") return 1;
  return 0;
}

export function sortReviewQueue<T extends RiskItemLike>(items: T[]) {
  const priorityRank: Record<Priority, number> = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
  return [...items].sort((a, b) => {
    const level = b.reviewLevel - a.reviewLevel;
    if (level !== 0) return level;
    return priorityRank[a.priority] - priorityRank[b.priority];
  });
}

export function deleteSourceSnippet(snippetId: string, riskItems: RiskItemLike[]) {
  const flaggedRiskItems = riskItems.map((item) =>
    item.sourceLinks.includes(snippetId)
      ? {
          ...item,
          reviewStatus: "SME_REVIEW_REQUIRED" as const,
          status: item.status === "QA_APPROVED" ? ("AUTHOR_REVIEWED" as const) : item.status,
          deterministicGateResult: "SOURCE_SUPERSEDED_REVIEW_REQUIRED"
        }
      : item
  );

  return {
    deletedSnippetId: snippetId,
    flaggedRiskItems
  };
}
