# Image Publishing And GHCR

## Current Workflow

The image publish workflow is defined in [`../.github/workflows/build.yml`](../.github/workflows/build.yml).

Main points:

- runs on pushes to `master`
- verifies frontend, backend, and agent before publishing
- publishes the main Yacht image for:
  - `linux/amd64`
  - `linux/arm64`
- does not publish a separate agent image in this workflow

## Current Tag Behavior

On each push to `master`:

- main image channel tag: `latest`
- version tag: `sha-<12-char-commit-sha>`
- additional short SHA tag emitted by metadata action

## GHCR Login Behavior

The workflow logs into GHCR with:

- `github.actor` / `GITHUB_TOKEN`

The workflow prints the auth context before push to make troubleshooting explicit.

## GHCR Preflight Checks

Before `docker/build-push-action`, the workflow performs preflight checks:

1. registry-level auth check against `https://ghcr.io/v2/`
2. package access check against `https://ghcr.io/v2/<owner>/yacht/tags/list?n=1`

Expected package check responses:

- `200`: package exists and token can read it
- `404`: package does not exist yet (first push path), credentials still acceptable

Failing responses (`401`/`403`) are surfaced early with remediation guidance so failures are easier to distinguish from Docker Buildx errors.

## Known GHCR Failure Mode

If the build succeeds but push fails with a blob `HEAD` request returning `403 Forbidden`, the problem is usually package permission scope, not Docker build content.

Typical causes:

- the existing `ghcr.io/yacht-sh/yacht` package is not linked to the `Yacht-sh/Yacht` repository
- the repository has not been granted package access
- the workflow token does not have effective package permissions for that existing package namespace

## What To Check In GitHub

1. Open the `ghcr.io/yacht-sh/yacht` package settings.
2. Ensure the `Yacht-sh/Yacht` repository has access to the package.
3. If using a PAT, ensure it has:
   - `read:packages`
   - `write:packages`
4. If the org uses SSO, authorize the token for the org.

Note: this workflow currently uses `GITHUB_TOKEN` for push and preflight. If your org policy requires a PAT for package publish, update the workflow auth step and preflight env accordingly.

## Platform Notes

The main image publish path no longer targets `linux/arm/v7`.

Reason:

- that path required unsupported dependency build work for the current branch
- `linux/amd64` and `linux/arm64` are the current maintained publish targets
