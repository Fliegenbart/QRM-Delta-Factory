import "server-only";

import type {
  DocumentSet,
  PipelineRun,
  ReviewDecisionValue,
  ReviewPack
} from "@/src/lib/review-ui";
import { normalizeReviewDecisionPayload } from "@/src/lib/review-ui";
import { getReviewBackendConfig } from "@/src/lib/review-runtime-config";

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

async function backendFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
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

  return (await response.json()) as T;
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

async function activateRequirementSet(requirementSetId: string): Promise<void> {
  await backendFetch(`/requirement-sets/${encodeURIComponent(requirementSetId)}/activate`, {
    method: "POST"
  });
}

async function ensureRequirementSet(input: {
  requirementSetId: string;
  tenantId: string;
}): Promise<void> {
  try {
    await activateRequirementSet(input.requirementSetId);
    return;
  } catch (error) {
    if (!isMissingRequirementSetError(error, input.requirementSetId)) {
      throw error;
    }
  }

  await importDefaultRequirementSet(input);
  await activateRequirementSet(input.requirementSetId);
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
  return {
    requirement_set_id: input.requirementSetId,
    tenant_id: input.tenantId,
    name: "Default GMP QRM Requirement Library",
    version: "2026.1",
    imported_at: "2026-05-09T09:00:00Z",
    imported_by: "user_quality_admin",
    active: true,
    requirements: [
      {
        requirement_id: "req_val_threshold_current_evidence",
        source_type: "internal_sop",
        source_name: "SOP-QRM-AVI-001",
        source_version: "3.0",
        section: "6.4",
        requirement_text:
          "Changed automated inspection thresholds require verification or validation evidence applicable to the changed setting.",
        applies_to_document_types: ["change_control_package", "validation_report"],
        applies_to_process_areas: ["automated_visual_inspection", "aseptic_filling"],
        criticality: "high",
        required_evidence: ["current validation report", "approved validation addendum"],
        auto_close_allowed: false,
        effective_from: "2026-01-01T00:00:00Z",
        effective_to: null
      }
    ]
  };
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
