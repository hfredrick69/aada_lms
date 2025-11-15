#!/usr/bin/env bash
set -euo pipefail

# Run Playwright tests inside the official container so Chrome can launch
# and still reach the host-based Docker services (backend + portals).

PLAYWRIGHT_IMAGE="${PLAYWRIGHT_IMAGE:-mcr.microsoft.com/playwright:v1.56.1-jammy}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Default host for hitting services from inside the container
DEFAULT_HOST="${E2E_HOST:-host.docker.internal}"

# Compose URLs that the tests expect. Callers can override if needed.
ADMIN_URL="${ADMIN_PORTAL_URL:-http://${DEFAULT_HOST}:5173}"
STUDENT_URL="${STUDENT_PORTAL_URL:-http://${DEFAULT_HOST}:5174}"
API_ORIGIN="${PLAYWRIGHT_API_ORIGIN:-http://${DEFAULT_HOST}:8000}"
API_BASE_URL="${PLAYWRIGHT_API_BASE_URL:-${API_ORIGIN}/api}"

docker run --rm \
  --add-host=host.docker.internal:host-gateway \
  -e E2E_HOST="${DEFAULT_HOST}" \
  -e ADMIN_PORTAL_URL="${ADMIN_URL}" \
  -e STUDENT_PORTAL_URL="${STUDENT_URL}" \
  -e PLAYWRIGHT_API_ORIGIN="${API_ORIGIN}" \
  -e PLAYWRIGHT_API_BASE_URL="${API_BASE_URL}" \
  -e HOME=/tmp \
  -v "${PROJECT_ROOT}":"${PROJECT_ROOT}" \
  -w "${PROJECT_ROOT}" \
  "${PLAYWRIGHT_IMAGE}" \
  npx playwright test "$@"
