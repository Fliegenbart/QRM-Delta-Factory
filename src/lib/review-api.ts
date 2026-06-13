import "server-only";

import type {
  DocumentSet,
  CalibrationExample,
  CalibrationRegressionGateReport,
  HumanFeedbackRegistryReport,
  PipelineRun,
  Requirement,
  RequirementLibraryOverview,
  ReviewCalibrationReport,
  RequirementSet,
  ReviewDecisionValue,
  ReviewPack
} from "@/src/lib/review-ui";
import { normalizeReviewDecisionPayload } from "@/src/lib/review-ui";
import { getReviewBackendConfig } from "@/src/lib/review-runtime-config";
import gmpGeneralRequirementLibrary from "@/src/data/gmp-general-requirement-library.json";

export class ReviewApiError extends Error {
  constructor(
    message: string,
    readonly status?: number
  ) {
    super(message);
  }
}

export async function listDocumentSets(): Promise<DocumentSet[]> {
  return backendFetch<DocumentSet[]>("/document-sets");
}

export async function createDocumentSet(input: {
  declaredDocumentType: string;
  declaredProcessArea: string;
  uploadedBy: string;
}): Promise<DocumentSet> {
  const { tenantId, requirementSetId } = getReviewBackendConfig();
  await ensureRequirementSet({ requirementSetId, tenantId });
  const payload = {
    tenant_id: tenantId,
    requirement_set_id: requirementSetId,
    declared_document_type: input.declaredDocumentType,
    declared_process_area: input.declaredProcessArea,
    uploaded_by: input.uploadedBy
  };

  try {
    return await postDocumentSet(payload);
  } catch (error) {
    if (!isRecoverableRequirementSetError(error, requirementSetId)) {
      throw error;
    }
    await ensureRequirementSet({ requirementSetId, tenantId });
    return postDocumentSet(payload);
  }
}

export async function getDocumentSet(documentSetId: string): Promise<DocumentSet> {
  return backendFetch<DocumentSet>(`/document-sets/${encodeURIComponent(documentSetId)}`);
}

export async function deleteDocumentSet(documentSetId: string): Promise<void> {
  await backendFetchWithoutJson(`/document-sets/${encodeURIComponent(documentSetId)}`, {
    method: "DELETE"
  });
}

export async function uploadDocumentToDocumentSet(input: {
  documentSetId: string;
  file: File;
  uploadedBy: string;
}) {
  const formData = new FormData();
  formData.set("uploaded_by", input.uploadedBy);
  formData.set("file", input.file);

  return backendFetch(`/document-sets/${encodeURIComponent(input.documentSetId)}/documents`, {
    method: "POST",
    body: formData
  });
}

export async function runPipeline(documentSetId: string): Promise<PipelineRun> {
  return backendFetch<PipelineRun>(
    `/document-sets/${encodeURIComponent(documentSetId)}/pipeline-runs`,
    { method: "POST" }
  );
}

export async function getReviewPack(documentSetId: string): Promise<ReviewPack> {
  return backendFetch<ReviewPack>(
    `/document-sets/${encodeURIComponent(documentSetId)}/review-pack`
  );
}

export async function getRequirementLibraryOverview(): Promise<RequirementLibraryOverview> {
  const { requirementSetId, tenantId } = getReviewBackendConfig();
  await ensureRequirementSet({ requirementSetId, tenantId });
  try {
    return await fetchRequirementLibraryOverview(requirementSetId);
  } catch (error) {
    if (!isMissingRequirementSetError(error, requirementSetId)) {
      throw error;
    }
    await ensureRequirementSet({ requirementSetId, tenantId });
    return fetchRequirementLibraryOverview(requirementSetId);
  }
}

export async function getHumanFeedbackRegistry(): Promise<HumanFeedbackRegistryReport> {
  return backendFetch<HumanFeedbackRegistryReport>("/analytics/human-feedback");
}

export async function getReviewCalibrationReport(): Promise<ReviewCalibrationReport> {
  return backendFetch<ReviewCalibrationReport>("/analytics/review-calibration");
}

