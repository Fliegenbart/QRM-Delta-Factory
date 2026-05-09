import "server-only";

import type {
  DemoSeedResponse,
  DocumentSet,
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

export async function getDocumentSet(documentSetId: string): Promise<DocumentSet> {
  return backendFetch<DocumentSet>(`/document-sets/${encodeURIComponent(documentSetId)}`);
}

export async function getReviewPack(documentSetId: string): Promise<ReviewPack> {
  return backendFetch<ReviewPack>(
    `/document-sets/${encodeURIComponent(documentSetId)}/review-pack`
  );
}

export async function seedDemoData(): Promise<DemoSeedResponse> {
  return backendFetch<DemoSeedResponse>("/demo/seed", { method: "POST" });
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

  const response = await fetch(`${backendUrl}${path}`, {
    ...init,
    headers,
    cache: "no-store"
  });

  if (!response.ok) {
    const message = await response.text();
    throw new ReviewApiError(message || response.statusText, response.status);
  }

  return (await response.json()) as T;
}
