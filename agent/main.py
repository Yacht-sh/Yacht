import json
import logging
import os
import socket
import time
from pathlib import Path

import docker
import requests


STATE_PATH = Path(os.environ.get("YACHT_AGENT_STATE", "/config/agent-state.json"))
HEARTBEAT_INTERVAL = int(os.environ.get("YACHT_AGENT_HEARTBEAT_INTERVAL", "30"))
JOB_POLL_INTERVAL = int(os.environ.get("YACHT_AGENT_JOB_POLL_INTERVAL", "5"))
VERIFY_SSL = os.environ.get("YACHT_AGENT_VERIFY_SSL", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
SUPPORTED_CONTAINER_ACTIONS = {"start", "stop", "restart", "remove", "kill"}
SUPPORTED_COMPOSE_ACTIONS = {"up", "down", "pull"}

logging.basicConfig(
    level=os.environ.get("YACHT_AGENT_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("yacht-agent")


def _normalize_server_url() -> str:
    server = os.environ.get("YACHT_SERVER_URL", "").strip().rstrip("/")
    if not server:
        raise RuntimeError("YACHT_SERVER_URL is required.")
    if server.endswith("/api"):
        return server
    return f"{server}/api"


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.warning("Ignoring unreadable state file: %s", exc)
        return {}


def _save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def _clear_registration(state: dict):
    state.pop("agent_token", None)
    state.pop("agent_id", None)
    state.pop("host_id", None)
    _save_state(state)


def _agent_name() -> str:
    return os.environ.get("YACHT_AGENT_NAME", socket.gethostname())


def _docker_client():
    docker_host = os.environ.get("DOCKER_HOST")
    if docker_host:
        client = docker.DockerClient(base_url=docker_host)
    else:
        client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
    client.ping()
    return client


def _capabilities() -> dict[str, bool]:
    return {
        "containers": True,
        "images": True,
        "volumes": True,
        "networks": True,
        "compose": True,
        "host_stats": True,
    }


def _registration_payload(client):
    version = client.version()
    return {
        "name": _agent_name(),
        "hostname": socket.gethostname(),
        "version": os.environ.get("YACHT_AGENT_VERSION", "0.1.0"),
        "docker_version": version.get("Version"),
        "capabilities": _capabilities(),
    }


def _host_stats() -> dict | None:
    try:
        with open("/proc/stat", "r", encoding="utf-8") as f:
            cpu_line = f.readline().strip()
    except OSError:
        cpu_line = ""
    cpu_parts = cpu_line.split()
    cpu_fields = {
        "user": int(cpu_parts[1]) if len(cpu_parts) > 1 else 0,
        "system": int(cpu_parts[2]) if len(cpu_parts) > 2 else 0,
        "idle": int(cpu_parts[3]) if len(cpu_parts) > 3 else 0,
        "iowait": int(cpu_parts[4]) if len(cpu_parts) > 4 else 0,
    }
    mem = {}
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split()
                if parts:
                    mem[parts[0].rstrip(":")] = int(parts[1])
    except OSError:
        pass
    mem_total = mem.get("MemTotal", 0)
    mem_available = mem.get("MemAvailable", 0)
    mem_used = max(mem_total - mem_available, 0)
    uptime_seconds = 0.0
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            uptime_seconds = float(f.read().split()[0])
    except OSError:
        pass

    return {
        "cpu": cpu_fields,
        "memory": {
            "total_bytes": mem_total * 1024,
            "available_bytes": mem_available * 1024,
            "used_bytes": mem_used * 1024,
            "percent_used": round((mem_used / mem_total) * 100, 2)
            if mem_total
            else 0.0,
        },
        "uptime_seconds": uptime_seconds,
    }


def _heartbeat_payload(client):
    payload = {
        "version": os.environ.get("YACHT_AGENT_VERSION", "0.1.0"),
        "docker_version": client.version().get("Version"),
        "capabilities": _capabilities(),
        "containers_running": len([c for c in client.containers.list(all=True) if c.status == "running"]),
        "containers_total": len(client.containers.list(all=True)),
    }
    stats = _host_stats()
    if stats is not None:
        payload["host_stats"] = stats
    return payload


def _safe_container_record(container):
    attrs = dict(container.attrs)
    attrs["name"] = container.name
    attrs["ports"] = container.ports
    attrs["short_id"] = container.short_id
    return attrs


def _safe_image_record(image, containers):
    attrs = dict(image.attrs)
    attrs["inUse"] = any(
        getattr(container.image, "id", None) and container.image.id in image.id
        for container in containers
    )
    return attrs


def _safe_volume_record(volume, containers):
    attrs = dict(volume.attrs)
    mountpoint = attrs.get("Mountpoint")
    attrs["inUse"] = any(
        any(
            mount.get("Source") == mountpoint
            for mount in container.attrs.get("Mounts", [])
        )
        for container in containers
    )
    return attrs


def _safe_network_record(network, containers):
    attrs = dict(network.attrs)
    attrs["inUse"] = any(
        any(
            details.get("NetworkID") == attrs.get("Id")
            for details in container.attrs.get("ContainerNetworkSettings", {})
            .get("Networks", {})
            .values()
        )
        for container in containers
    )
    labels = attrs.get("Labels") or {}
    if labels.get("com.docker.compose.project"):
        attrs["Project"] = labels["com.docker.compose.project"]
    return attrs


def _inventory_payload(client):
    containers = client.containers.list(all=True)
    images = client.images.list()
    volumes = client.volumes.list()
    networks = client.networks.list()
    return {
        "containers": [_safe_container_record(container) for container in containers],
        "images": [_safe_image_record(image, containers) for image in images],
        "volumes": [_safe_volume_record(volume, containers) for volume in volumes],
        "networks": [_safe_network_record(network, containers) for network in networks],
    }


def _compose_payload(client):
    projects = {}
    containers = client.containers.list(all=True)
    for container in containers:
        labels = container.attrs.get("Config", {}).get("Labels") or {}
        project = labels.get("com.docker.compose.project")
        if not project:
            continue
        entry = projects.setdefault(
            project,
            {
                "name": project,
                "containers": [],
                "working_dir": labels.get("com.docker.compose.working_dir"),
                "config_files": labels.get("com.docker.compose.config.file"),
            },
        )
        entry["containers"].append(
            {
                "id": container.id,
                "name": container.name,
                "service": labels.get("com.docker.compose.service"),
                "state": container.status,
                "exit_code": container.attrs.get("State", {}).get("ExitCode"),
            }
        )
    return projects


def _session():
    session = requests.Session()
    session.trust_env = False
    return session


def _agent_headers(state: dict) -> dict:
    agent_token = state.get("agent_token")
    if not agent_token:
        raise RuntimeError("Agent token is missing from state.")
    return {"X-Yacht-Agent-Token": agent_token}


def register_agent(session, client, state):
    enroll_token = os.environ.get("YACHT_AGENT_ENROLLMENT_TOKEN", "").strip()
    if not enroll_token:
        raise RuntimeError("YACHT_AGENT_ENROLLMENT_TOKEN is required.")

    response = session.post(
        f"{_normalize_server_url()}/agents/register",
        json=_registration_payload(client),
        headers={"X-Yacht-Agent-Enrollment-Token": enroll_token},
        timeout=15,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()
    data = response.json()
    state["agent_token"] = data["agent_token"]
    state["agent_id"] = data["agent_id"]
    state["host_id"] = data["host_id"]
    _save_state(state)
    logger.info("Registered agent %s for host %s", data["agent_id"], data["host_id"])
    return int(data.get("heartbeat_interval", HEARTBEAT_INTERVAL))


def heartbeat(session, client, state):
    response = session.post(
        f"{_normalize_server_url()}/agents/heartbeat",
        json=_heartbeat_payload(client),
        headers=_agent_headers(state),
        timeout=15,
        verify=VERIFY_SSL,
    )
    if response.status_code in {401, 403, 404}:
        logger.warning("Agent token rejected by server, re-registering.")
        _clear_registration(state)
        return register_agent(session, client, state)

    response.raise_for_status()
    data = response.json()
    logger.info("Heartbeat accepted for host %s", data.get("host_id"))
    return int(data.get("heartbeat_interval", HEARTBEAT_INTERVAL))


def sync_inventory(session, client, state):
    response = session.post(
        f"{_normalize_server_url()}/agents/sync",
        json={
            **_inventory_payload(client),
            "compose_projects": _compose_payload(client),
        },
        headers=_agent_headers(state),
        timeout=30,
        verify=VERIFY_SSL,
    )
    if response.status_code in {401, 403, 404}:
        logger.warning("Inventory sync rejected by server, re-registering.")
        _clear_registration(state)
        return False

    response.raise_for_status()
    data = response.json()
    logger.info("Inventory sync accepted for host %s", data.get("host_id"))
    return True


def fetch_next_job(session, state):
    response = session.get(
        f"{_normalize_server_url()}/agents/jobs/next",
        headers=_agent_headers(state),
        timeout=15,
        verify=VERIFY_SSL,
    )
    if response.status_code in {401, 403, 404}:
        logger.warning("Job polling rejected by server, re-registering.")
        _clear_registration(state)
        return None
    response.raise_for_status()
    return response.json()


def submit_job_result(session, state, job_id, status, result=None, error=None):
    response = session.post(
        f"{_normalize_server_url()}/agents/jobs/{job_id}/result",
        json={
            "status": status,
            "result": result or {},
            "error": error,
        },
        headers=_agent_headers(state),
        timeout=30,
        verify=VERIFY_SSL,
    )
    if response.status_code in {401, 403, 404}:
        logger.warning("Job result rejected by server, re-registering.")
        _clear_registration(state)
        return
    response.raise_for_status()


def _run_container_action(client, payload):
    container_name = (payload or {}).get("container")
    action = (payload or {}).get("action")
    if not container_name:
        raise ValueError("Container action job is missing a container name.")
    if action not in SUPPORTED_CONTAINER_ACTIONS:
        raise ValueError(f"Unsupported container action: {action}")

    container = client.containers.get(container_name)
    container_action = getattr(container, action, None)
    if container_action is None:
        raise ValueError(f"Container action is not available: {action}")

    if action == "remove":
        container_action(force=True)
    else:
        container_action()

    return {
        "container": container_name,
        "action": action,
        "inventory": _inventory_payload(client),
        "compose_projects": _compose_payload(client),
    }


def _find_compose_file(working_dir):
    """Find the compose file in the working directory."""
    patterns = ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]
    for pattern in patterns:
        candidate = Path(working_dir) / pattern
        if candidate.exists():
            return str(candidate)
    # Fallback: any .yml/.yaml file in the directory
    for ext in (".yml", ".yaml"):
        matches = list(Path(working_dir).glob(f"*{ext}"))
        if matches:
            return str(matches[0])
    return None


def _run_compose_action(client, payload):
    project = (payload or {}).get("project")
    action = (payload or {}).get("action")
    working_dir = (payload or {}).get("working_dir")
    if not project or action not in SUPPORTED_COMPOSE_ACTIONS:
        raise ValueError("Compose job requires project and a supported action.")

    import subprocess

    config_files = (payload or {}).get("config_files")
    if working_dir is None:
        working_dir = config_files.rsplit("/", 1)[0] if config_files else None

    cwd = working_dir
    compose_file = None
    if cwd and Path(cwd).exists():
        compose_file = _find_compose_file(cwd)

    cmd_map = {
        "up": ["up", "-d", "--remove-orphans"],
        "down": ["down", "--remove-orphans"],
        "pull": ["pull"],
    }
    subcmd = cmd_map[action]
    cmd = ["docker", "compose"]
    if compose_file:
        cmd.extend(["-f", compose_file])
    cmd.extend(subcmd)

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd if cwd and Path(cwd).exists() else None,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"docker compose {action} failed (exit {result.returncode}):\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
    except FileNotFoundError:
        raise RuntimeError(
            "docker compose CLI is not available in the agent container. "
            "Install the docker-compose plugin or docker CLI."
        )

    return {
        "project": project,
        "action": action,
        "inventory": _inventory_payload(client),
        "compose_projects": _compose_payload(client),
    }


def execute_job(session, client, state, job):
    if not job:
        return False

    job_id = job.get("job_id")
    job_type = job.get("job_type")
    payload = job.get("payload") or {}
    if not job_id or not job_type:
        logger.warning("Ignoring malformed job payload: %s", job)
        return False

    try:
        if job_type == "container_action":
            result = _run_container_action(client, payload)
        elif job_type == "compose_action":
            result = _run_compose_action(client, payload)
        else:
            raise ValueError(f"Unsupported job type: {job_type}")
    except docker.errors.DockerException as exc:
        logger.error("Agent job %s failed: %s", job_id, exc)
        submit_job_result(session, state, job_id, "failed", error=str(exc))
        return True
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Agent job %s failed: %s", job_id, exc)
        submit_job_result(session, state, job_id, "failed", error=str(exc))
        return True

    submit_job_result(session, state, job_id, "succeeded", result=result)
    logger.info("Completed agent job %s (%s)", job_id, job_type)
    return True


def main():
    state = _load_state()
    next_heartbeat_at = 0.0
    next_sync_at = 0.0
    current_heartbeat_interval = HEARTBEAT_INTERVAL

    while True:
        now = time.monotonic()
        try:
            client = _docker_client()
            session = _session()
            try:
                if not state.get("agent_token"):
                    current_heartbeat_interval = register_agent(session, client, state)
                    sync_inventory(session, client, state)
                    now = time.monotonic()
                    next_heartbeat_at = now + current_heartbeat_interval
                    next_sync_at = now + current_heartbeat_interval
                else:
                    if now >= next_heartbeat_at:
                        current_heartbeat_interval = heartbeat(session, client, state)
                        next_heartbeat_at = now + current_heartbeat_interval
                    if now >= next_sync_at:
                        if sync_inventory(session, client, state):
                            next_sync_at = now + current_heartbeat_interval

                if state.get("agent_token"):
                    job = fetch_next_job(session, state)
                    if job:
                        execute_job(session, client, state, job)
            finally:
                session.close()
                client.close()
        except requests.RequestException as exc:
            logger.error("HTTP error talking to Yacht: %s", exc)
        except docker.errors.DockerException as exc:
            logger.error("Local Docker error: %s", exc)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Agent loop failed: %s", exc)

        time.sleep(max(JOB_POLL_INTERVAL, 2))


if __name__ == "__main__":
    main()
