# Verification Runbook

This page records the checks that match the current repository workflows and the local commands that were used to verify the current `develop` branch.

## CI Workflow Summary

The main build workflow is [`../.github/workflows/build.yml`](../.github/workflows/build.yml).

It currently runs:

- frontend install, lint, audit, and production build
- backend dependency install, `pip check`, `compileall`, Bandit, and `pip-audit`
- agent dependency install, `compileall`, Bandit, and `pip-audit`
- image publishing after verification succeeds

## Frontend Local Verification

Use Docker to avoid host Node drift:

```bash
docker run --rm -v "$PWD/frontend:/app" -w /app node:20-bookworm-slim \
  bash -lc 'npm ci --legacy-peer-deps --no-audit --no-fund && npm run lint && npm run build'
```

Expected result:

- `npm run lint` may emit warnings
- the command should still exit successfully
- `npm run build` should complete and produce `frontend/dist`

## Backend Local Verification

Fast local checks:

```bash
python3 -m compileall backend
bandit -q -r backend/api
```

Containerized dependency audit with native build packages:

```bash
docker run --rm -v "$PWD/backend:/app" -w /app python:3.11-slim \
  bash -lc 'apt-get update >/tmp/apt.log && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential pkg-config libffi-dev libssl-dev libpq-dev \
      default-libmysqlclient-dev libjpeg-dev zlib1g-dev libyaml-dev >/tmp/apt-install.log && \
    python -m pip install --no-cache-dir pip-audit >/tmp/pip-audit-install.log && \
    pip-audit -r requirements.txt --progress-spinner=off'
```

Expected result:

- `No known vulnerabilities found`

## Agent Local Verification

The CI workflow verifies the agent separately. Follow the same pattern as the backend:

- install `agent/requirements.txt`
- run `python -m compileall agent`
- run `bandit -q -r agent`
- run `pip-audit -r agent/requirements.txt --progress-spinner=off`

## When Verification Fails

- fix the dependency or workflow problem first
- do not document a change as current behavior until the branch verifies cleanly
- if a dependency bump is incompatible with the current codebase, pin it back to the last known-good version and document why in the compatibility page
