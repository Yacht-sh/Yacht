import hashlib
import secrets
import time
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.db.models.agent_jobs import AgentJob
from api.db.models.agents import Agent
from api.db.models.hosts import Host
from api.settings import Settings

settings = Settings()


def _hash_agent_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _validate_enrollment_token(token: str | None):
    configured_token = settings.AGENT_ENROLLMENT_TOKEN
    if not configured_token:
        raise HTTPException(
            status_code=503,
            detail="Agent enrollment is not configured on this Yacht server.",
        )
    if not token or token != configured_token:
        raise HTTPException(status_code=403, detail="Invalid agent enrollment token.")


def _issue_agent_token() -> str:
    return secrets.token_hex(32)


def register_agent(db: Session, payload, enrollment_token: str | None):
    _validate_enrollment_token(enrollment_token)

    host = db.query(Host).filter(Host.name == payload.name).first()
    if host is not None and host.connection_type != "agent":
        raise HTTPException(
            status_code=409,
            detail="Host name already exists for a non-agent connection type.",
        )

    if host is None:
        host = Host(
            name=payload.name,
            connection_type="agent",
            is_active=True,
            is_default=False,
            last_seen=datetime.utcnow(),
        )
        db.add(host)
        db.flush()
    else:
        host.connection_type = "agent"
        host.is_active = True
        host.last_seen = datetime.utcnow()
        db.add(host)
        db.flush()

    agent = db.query(Agent).filter(Agent.host_id == host.id).first()
    raw_token = _issue_agent_token()
    if agent is None:
        agent = Agent(
            host_id=host.id,
            agent_key=str(uuid4()),
            token_hash=_hash_agent_token(raw_token),
        )

    agent.token_hash = _hash_agent_token(raw_token)
    agent.hostname = payload.hostname
    agent.version = payload.version
    agent.docker_version = payload.docker_version
    agent.capabilities = payload.capabilities or {}
    agent.last_heartbeat = datetime.utcnow()
    db.add(agent)
    db.commit()
    db.refresh(host)
    db.refresh(agent)
    return host, agent, raw_token


def authenticate_agent(db: Session, agent_token: str | None):
    if not agent_token:
        raise HTTPException(status_code=401, detail="Missing agent token.")

    token_hash = _hash_agent_token(agent_token)
    agent = db.query(Agent).filter(Agent.token_hash == token_hash).first()
    if agent is None:
        raise HTTPException(status_code=401, detail="Invalid agent token.")
    return agent


def heartbeat_agent(db: Session, payload, agent_token: str | None):
    agent = authenticate_agent(db, agent_token)
    host = db.query(Host).filter(Host.id == agent.host_id).first()
    if host is None:
        raise HTTPException(status_code=404, detail="Agent host not found.")

    host.is_active = True
    host.last_seen = datetime.utcnow()
    agent.last_heartbeat = datetime.utcnow()
    if payload.version:
        agent.version = payload.version
    if payload.docker_version:
        agent.docker_version = payload.docker_version
    if payload.capabilities is not None:
        agent.capabilities = payload.capabilities
    db.add(host)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return host, agent


def _apply_inventory_to_agent(agent: Agent, inventory: dict | None):
    if inventory is None:
        return
    agent.inventory_updated_at = datetime.utcnow()
    agent.containers = inventory.get("containers", [])
    agent.images = inventory.get("images", [])
    agent.volumes = inventory.get("volumes", [])
    agent.networks = inventory.get("networks", [])


def sync_agent_inventory(db: Session, payload, agent_token: str | None):
    agent = authenticate_agent(db, agent_token)
    host = db.query(Host).filter(Host.id == agent.host_id).first()
    if host is None:
        raise HTTPException(status_code=404, detail="Agent host not found.")

    updated_at = datetime.utcnow()
    host.is_active = True
    host.last_seen = updated_at
    agent.last_heartbeat = updated_at
    agent.inventory_updated_at = updated_at
    agent.containers = payload.containers
    agent.images = payload.images
    agent.volumes = payload.volumes
    agent.networks = payload.networks
    db.add(host)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return host, agent


def get_agent_for_host(db: Session, host_id: int):
    agent = db.query(Agent).filter(Agent.host_id == host_id).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent inventory not found.")
    return agent


def queue_agent_job(db: Session, host_id: int, job_type: str, payload: dict):
    agent = get_agent_for_host(db, host_id)
    job = AgentJob(
        agent_id=agent.id,
        job_key=str(uuid4()),
        job_type=job_type,
        status="pending",
        payload=payload,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def claim_next_agent_job(db: Session, agent_token: str | None):
    agent = authenticate_agent(db, agent_token)
    host = db.query(Host).filter(Host.id == agent.host_id).first()
    if host is None:
        raise HTTPException(status_code=404, detail="Agent host not found.")

    now = datetime.utcnow()
    stale_after = 60
    jobs = (
        db.query(AgentJob)
        .filter(AgentJob.agent_id == agent.id)
        .filter(AgentJob.status.in_(("pending", "running")))
        .order_by(AgentJob.created_at.asc())
        .all()
    )
    for job in jobs:
        if job.status == "running" and job.assigned_at is not None:
            if (now - job.assigned_at).total_seconds() < stale_after:
                continue
        job.status = "running"
        job.assigned_at = now
        agent.last_heartbeat = now
        host.is_active = True
        host.last_seen = now
        db.add(job)
        db.add(agent)
        db.add(host)
        db.commit()
        db.refresh(job)
        return host, agent, job
    return host, agent, None


def complete_agent_job(
    db: Session, job_key: str, payload, agent_token: str | None
):
    agent = authenticate_agent(db, agent_token)
    job = (
        db.query(AgentJob)
        .filter(AgentJob.agent_id == agent.id, AgentJob.job_key == job_key)
        .first()
    )
    if job is None:
        raise HTTPException(status_code=404, detail="Agent job not found.")

    host = db.query(Host).filter(Host.id == agent.host_id).first()
    if host is None:
        raise HTTPException(status_code=404, detail="Agent host not found.")

    now = datetime.utcnow()
    job.status = payload.status
    job.result = payload.result or {}
    job.error = payload.error
    job.completed_at = now
    agent.last_heartbeat = now
    host.is_active = True
    host.last_seen = now
    _apply_inventory_to_agent(agent, job.result.get("inventory"))
    db.add(job)
    db.add(agent)
    db.add(host)
    db.commit()
    db.refresh(job)
    return host, agent, job


def wait_for_agent_job(db: Session, job_id: int, timeout_seconds: int = 20):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        db.expire_all()
        job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
        if job is None:
            raise HTTPException(status_code=404, detail="Agent job not found.")
        if job.status in {"succeeded", "failed"}:
            return job
        time.sleep(1)
    raise HTTPException(status_code=504, detail="Timed out waiting for agent job.")


def list_agents(db: Session):
    return db.query(Agent, Host).join(Host, Host.id == Agent.host_id).all()
