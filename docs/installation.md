# Installation

## Requirements

Main Yacht host requirements:

- Linux host
- Docker Engine
- access to `/var/run/docker.sock`

Remote agent host requirements:

- Linux host
- Docker Engine
- ability to reach the main Yacht server over HTTP or HTTPS

## Local Development Compose

The repository includes a local compose file at `docker-compose.yaml`.

Start the local stack:

```bash
docker compose up --build
```

Run detached:

```bash
docker compose up -d --build
```

Stop it:

```bash
docker compose down
```

Current local compose defaults in this repo:

- URL: `http://localhost:8000`
- admin email: `admin@example.local`
- admin password: `changeme123`

Those credentials come from `docker-compose.yaml`. If you change them after first boot, they do not overwrite an existing database.

## Reset Local State

The local compose file persists app state in:

- `./.local/yacht-config`

To reset the local database and recreate the default admin user:

```bash
docker compose down
rm -rf ./.local/yacht-config
docker compose up --build
```

After reset, the startup logs should include the default user creation path.

## Main Yacht Container Deployment

The main container expects a writable `/config` volume and Docker socket access.

Basic example:

```bash
docker run -d \
  --name yacht \
  --restart unless-stopped \
  -p 8000:8000 \
  -e SECRET_KEY=replace-me \
  -e ADMIN_EMAIL=admin@yacht.local \
  -e ADMIN_PASSWORD=pass \
  -e AGENT_ENROLLMENT_TOKEN=replace-with-shared-token \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v yacht-config:/config \
  ghcr.io/<owner>/yacht:latest
```

## Additional Compose Examples

The repo also includes additional compose examples under:

- `Docker-Compose-Files/docker-compose-MAC-Linux.yml`
- `Docker-Compose-Files/docker-compose-w-traefik.yml`

Review those files before use. They are examples, not guarantees of current production readiness.

## Traefik Compose Notes

The current Traefik example assumes:

- image: `ghcr.io/yacht-sh/yacht:latest`
- internal Yacht service port: `8000`
- reverse proxy target protocol: `http`
- external Traefik Docker network named `web`

Why port `8000` is correct:

- the container starts FastAPI behind the bundled `nginx.conf`
- nginx listens on `8000` inside the container
- Traefik should route to that internal nginx listener, not directly to uvicorn

Before using the example, replace:

- `yacht.domain.tld`
- `domain.tld`
- `dns` certificate resolver name
- `./config` if you want a different persistent config path
