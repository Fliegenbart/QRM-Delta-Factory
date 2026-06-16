type ReviewAuthEnv = Record<string, string | undefined>;

const truthyEnvValues = new Set(["1", "true", "yes", "on"]);
const falsyEnvValues = new Set(["0", "false", "no", "off"]);

function isSamePathOrChild(pathname: string, prefix: string) {
  return pathname === prefix || pathname.startsWith(`${prefix}/`);
}

function cleanEnvFlag(value: string | undefined) {
  return value?.trim().toLowerCase();
}

export function isProtectedReviewPath(pathname: string) {
  return (
    isSamePathOrChild(pathname, "/review-ui") ||
    isSamePathOrChild(pathname, "/api/review-ui")
  );
}

export function isProtectedReviewApiPath(pathname: string) {
  return isSamePathOrChild(pathname, "/api/review-ui");
}

export function isReviewAuthRequired(env: ReviewAuthEnv = process.env) {
  const explicitFlag = cleanEnvFlag(env.QRM_REVIEW_UI_AUTH_REQUIRED);
  if (explicitFlag && truthyEnvValues.has(explicitFlag)) return true;
  if (explicitFlag && falsyEnvValues.has(explicitFlag)) return false;

  return env.NODE_ENV === "production" || Boolean(env.VERCEL);
}
