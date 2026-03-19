# Usage Guide

## Logging In

For local repo compose, the default credentials are currently:

- email: `admin@example.local`
- password: `changeme123`

In other deployments, use the values you set through `ADMIN_EMAIL` and `ADMIN_PASSWORD` on first startup.

## Managing Hosts

### Local Host

The main Yacht server creates a `local` host record for the Docker socket available to the main container.

### Docker API Hosts

You can manually add direct Docker API hosts from the Hosts settings page.

Expected fields:

- host name
- Docker host URL such as `tcp://192.168.1.50:2375`
- whether it should be the default host

### Agent Hosts

You do not manually create agent hosts in the Hosts form.

Agent-managed hosts appear automatically when a `yacht-agent` container registers back to the main Yacht server.

## Switching Hosts

The frontend stores the selected host ID in browser local storage. The top bar host selector controls which host the UI is querying.

## Container Management

For local and Docker API hosts, existing Yacht behavior applies.

For agent-managed hosts, current support includes:

- listing containers
- viewing container details from cached inventory
- starting a container
- stopping a container
- restarting a container
- killing a container
- removing a container

## Template and Compose Notes

Template and compose workflows remain part of the main Yacht application, but agent-backed compose execution is not fully implemented yet.

Treat compose management on agent hosts as incomplete until that job path is added.

## API Routing Notes

Most frontend host-aware routes include `host_id` as a query parameter.

Examples:

```text
/api/apps/?host_id=2
/api/apps/actions/nginx/start?host_id=2
/api/resources/images?host_id=2
```
