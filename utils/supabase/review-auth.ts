type ReviewAuthEnv = Record<string, string | undefined>;

const truthyEnvValues = new Set(["1", "true", "yes", "on"]);

function isSamePathOrChild(pathname: string, prefix: string) {
  return pathname === prefix || pathname.startsWith(`${prefix}/`);
}

function cleanEnvFlag(value: string | undefined) {
  return value?.trim().toLowerCase();
}

export function isProtectedReviewPath(pathname: string) {
  if (isSamePathOrChild(pathname, "/review-ui/demo")) return false;
  return (
    isSamePathOrChild(pathname, "/review-ui") ||
    isSamePathOrChild(pathname, "/api/review-ui")
  );
}

export function isProtectedReviewApiPath(pathname: string) {
  return isSamePathOrChild(pathname, "/api/review-ui");
}

export function isReviewAuthRequired(env: ReviewAuthEnv = process.env) {
  // Fail secure: production deployments are always protected. A leftover
  // QRM_REVIEW_UI_AUTH_REQUIRED="false" (e.g. copied from .env.example)
  // must not expose the review workspace on a real deployment.
  if (env.NODE_ENV === "production" || Boolean(env.VERCEL)) return true;

  const explicitFlag = cleanEnvFlag(env.QRM_REVIEW_UI_AUTH_REQUIRED);
  if (explicitFlag && truthyEnvValues.has(explicitFlag)) return true;
  return false;
}
