# Yacht Wiki

This wiki folder captures the current operational state of the `develop` branch.

It is intentionally practical. These pages document the branch flow, CI checks, dependency compatibility rules, and image publishing prerequisites that are easy to lose during day-to-day work.

## Pages

- [Development And Release Flow](./Development-And-Release-Flow.md)
- [Verification Runbook](./Verification-Runbook.md)
- [Dependency Compatibility](./Dependency-Compatibility.md)
- [Image Publishing And GHCR](./Image-Publishing-And-GHCR.md)

## Current Snapshot

- default branch: `master`
- integration branch: `develop`
- main application image platforms: `linux/amd64`, `linux/arm64`
- frontend stack: Vue 2 + Vuetify 2
- backend API stack: FastAPI with Pydantic v1 compatibility preserved

## Why This Exists

Recent work on `develop` merged a large set of dependency and workflow updates. Some of those updates were compatible as-is, and some required explicit pins to keep the codebase working. The pages in this folder record those decisions so future dependency and CI work starts from the current known-good state instead of rediscovering it.
