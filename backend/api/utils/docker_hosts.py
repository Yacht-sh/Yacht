from datetime import datetime

import aiodocker
import docker
from fastapi import HTTPException

from api.db.crud.hosts import get_default_host, get_host


LOCAL_DOCKER_URL = "unix:///var/run/docker.sock"


def _normalize_docker_host(host):
    return host.docker_host or LOCAL_DOCKER_URL


def docker_base_url(host):
    return _normalize_docker_host(host)


def _http_exception_from_docker_error(exc, default_status=502):
    if hasattr(exc, "response") and exc.response is not None:
        return HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )
    detail = exc.args[0] if exc.args else str(exc)
    return HTTPException(status_code=default_status, detail=detail)


def resolve_host(db, host_id=None):
    host = get_default_host(db) if host_id is None else get_host(db, host_id)
    if not host.is_active:
        raise HTTPException(status_code=400, detail="Host is inactive.")
    host.last_seen = datetime.utcnow()
    db.add(host)
    db.commit()
    db.refresh(host)
    return host


def get_docker_client(db, host_id=None):
    host = resolve_host(db, host_id)
    try:
        if host.connection_type == "local":
            client = docker.from_env()
        elif host.connection_type == "docker_api":
            client = docker.DockerClient(base_url=_normalize_docker_host(host))
        else:
            raise HTTPException(
                status_code=501,
                detail=f"Unsupported host connection type: {host.connection_type}",
            )
        client.ping()
    except HTTPException:
        raise
    except Exception as exc:
        raise _http_exception_from_docker_error(exc)
    return host, client


def get_async_docker_client(db, host_id=None):
    host = resolve_host(db, host_id)
    if host.connection_type not in {"local", "docker_api"}:
        raise HTTPException(
            status_code=501,
            detail=f"Unsupported host connection type: {host.connection_type}",
        )
    return host, aiodocker.Docker(url=_normalize_docker_host(host))


def host_metadata(host):
    return {
        "id": host.id,
        "name": host.name,
        "connection_type": host.connection_type,
    }
