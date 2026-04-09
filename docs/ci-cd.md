# CI/CD and Main Image Publishing

## Registries

Images are published to GitHub Container Registry.

Main image:

- `ghcr.io/<owner>/yacht`

## Workflow

Current image publishing uses:

- `.github/workflows/build.yml`

Trigger:

- push to `master`

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

On each push to `master`:

- `yacht:latest`
- `yacht:sha-<12-char-commit-sha>`

## Target Platforms

The published main image targets:

- `linux/amd64`
- `linux/arm64`

The workflow does not publish `arm/v7`.

## Supply Chain Metadata

Current Docker build jobs enable:

- `sbom: true`
- `provenance: mode=max`

## Authentication

The workflows log in to GHCR with:

- `GHCR_USERNAME` and `GHCR_TOKEN` when provided
- otherwise `github.actor` and `GITHUB_TOKEN`

There is no Docker Hub publishing path in the current repo configuration, and the workflow no longer publishes a separate agent image.
