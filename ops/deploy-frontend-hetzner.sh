#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

if [[ ! -f .env.frontend ]]; then
  echo "Missing .env.frontend in $repo_dir" >&2
  exit 1
fi

# NEXT_PUBLIC_* variables are compiled into the Next.js browser bundle. `env_file`
# only configures the runtime container, so it is not sufficient for the build.
docker compose --env-file .env.frontend -f docker-compose.frontend.hetzner.yml up -d --build
