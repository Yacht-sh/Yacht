# Development Guide

## Repo Layout

- `frontend/`: Vue/Vuetify frontend
- `backend/`: FastAPI backend and database models
- `agent/`: standalone agent service
- `.github/workflows/`: CI/CD pipelines
- `docs/`: repo-local documentation

## Local Build and Run

### Main Stack

```bash
docker compose up --build
```

### Frontend

Common commands:

```bash
cd frontend
npm ci --legacy-peer-deps --no-audit --no-fund
npm run lint
npm run build
```

### Backend

Common commands:

```bash
python3 -m compileall backend
bandit -q -r backend/api
```

### Agent

Common commands:

```bash
python3 -m compileall agent
bandit -q -r agent
```

## Dependency Notes

Frontend:

- uses Vue 2 and Vuetify 2
- some audit/deprecation issues are temporarily tolerated because the current stack does not have a non-breaking upgrade path

Backend:

- Python 3.11 is the CI target
- system packages are required for `mysqlclient` and some compiled dependencies

## Build Artifacts

Main image build stages:

1. `node:20-bookworm-slim` builds the frontend
2. `python:3.11-slim` builds the runtime image

Agent image build:

- separate `agent/Dockerfile`
- publishes as `yacht-agent`

## Current Implementation Boundaries

Implemented on agent hosts:

- registration
- heartbeat
- inventory sync
- container actions via queued jobs

Still pending:

- deploy/update jobs
- compose jobs
- logs/stats streaming
- resource mutation jobs

## Coding Expectations

When extending the agent model, keep these rules:

- prefer explicit supported job types over generic remote execution
- keep agent connectivity outbound from the remote host to the server
- avoid exposing raw Docker APIs unless directly intended
- update repo-local docs when behavior changes
