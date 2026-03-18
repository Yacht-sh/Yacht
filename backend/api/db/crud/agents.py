import hashlib
import secrets
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

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


def list_agents(db: Session):
    return db.query(Agent, Host).join(Host, Host.id == Agent.host_id).all()
