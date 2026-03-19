# CI/CD and Image Publishing

## Registries

Images are published to GitHub Container Registry.

Main image:

- `ghcr.io/<owner>/yacht`

Agent image:

- `ghcr.io/<owner>/yacht-agent`

## Branch Workflows

### Develop

Workflow:

- `.github/workflows/docker-image.yml`

Trigger:

- push to `develop`
- manual dispatch

Verification stages:

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

Publish stages:

- `yacht:dev-latest`
- `yacht:<YYYYMMDD-HHMMSS>`
- `yacht-agent:dev-latest`
- `yacht-agent:<YYYYMMDD-HHMMSS>`

### Master

Workflow:

- `.github/workflows/build.yml`

Trigger:

- push to `master`
- manual dispatch

Publish stages:

- `yacht:latest`
- `yacht:<YYYYMMDD-HHMMSS>`
- `yacht-agent:latest`
- `yacht-agent:<YYYYMMDD-HHMMSS>`

## Manual Builds

Workflow:

- `.github/workflows/manual-build.yml`

This workflow can build either image from a provided ref or tag and publish it to GHCR.

## Supply Chain Metadata

Current Docker build jobs enable:

- `sbom: true`
- `provenance: mode=max`

## Authentication

The workflows publish with:

- `GITHUB_TOKEN`

There is no Docker Hub publishing path in the current repo configuration.
