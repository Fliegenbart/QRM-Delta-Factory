import { beforeEach, describe, expect, it, vi } from "vitest";

import canonicalRequirementLibrary from "@/src/data/gmp-general-requirement-library.json";

vi.mock("server-only", () => ({}));

vi.mock("@/src/lib/review-runtime-config", () => ({
  getReviewBackendConfig: () => ({
    backendUrl: "https://qrm-backend.example.test",
    apiKey: "test-api-key",
    tenantId: "tenant_example_pharma",
    requirementSetId: "rset_demo_gmp_qrm_2026_1"
  })
}));

import { createDocumentSet } from "@/src/lib/review-api";

const configuredRequirementSetId = "rset_demo_gmp_qrm_2026_1";
const configuredTenantId = "tenant_example_pharma";

function requirementSet(overrides: Record<string, unknown> = {}) {
  return {
    ...canonicalRequirementLibrary,
    requirement_set_id: configuredRequirementSetId,
    tenant_id: configuredTenantId,
    imported_at: "2026-07-24T00:00:00.000Z",
    imported_by: "user_quality_admin",
    active: true,
    requirements: canonicalRequirementLibrary.requirements.map((requirement) => ({ ...requirement })),
    ...overrides
  };
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" }
  });
}

function requestUrl(input: RequestInfo | URL): string {
  return typeof input === "string" ? input : input.toString();
}

function requestPaths(fetchMock: ReturnType<typeof vi.fn>): string[] {
  return fetchMock.mock.calls.map(([input]) => new URL(requestUrl(input)).pathname);
}

const documentSetInput = {
  declaredDocumentType: "deviation_package",
  declaredProcessArea: "aseptic_filling",
  uploadedBy: "user_qrm_author"
};

describe("createDocumentSet requirement-library refresh", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("imports a canonical library when an active nonlegacy set has the same version but only 23 of 28 requirement IDs", async () => {
    const staleSameVersionSet = requirementSet({
      requirements: canonicalRequirementLibrary.requirements.slice(0, 23)
    });
    const fetchMock = vi.fn(async (input: RequestInfo | URL, _init?: RequestInit) => {
      const url = requestUrl(input);
      if (url.endsWith(`/requirement-sets/${configuredRequirementSetId}/activate`)) {
        return jsonResponse(staleSameVersionSet);
      }
      if (url.endsWith("/requirement-sets/import")) {
        return jsonResponse(requirementSet());
      }
      if (url.endsWith("/document-sets")) {
        return jsonResponse({ document_set_id: "dset_refreshed" });
      }
      throw new Error(`Unexpected backend request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await createDocumentSet(documentSetInput);

    const importCalls = fetchMock.mock.calls.filter(([input]) =>
      requestUrl(input).endsWith("/requirement-sets/import")
    );
    expect(importCalls).toHaveLength(1);

    const importBody = importCalls[0]?.[1]?.body as FormData;
    const importedPayload = JSON.parse(await (importBody.get("file") as Blob).text());
    expect(importedPayload).toMatchObject({
      requirement_set_id: configuredRequirementSetId,
      tenant_id: configuredTenantId,
      version: "2026.2"
    });
  });

  it("imports a canonical library when its requirement IDs match but its version is older", async () => {
    const olderVersionSet = requirementSet({ version: "2026.1" });
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = requestUrl(input);
      if (url.endsWith(`/requirement-sets/${configuredRequirementSetId}/activate`)) {
        return jsonResponse(olderVersionSet);
      }
      if (url.endsWith("/requirement-sets/import")) {
        return jsonResponse(requirementSet());
      }
      if (url.endsWith("/document-sets")) {
        return jsonResponse({ document_set_id: "dset_version_refreshed" });
      }
      throw new Error(`Unexpected backend request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await createDocumentSet(documentSetInput);

    expect(requestPaths(fetchMock)).toEqual([
      `/requirement-sets/${configuredRequirementSetId}/activate`,
      "/requirement-sets/import",
      `/requirement-sets/${configuredRequirementSetId}/activate`,
      "/document-sets"
    ]);
  });

  it("does not import an active canonical library with matching requirement IDs", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = requestUrl(input);
      if (url.endsWith(`/requirement-sets/${configuredRequirementSetId}/activate`)) {
        return jsonResponse(requirementSet());
      }
      if (url.endsWith("/document-sets")) {
        return jsonResponse({ document_set_id: "dset_current" });
      }
      throw new Error(`Unexpected backend request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await createDocumentSet(documentSetInput);

    expect(requestPaths(fetchMock)).toEqual([
      `/requirement-sets/${configuredRequirementSetId}/activate`,
      "/document-sets"
    ]);
  });

  it("activates an inactive canonical library without importing it", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = requestUrl(input);
      if (url.endsWith(`/requirement-sets/${configuredRequirementSetId}/activate`)) {
        return jsonResponse(requirementSet({ active: true }));
      }
      if (url.endsWith("/document-sets")) {
        return jsonResponse({ document_set_id: "dset_reactivated" });
      }
      throw new Error(`Unexpected backend request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await createDocumentSet(documentSetInput);

    expect(requestPaths(fetchMock)).toEqual([
      `/requirement-sets/${configuredRequirementSetId}/activate`,
      "/document-sets"
    ]);
  });

  it("imports and activates a missing canonical library before creating a document set", async () => {
    let activationAttempts = 0;
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = requestUrl(input);
      if (url.endsWith(`/requirement-sets/${configuredRequirementSetId}/activate`)) {
        activationAttempts += 1;
        return activationAttempts === 1
          ? new Response(`RequirementSet ${configuredRequirementSetId} not found`, { status: 404 })
          : jsonResponse(requirementSet());
      }
      if (url.endsWith("/requirement-sets/import")) {
        return jsonResponse(requirementSet());
      }
      if (url.endsWith("/document-sets")) {
        return jsonResponse({ document_set_id: "dset_imported" });
      }
      throw new Error(`Unexpected backend request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await createDocumentSet(documentSetInput);

    expect(requestPaths(fetchMock)).toEqual([
      `/requirement-sets/${configuredRequirementSetId}/activate`,
      "/requirement-sets/import",
      `/requirement-sets/${configuredRequirementSetId}/activate`,
      "/document-sets"
    ]);
  });

  it("does not create a document set when the requirement-library import fails", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = requestUrl(input);
      if (url.endsWith(`/requirement-sets/${configuredRequirementSetId}/activate`)) {
        return new Response(`RequirementSet ${configuredRequirementSetId} not found`, { status: 404 });
      }
      if (url.endsWith("/requirement-sets/import")) {
        return new Response("RequirementSet tenant does not match authenticated tenant", { status: 403 });
      }
      throw new Error(`Unexpected backend request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(createDocumentSet(documentSetInput)).rejects.toMatchObject({ status: 403 });

    expect(requestPaths(fetchMock)).toEqual([
      `/requirement-sets/${configuredRequirementSetId}/activate`,
      "/requirement-sets/import"
    ]);
  });
});
