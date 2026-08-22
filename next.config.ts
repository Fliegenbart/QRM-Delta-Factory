import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {},
  // The Ringversuch pages read goldstandard_pharmaqrm/runs/*/results.json
  // from disk at request time. Next's file tracing only bundles files a
  // route imports, so on Vercel the directory was simply absent and the
  // proof page answered {"runs": []} -- the numbers we pitch with were
  // never visible on the customer-facing site. Both readers are listed so
  // a future route cannot silently regress by reading the data elsewhere.
  outputFileTracingIncludes: {
    "/[section]": ["./goldstandard_pharmaqrm/runs/**/results.json"],
    "/api/ringversuch": ["./goldstandard_pharmaqrm/runs/**/results.json"]
  }
};

export default nextConfig;
