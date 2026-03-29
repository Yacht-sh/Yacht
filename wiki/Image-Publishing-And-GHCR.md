# Image Publishing And GHCR

## Current Workflow

The image publish workflow is defined in [`../.github/workflows/build.yml`](../.github/workflows/build.yml).

Main points:

- runs on pushes to `master` and `develop`
- verifies frontend, backend, and agent before publishing
- publishes the main Yacht image for:
  - `linux/amd64`
  - `linux/arm64`
- publishes the agent image separately

## Current Tag Behavior

On `master`:

- main image channel tag: `latest`
- version tag: UTC timestamp

On `develop`:

- main image channel tag: `dev-latest`
- version tag: `dev-<timestamp>`

## GHCR Login Behavior

The workflow logs into GHCR with:

- `GHCR_USERNAME` / `GHCR_TOKEN` if they are configured
- otherwise `github.actor` / `GITHUB_TOKEN`

## Known GHCR Failure Mode

If the build succeeds but push fails with a blob `HEAD` request returning `403 Forbidden`, the problem is usually package permission scope, not Docker build content.

Typical causes:

- the existing `ghcr.io/yacht-sh/yacht` package is not linked to the `Yacht-sh/Yacht` repository
- the repository has not been granted package access
- the fallback `GITHUB_TOKEN` does not have the effective package permissions needed for that existing package namespace
- a PAT is being used without the required `read:packages` and `write:packages` scopes

## What To Check In GitHub

1. Open the `ghcr.io/yacht-sh/yacht` package settings.
2. Ensure the `Yacht-sh/Yacht` repository has access to the package.
3. If using a PAT, ensure it has:
   - `read:packages`
   - `write:packages`
4. If the org uses SSO, authorize the token for the org.

## Platform Notes

The main image publish path no longer targets `linux/arm/v7`.

Reason:

- that path required unsupported dependency build work for the current branch
- `linux/amd64` and `linux/arm64` are the current maintained publish targets
