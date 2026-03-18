# Yacht Documentation

This directory contains the repo-local documentation for the current Yacht implementation on the `develop` branch.

## Contents

- [Architecture](./architecture.md)
- [Installation](./installation.md)
- [Agent Deployment](./agent.md)
- [Usage Guide](./usage.md)
- [Operations Runbook](./operations.md)
- [Development Guide](./development.md)
- [CI/CD and Image Publishing](./ci-cd.md)
- [Security Guide](./security.md)

## Scope

These docs describe the code that exists in this repository today, including:

- the main Yacht web UI and API container
- the separate `yacht-agent` container for remote Docker hosts
- GitHub Actions workflows that verify, build, and publish both images to GHCR

## Current Agent Support

Agent-managed hosts currently support:

- host registration
- heartbeat and inventory sync
- read-only container, image, volume, and network inventory in the main UI/API
- queued container actions: `start`, `stop`, `restart`, `kill`, and `remove`

Agent-managed hosts do not yet fully support:

- deploy/update through the agent
- live logs and stats through the agent
- compose job execution through the agent
- image, volume, and network mutation through the agent
