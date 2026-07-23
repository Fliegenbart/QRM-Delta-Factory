export const reviewRoles = [
  "viewer",
  "reviewer",
  "quality-admin",
  "system-owner"
] as const;

export type ReviewRole = (typeof reviewRoles)[number];

export type ReviewActor = {
  userId: string;
  email?: string;
  role: ReviewRole;
  tenantId: string;
  source: "supabase" | "local-demo";
};

export type ReviewOperation =
  | "read"
  | "create-document-set"
  | "upload-document"
  | "run-pipeline"
  | "submit-review"
  | "import-requirements"
  | "run-regression"
  | "approve-calibration"
  | "delete-document-set";

type UserClaims = {
  id: string;
  email?: string | null;
  app_metadata?: Record<string, unknown> | null;
  user_metadata?: Record<string, unknown> | null;
};

type ReviewAuthEnv = Record<string, string | undefined>;

const roleSet = new Set<string>(reviewRoles);
const permissions: Record<ReviewOperation, readonly ReviewRole[]> = {
  read: reviewRoles,
  "create-document-set": ["reviewer", "quality-admin", "system-owner"],
  "upload-document": ["reviewer", "quality-admin", "system-owner"],
  "run-pipeline": ["reviewer", "quality-admin", "system-owner"],
  "submit-review": ["reviewer", "quality-admin", "system-owner"],
  "import-requirements": ["quality-admin", "system-owner"],
  "run-regression": ["quality-admin", "system-owner"],
  "approve-calibration": ["quality-admin", "system-owner"],
  "delete-document-set": ["system-owner"]
};

export function resolveReviewActorFromClaims(user: UserClaims): ReviewActor | null {
  const claims = user.app_metadata ?? {};
  const role = claims.qrm_role ?? claims.role;
  const tenantId = claims.qrm_tenant_id ?? claims.tenant_id;

  if (
    typeof role !== "string" ||
    !roleSet.has(role) ||
    typeof tenantId !== "string" ||
    tenantId.trim().length === 0
  ) {
    return null;
  }

  return {
    userId: user.id,
    ...(user.email ? { email: user.email } : {}),
    role: role as ReviewRole,
    tenantId: tenantId.trim(),
    source: "supabase"
  };
}

export function authorizeReviewOperation(
  actor: ReviewActor,
  operation: ReviewOperation
): { allowed: true } | { allowed: false; reason: string } {
  return permissions[operation].includes(actor.role)
    ? { allowed: true }
    : { allowed: false, reason: "Insufficient review role for this operation." };
}

export function getLocalReviewFallbackActor(env: ReviewAuthEnv = process.env): ReviewActor | null {
  if (
    env.NODE_ENV === "production" ||
    Boolean(env.VERCEL) ||
    cleanEnvFlag(env.QRM_REVIEW_UI_AUTH_REQUIRED) === "true"
  ) {
    return null;
  }

  return {
    userId: "local-demo-owner",
    role: "system-owner",
    tenantId: cleanEnvValue(env.QRM_BACKEND_TENANT_ID) ?? cleanEnvValue(env.QRM_TENANT_ID) ?? "tenant_example_pharma",
    source: "local-demo"
  };
}

function cleanEnvFlag(value: string | undefined): string | undefined {
  const normalized = value?.trim().toLowerCase();
  return normalized || undefined;
}

function cleanEnvValue(value: string | undefined): string | undefined {
  const normalized = value?.trim();
  return normalized || undefined;
}
