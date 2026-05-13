const DEFAULT_BACKEND_URL = "http://localhost:8000";
const DEFAULT_TENANT_ID = "tenant_example_pharma";
const DEFAULT_REQUIREMENT_SET_ID = "rset_example_gmp_qrm_2026_1";

export function cleanEnvValue(value: string | undefined): string | undefined {
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

export function getReviewBackendConfig(
  env: Record<string, string | undefined> = process.env
) {
  return {
    backendUrl: cleanEnvValue(env.QRM_BACKEND_URL) ?? DEFAULT_BACKEND_URL,
    apiKey: cleanEnvValue(env.QRM_BACKEND_API_KEY),
    tenantId:
      cleanEnvValue(env.QRM_BACKEND_TENANT_ID) ??
      cleanEnvValue(env.QRM_TENANT_ID) ??
      DEFAULT_TENANT_ID,
    requirementSetId:
      cleanEnvValue(env.QRM_DEFAULT_REQUIREMENT_SET_ID) ??
      DEFAULT_REQUIREMENT_SET_ID
  };
}
