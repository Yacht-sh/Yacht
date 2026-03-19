# Security Guide

## Current Security Controls

Backend settings include:

- `SECURE_COOKIES`
- `ENABLE_SECURITY_HEADERS`
- `ENABLE_HTTPS_REDIRECT`
- `EXPOSE_API_DOCS`
- `HSTS_SECONDS`
- `TRUSTED_HOSTS`
- `AGENT_ENROLLMENT_TOKEN`

These are defined in:

- `backend/api/settings.py`

## Reverse Proxy and Headers

The bundled `nginx.conf` sets:

- `server_tokens off`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`
- `Permissions-Policy`
- `Cross-Origin-Opener-Policy`
- `Cross-Origin-Resource-Policy`
- request size limit via `client_max_body_size`

The FastAPI app also sets security headers through middleware.

## Recommended Production Settings

Set these in production unless you have a specific reason not to:

```bash
SECURE_COOKIES=true
ENABLE_SECURITY_HEADERS=true
ENABLE_HTTPS_REDIRECT=true
EXPOSE_API_DOCS=false
HSTS_SECONDS=31536000
TRUSTED_HOSTS=your.domain.example
```

Also set a strong enrollment token if you use agents:

```bash
AGENT_ENROLLMENT_TOKEN=replace-with-a-long-random-secret
```

## Authentication Notes

- `DISABLE_AUTH=false` is the recommended default
- only disable auth if another control plane is enforcing access in front of Yacht

## Agent Security Model

The current agent model is safer than exposing remote Docker APIs directly because:

- the remote host initiates the outbound connection
- the server does not require direct inbound Docker API access to the remote host
- jobs are constrained to known job types instead of arbitrary shell execution

Current agent trust model:

- shared enrollment token for first registration
- issued long-lived agent token for subsequent authenticated traffic

This is sufficient for initial development, but it is not the final security model. Stronger future options include:

- token rotation
- explicit host approval
- mTLS
- scoped per-agent permissions

## Audit and Static Analysis

Current CI checks include:

- `npm audit` for frontend runtime dependencies
- `bandit` for backend and agent Python code
- `pip-audit` for backend and agent Python dependencies

## Known Risk Areas

- the frontend remains on Vue 2 and Vuetify 2
- one frontend advisory is allowlisted because the non-breaking fix path is not available in the current stack
- agent job execution currently supports only a small set of known Docker operations, which is intentional
