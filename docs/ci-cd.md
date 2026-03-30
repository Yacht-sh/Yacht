# CI/CD and Image Publishing

## Registries

Images are published to GitHub Container Registry.

Main image:

- `ghcr.io/<owner>/yacht`

Agent image:

- `ghcr.io/<owner>/yacht-agent`

## Workflow

Current image publishing uses:

- `.github/workflows/build.yml`

Trigger:

- push to `develop`
- push to `master`
- manual dispatch

## Verification Stages

Before publishing, the workflow verifies:

- frontend install
- frontend lint
- frontend runtime audit
- frontend build
- backend dependency install
- backend compile
- backend Bandit scan
- backend pip-audit
- agent dependency install
- agent compile
- agent Bandit scan
- agent pip-audit

## Publish Tags

On `develop`:

- `yacht:dev-latest`
- `yacht:dev-<YYYYMMDD-HHMMSS>`
- `yacht-agent:dev-latest`
- `yacht-agent:dev-<YYYYMMDD-HHMMSS>`

On `master`:

- `yacht:latest`
- `yacht:<YYYYMMDD-HHMMSS>`
- `yacht-agent:latest`
- `yacht-agent:<YYYYMMDD-HHMMSS>`

## Supply Chain Metadata

Current Docker build jobs enable:

- `sbom: true`
- `provenance: mode=max`

## Authentication

The workflows log in to GHCR with:

- `GHCR_USERNAME` and `GHCR_TOKEN` when provided
- otherwise `github.actor` and `GITHUB_TOKEN`

There is no Docker Hub publishing path in the current repo configuration.
