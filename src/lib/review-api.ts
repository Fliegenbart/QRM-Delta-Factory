import "server-only";

import type {
  DocumentSet,
  PipelineRun,
  ReviewDecisionValue,
  ReviewPack
} from "@/src/lib/review-ui";
import { normalizeReviewDecisionPayload } from "@/src/lib/review-ui";

const DEFAULT_BACKEND_URL = "http://localhost:8000";

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
  const tenantId =
    process.env.QRM_BACKEND_TENANT_ID ??
    process.env.QRM_TENANT_ID ??
    "tenant_example_pharma";
  const requirementSetId =
    process.env.QRM_DEFAULT_REQUIREMENT_SET_ID ??
    "rset_example_gmp_qrm_2026_1";

  return backendFetch<DocumentSet>("/document-sets", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      tenant_id: tenantId,
      requirement_set_id: requirementSetId,
      declared_document_type: input.declaredDocumentType,
      declared_process_area: input.declaredProcessArea,
      uploaded_by: input.uploadedBy
    })
  });
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
  const backendUrl = process.env.QRM_BACKEND_URL ?? DEFAULT_BACKEND_URL;
  const apiKey = process.env.QRM_BACKEND_API_KEY;
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