export async function runReviewCalibrationRegressionGate(): Promise<CalibrationRegressionGateReport> {
  return backendFetch<CalibrationRegressionGateReport>(
    "/analytics/review-calibration/run-regression-gate",
    { method: "POST" }
  );
}

export async function approveReviewCalibrationExample(input: {
  calibrationExampleId: string;
  approvedBy: string;
  activate?: boolean;
  regressionGateReportId?: string;
  regressionGatePassed?: boolean;
}): Promise<CalibrationExample> {
  return backendFetch<CalibrationExample>(
    `/analytics/review-calibration/${encodeURIComponent(input.calibrationExampleId)}/approve`,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        approved_by: normalizeReviewerId(input.approvedBy),
        activate: Boolean(input.activate),
        regression_gate_passed: Boolean(input.regressionGatePassed),
        regression_gate_report_id: input.regressionGateReportId || null
      })
    }
  );
}

export async function importRequirementLibrary(input: {
  file: File;
  importedBy: string;
}): Promise<RequirementLibraryOverview> {
  const { requirementSetId } = getReviewBackendConfig();
  const formData = new FormData();
  formData.set("file", input.file);
  formData.set("imported_by", input.importedBy);

  const requirementSet = await backendFetch<RequirementSet>("/requirement-sets/import", {
    method: "POST",
    body: formData
  });
  if (requirementSet.requirement_set_id !== requirementSetId) {
    throw new ReviewApiError(
      `Das importierte Regelwerk hat die ID ${requirementSet.requirement_set_id}. Für neue Analysen ist aktuell ${requirementSetId} konfiguriert.`
    );
  }
  await activateRequirementSet(requirementSet.requirement_set_id);
  return fetchRequirementLibraryOverview(requirementSetId);
}

export async function submitReviewDecision(input: {
  findingId: string;
  reviewerId: string;
  decision: ReviewDecisionValue;
  rationale: string;
}) {
  return backendFetch(`/findings/${encodeURIComponent(input.findingId)}/review-decision`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(
      normalizeReviewDecisionPayload({
        reviewerId: input.reviewerId,
        decision: input.decision,
        rationale: input.rationale
      })
    )
  });
}

function normalizeReviewerId(value: string): string {
  const trimmed = value.trim() || "qa_lead";
  return trimmed.startsWith("reviewer_") ? trimmed : `reviewer_${trimmed}`;
}

async function backendFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await rawBackendFetch(path, init);
  return (await response.json()) as T;
}

async function backendFetchWithoutJson(path: string, init: RequestInit = {}): Promise<void> {
  await rawBackendFetch(path, init);
}

async function rawBackendFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const { backendUrl, apiKey } = getReviewBackendConfig();
  const headers = new Headers(init.headers);
  headers.set("accept", "application/json");
  if (apiKey) {
    headers.set("X-API-Key", apiKey);
  }

  let response: Response;
  try {
    response = await fetch(`${backendUrl}${path}`, {
      ...init,
      headers,
      cache: "no-store"
    });
  } catch {
    throw new ReviewApiError(
      "Backend nicht verbunden. Prüfe QRM_BACKEND_URL und QRM_BACKEND_API_KEY."
    );
  }

  if (!response.ok) {
    const message = await response.text();
    throw new ReviewApiError(message || response.statusText, response.status);
  }

  return response;
}

