# Agent Deployment

## Purpose

Use `yacht-agent` when you want a remote Docker host to be managed by a central Yacht server without exposing the remote Docker API directly.

## Required Environment Variables

- `YACHT_SERVER_URL`: the base URL of the main Yacht server, with or without `/api`
- `YACHT_AGENT_ENROLLMENT_TOKEN`: shared token matching `AGENT_ENROLLMENT_TOKEN` on the main Yacht server

## Optional Environment Variables

- `YACHT_AGENT_NAME`: logical host name shown in Yacht; defaults to the system hostname
- `YACHT_AGENT_VERIFY_SSL`: `true` or `false`; default `true`
- `YACHT_AGENT_HEARTBEAT_INTERVAL`: heartbeat interval in seconds; default `30`
- `YACHT_AGENT_JOB_POLL_INTERVAL`: job polling interval in seconds; default `5`
- `YACHT_AGENT_VERSION`: manual version override; default `0.1.0`
- `YACHT_AGENT_LOG_LEVEL`: log level; default `INFO`
- `YACHT_AGENT_STATE`: state file path; default `/config/agent-state.json`

## Docker Compose Example

The repo includes `agent/docker-compose.yaml`.

Example:

```yaml
services:
  yacht-agent:
    image: ghcr.io/yacht-sh/yacht-agent:dev-latest
    container_name: yacht-agent
    restart: unless-stopped
    environment:
      YACHT_SERVER_URL: https://yacht.example.com
      YACHT_AGENT_ENROLLMENT_TOKEN: replace-with-shared-enrollment-token
      YACHT_AGENT_NAME: remote-docker-host
      YACHT_AGENT_VERIFY_SSL: "true"
      YACHT_AGENT_HEARTBEAT_INTERVAL: "30"
      YACHT_AGENT_JOB_POLL_INTERVAL: "5"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - yacht-agent-config:/config

volumes:
  yacht-agent-config:
```

Start the agent:

```bash
docker compose -f agent/docker-compose.yaml up -d
```

## Registration Flow

1. Set `AGENT_ENROLLMENT_TOKEN` on the main Yacht server.
2. Set the same value as `YACHT_AGENT_ENROLLMENT_TOKEN` on the agent.
3. Start the agent container.
4. The agent registers with the main Yacht server.
5. The host appears in Yacht as an `agent` connection type.

## Agent Logs

View the running agent logs:

```bash
docker logs -f yacht-agent
```

Successful startup should show:

- registration accepted
- heartbeat accepted
- inventory sync accepted

## Agent State File

The agent stores its issued token and server-linked identifiers in:

- `/config/agent-state.json`

If you need to force re-registration, remove that state and restart the container.

Example:

```bash
docker exec yacht-agent rm -f /config/agent-state.json
docker restart yacht-agent
```

## Current Agent Capabilities

The agent currently supports:

- registration
- heartbeat
- inventory sync
- queued container actions

The agent does not yet fully support:

- compose execution
- deploy jobs
- log streaming
- stats streaming
- image, volume, and network mutation
