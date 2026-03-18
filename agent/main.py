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
VERIFY_SSL = os.environ.get("YACHT_AGENT_VERIFY_SSL", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

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


def _agent_name() -> str:
    return os.environ.get("YACHT_AGENT_NAME", socket.gethostname())


def _docker_client():
    client = docker.from_env()
    client.ping()
    return client


def _capabilities() -> dict[str, bool]:
    return {
        "containers": True,
        "images": True,
        "volumes": True,
        "networks": True,
        "compose": True,
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


def _heartbeat_payload(client):
    containers = client.containers.list(all=True)
    version = client.version()
    return {
        "version": os.environ.get("YACHT_AGENT_VERSION", "0.1.0"),
        "docker_version": version.get("Version"),
        "capabilities": _capabilities(),
        "containers_running": len([c for c in containers if c.status == "running"]),
        "containers_total": len(containers),
    }


def _session():
    session = requests.Session()
    session.trust_env = False
    return session


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
    agent_token = state.get("agent_token")
    if not agent_token:
        raise RuntimeError("Agent token is missing from state.")

    response = session.post(
        f"{_normalize_server_url()}/agents/heartbeat",
        json=_heartbeat_payload(client),
        headers={"X-Yacht-Agent-Token": agent_token},
        timeout=15,
        verify=VERIFY_SSL,
    )
    if response.status_code in {401, 403, 404}:
        logger.warning("Agent token rejected by server, re-registering.")
        state.pop("agent_token", None)
        state.pop("agent_id", None)
        state.pop("host_id", None)
        _save_state(state)
        return register_agent(session, client, state)

    response.raise_for_status()
    data = response.json()
    logger.info("Heartbeat accepted for host %s", data.get("host_id"))
    return int(data.get("heartbeat_interval", HEARTBEAT_INTERVAL))


def main():
    state = _load_state()
    while True:
        try:
            client = _docker_client()
            session = _session()
            try:
                if not state.get("agent_token"):
                    interval = register_agent(session, client, state)
                else:
                    interval = heartbeat(session, client, state)
            finally:
                session.close()
                client.close()
        except requests.RequestException as exc:
            logger.error("HTTP error talking to Yacht: %s", exc)
            interval = HEARTBEAT_INTERVAL
        except docker.errors.DockerException as exc:
            logger.error("Local Docker error: %s", exc)
            interval = HEARTBEAT_INTERVAL
        except Exception as exc:
            logger.exception("Agent loop failed: %s", exc)
            interval = HEARTBEAT_INTERVAL

        time.sleep(max(interval, 5))


if __name__ == "__main__":
    main()
