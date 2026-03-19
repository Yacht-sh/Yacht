# Operations Runbook

## Common Commands

### Start Local Development Stack

```bash
docker compose up -d --build
```

### Stop Local Development Stack

```bash
docker compose down
```

### Reset Local State

```bash
docker compose down
rm -rf ./.local/yacht-config
docker compose up --build
```

### View Main Yacht Logs

```bash
docker logs -f yacht-local
```

### View Agent Logs

```bash
docker logs -f yacht-agent
```

## Health Checks

### Main Application

At startup, the backend should show:

- Uvicorn starting
- application startup complete
- local host creation or validation
- secret key creation or reuse

### Agent

A healthy agent should show:

- registration accepted
- heartbeat accepted
- inventory sync accepted

## Troubleshooting

### Login Returns 400

Likely causes:

- the database already exists with different credentials
- you are using credentials that do not match the persistent database

Reset local state if you want the compose defaults reapplied.

### `/auth/me` and `/auth/refresh` Return 401 Before Login

That is expected before authentication.

### Docker Build Fails on macOS Keychain Access

If Docker cannot access stored credentials in a non-interactive session, you may need to unlock the keychain or reconfigure Docker credential storage.

This is a local environment issue, not a Yacht application bug.

### Agent Repeatedly Re-registers

Check:

- `YACHT_AGENT_ENROLLMENT_TOKEN`
- `AGENT_ENROLLMENT_TOKEN` on the main Yacht server
- reachability of `YACHT_SERVER_URL`
- whether the stored `/config/agent-state.json` is valid for the current server

### Agent Host Shows Stale Inventory

Check:

- agent logs for heartbeat and sync failures
- whether the agent can still reach the server
- whether the agent can talk to the local Docker socket

### Agent Actions Return Timeout

Current server behavior waits for the queued job to complete. If it times out:

- inspect agent logs
- confirm the agent is polling jobs
- confirm the target container exists on the remote host

## Backups

The built-in SQLite database lives at:

- `/config/data.sqlite`

Back up `/config` for basic state preservation.

If using an external SQL database, follow that platform's normal backup procedures.
