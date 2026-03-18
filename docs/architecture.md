# Architecture

## Main Components

Yacht is split into two runtime roles.

### 1. Main Yacht Application

The main Yacht application is the control plane. It provides:

- the web UI
- the FastAPI backend
- authentication
- the database
- host inventory and selection
- template and compose management
- agent registration and job queueing

Main image:

- `ghcr.io/<owner>/yacht`

Primary files:

- `Dockerfile`
- `backend/api/main.py`
- `frontend/`
- `nginx.conf`

### 2. Yacht Agent

The agent runs on a remote Docker host and connects back to the main Yacht server.

The agent:

- mounts the local Docker socket
- registers with the main Yacht server using an enrollment token
- sends heartbeat data
- syncs Docker inventory back to the main Yacht server
- polls for queued jobs
- executes supported jobs locally
- returns job results and refreshed inventory

Agent image:

- `ghcr.io/<owner>/yacht-agent`

Primary files:

- `agent/Dockerfile`
- `agent/main.py`
- `agent/docker-compose.yaml`

## Host Connection Types

The backend currently recognizes these host types:

- `local`: the main Yacht container manages its own local Docker socket
- `docker_api`: Yacht talks directly to a remote Docker API endpoint
- `agent`: a remote `yacht-agent` connects back to Yacht and executes jobs locally

## Current Agent Data Flow

### Registration

1. The agent starts.
2. The agent reads `YACHT_SERVER_URL` and `YACHT_AGENT_ENROLLMENT_TOKEN`.
3. The agent sends `POST /api/agents/register`.
4. The server creates or updates the matching `Host` and `Agent` records.
5. The server returns a long-lived agent token.
6. The agent stores that token in `/config/agent-state.json`.

### Heartbeat and Inventory Sync

1. The agent sends `POST /api/agents/heartbeat` on the configured interval.
2. The agent sends `POST /api/agents/sync` with local Docker inventory.
3. The main Yacht server stores the inventory on the matching `Agent` record.
4. Main app views for apps and resources can read the cached inventory for agent-managed hosts.

### Job Execution

1. The main Yacht server queues a job in the `agent_jobs` table.
2. The agent polls `GET /api/agents/jobs/next`.
3. The server returns the next pending job for that agent.
4. The agent executes the job locally against the Docker socket.
5. The agent posts the result to `POST /api/agents/jobs/{job_id}/result`.
6. The server marks the job complete and updates cached inventory if the result includes it.

## Current Agent Job Types

Implemented:

- `container_action`

Supported container actions:

- `start`
- `stop`
- `restart`
- `kill`
- `remove`

Not yet implemented:

- deploy jobs
- update jobs
- compose jobs
- log streaming jobs
- stats jobs
- resource mutation jobs

## Database Notes

The backend creates tables on startup using SQLAlchemy metadata.

Relevant models:

- `hosts`
- `agents`
- `agent_jobs`
- other existing Yacht application tables

Because tables are created from metadata at app startup, adding new models changes runtime schema expectations immediately. In production, treat model changes carefully and prefer explicit migration work if this project moves toward stricter schema management.
