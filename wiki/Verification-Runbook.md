# Verification Runbook

This page records the checks used by the current repository workflows and the corresponding local verification commands.

## CI Workflow Summary

The main workflow is [`../.github/workflows/ci.yml`](../.github/workflows/ci.yml).

It currently runs a code-quality job that:

- installs backend dependencies with Python 3.11 and syntax-checks selected backend modules
- installs frontend dependencies and runs the production build (CI does not run frontend lint)
- runs Bandit and a non-blocking backend `pip-audit`
- builds and publishes the image, then runs non-blocking Trivy scans

## Frontend Local Verification

Use Docker to avoid host Node drift:

```bash
docker run --rm -v "$PWD/frontend:/app" -w /app node:26-bookworm-slim \
  bash -lc 'npm ci --legacy-peer-deps --no-audit --no-fund && npm run lint && npm run build'
```

Expected result:

- `npm run lint` uses the ESLint 10 flat config and Vue 2 preset; it can emit warnings but should exit successfully
- `npm run build` should complete and produce `frontend/dist`

## Backend Local Verification

Fast local checks:

```bash
python3 -m compileall backend
bandit -q -r backend/api
```

Containerized dependency audit with native build packages:

```bash
docker run --rm -v "$PWD/backend:/app" -w /app python:3.15-slim \
  bash -lc 'apt-get update >/tmp/apt.log && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential pkg-config libffi-dev libssl-dev libpq-dev \
      default-libmysqlclient-dev libjpeg-dev zlib1g-dev libyaml-dev >/tmp/apt-install.log && \
    python -m pip install --no-cache-dir pip-audit >/tmp/pip-audit-install.log && \
    pip-audit -r requirements.txt --progress-spinner=off'
```

Expected result:

- `No known vulnerabilities found`

## When Verification Fails

- fix the dependency or workflow problem first
- do not document a change as current behavior until the branch verifies cleanly
- if a dependency bump is incompatible with the current codebase, pin it back to the last known-good version and document why in the compatibility page