function postDocumentSet(payload: {
  tenant_id: string;
  requirement_set_id: string;
  declared_document_type: string;
  declared_process_area: string;
  uploaded_by: string;
}): Promise<DocumentSet> {
  return backendFetch<DocumentSet>("/document-sets", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
}

async function activateRequirementSet(requirementSetId: string): Promise<RequirementSet> {
  return backendFetch<RequirementSet>(`/requirement-sets/${encodeURIComponent(requirementSetId)}/activate`, {
    method: "POST"
  });
}

async function getRequirementSet(requirementSetId: string): Promise<RequirementSet> {
  return backendFetch<RequirementSet>(`/requirement-sets/${encodeURIComponent(requirementSetId)}`);
}

async function searchActiveRequirements(): Promise<Requirement[]> {
  return backendFetch<Requirement[]>("/requirements/search");
}

async function fetchRequirementLibraryOverview(
  requirementSetId: string
): Promise<RequirementLibraryOverview> {
  const [requirementSet, activeRequirements] = await Promise.all([
    getRequirementSet(requirementSetId),
    searchActiveRequirements()
  ]);
  return {
    configuredRequirementSetId: requirementSetId,
    requirementSet,
    activeRequirements
  };
}

async function ensureRequirementSet(input: {
  requirementSetId: string;
  tenantId: string;
}): Promise<void> {
  let existingRequirementSet: RequirementSet | null = null;
  try {
    existingRequirementSet = await activateRequirementSet(input.requirementSetId);
  } catch (error) {
    if (!isMissingRequirementSetError(error, input.requirementSetId)) {
      throw error;
    }
  }

  if (
    existingRequirementSet === null ||
    shouldReplaceLegacyDefaultRequirementSet(existingRequirementSet)
  ) {
    await importDefaultRequirementSet(input);
    await activateRequirementSet(input.requirementSetId);
  }
}

async function importDefaultRequirementSet(input: {
  requirementSetId: string;
  tenantId: string;
}): Promise<void> {
  const formData = new FormData();
  const requirementSet = defaultRequirementSet(input);
  formData.set(
    "file",
    new Blob([JSON.stringify(requirementSet, null, 2)], { type: "application/json" }),
    `${input.requirementSetId}.json`
  );
  formData.set("imported_by", requirementSet.imported_by);

  await backendFetch("/requirement-sets/import", {
    method: "POST",
    body: formData
  });
}

function defaultRequirementSet(input: { requirementSetId: string; tenantId: string }) {
  const template = gmpGeneralRequirementLibrary as unknown as RequirementSet;
  return {
    ...template,
    requirement_set_id: input.requirementSetId,
    tenant_id: input.tenantId,
    imported_at: new Date().toISOString(),
    imported_by: "user_quality_admin",
    active: true,
    requirements: template.requirements.map((requirement) => ({ ...requirement }))
  };
}

function shouldReplaceLegacyDefaultRequirementSet(requirementSet: RequirementSet): boolean {
  // Replace earlier seed libraries with the grounded general GMP library:
  // the original one-rule stub, the old "Default" name, and the synthetic
  // Grünewald SOP set. Any set whose requirements are not source-grounded
  // (no regulatory source_refs like "EU GMP Annex 11 §9") is treated as legacy.
  const isGroundedGeneralLibrary = requirementSet.requirements.some((requirement) =>
    requirement.requirement_id?.startsWith("req_di_") ||
    requirement.requirement_id?.startsWith("req_dev_") ||
    requirement.requirement_id?.startsWith("req_capa_effectiveness")
  );
  return (
    requirementSet.name === "Default GMP QRM Requirement Library" ||
    requirementSet.name === "Grünewald Synthetic GMP/QRM Rule Library" ||
    (
      requirementSet.requirements.length === 1 &&
      requirementSet.requirements[0]?.requirement_id === "req_val_threshold_current_evidence"
    ) ||
    !isGroundedGeneralLibrary
  );
}

function isRecoverableRequirementSetError(
  error: unknown,
  requirementSetId: string
): boolean {
  return (
    isInactiveRequirementSetError(error, requirementSetId) ||
    isMissingRequirementSetError(error, requirementSetId)
  );
}

function isInactiveRequirementSetError(error: unknown, requirementSetId: string): boolean {
  if (!(error instanceof ReviewApiError)) {
    return false;
  }
  return (
    error.status === 422 &&
    error.message.includes(`RequirementSet ${requirementSetId} is not active`)
  );
}

function isMissingRequirementSetError(error: unknown, requirementSetId: string): boolean {
  if (!(error instanceof ReviewApiError)) {
    return false;
  }
  return (
    error.status === 404 &&
    error.message.includes(`RequirementSet ${requirementSetId} not found`)
  );
}
