from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from api.auth.auth import auth_check
from api.db.crud.agents import (
    claim_next_agent_job,
    complete_agent_job,
    heartbeat_agent,
    list_agents,
    register_agent,
    sync_agent_inventory,
)
from api.db.schemas.agents import (
    AgentHeartbeat,
    AgentHeartbeatResponse,
    AgentJobRead,
    AgentJobResult,
    AgentJobResultResponse,
    AgentInventorySync,
    AgentInventorySyncResponse,
    AgentRead,
    AgentRegister,
    AgentRegisterResponse,
)
from api.utils.auth import get_db

router = APIRouter()


@router.get("/", response_model=list[AgentRead])
def index(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    agents = list_agents(db)
    return [
        AgentRead(
            id=agent.id,
            host_id=host.id,
            host_name=host.name,
            hostname=agent.hostname,
            version=agent.version,
            docker_version=agent.docker_version,
            capabilities=agent.capabilities or {},
            last_heartbeat=agent.last_heartbeat,
            inventory_updated_at=agent.inventory_updated_at,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )
        for agent, host in agents
    ]


@router.post(
    "/register",
    response_model=AgentRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: AgentRegister,
    db: Session = Depends(get_db),
    x_yacht_agent_enrollment_token: Optional[str] = Header(default=None),
):
    host, agent, raw_token = register_agent(
        db, payload, x_yacht_agent_enrollment_token
    )
    return AgentRegisterResponse(
        host_id=host.id,
        agent_id=agent.agent_key,
        agent_token=raw_token,
        heartbeat_interval=30,
    )


@router.post("/heartbeat", response_model=AgentHeartbeatResponse)
def heartbeat(
    payload: AgentHeartbeat,
    db: Session = Depends(get_db),
    x_yacht_agent_token: Optional[str] = Header(default=None),
):
    host, _agent = heartbeat_agent(db, payload, x_yacht_agent_token)
    return AgentHeartbeatResponse(
        host_id=host.id,
        heartbeat_interval=30,
        server_time=datetime.utcnow(),
    )


@router.get("/jobs/next", response_model=Optional[AgentJobRead])
def next_job(
    db: Session = Depends(get_db),
    x_yacht_agent_token: Optional[str] = Header(default=None),
):
    _host, _agent, job = claim_next_agent_job(db, x_yacht_agent_token)
    if job is None:
        return None
    return AgentJobRead(job_id=job.job_key, job_type=job.job_type, payload=job.payload)


@router.post("/jobs/{job_id}/result", response_model=AgentJobResultResponse)
def complete_job(
    job_id: str,
    payload: AgentJobResult,
    db: Session = Depends(get_db),
    x_yacht_agent_token: Optional[str] = Header(default=None),
):
    _host, _agent, job = complete_agent_job(db, job_id, payload, x_yacht_agent_token)
    return AgentJobResultResponse(
        job_id=job.job_key,
        status=job.status,
        updated_at=job.updated_at,
    )


@router.post("/sync", response_model=AgentInventorySyncResponse)
def sync(
    payload: AgentInventorySync,
    db: Session = Depends(get_db),
    x_yacht_agent_token: Optional[str] = Header(default=None),
):
    host, agent = sync_agent_inventory(db, payload, x_yacht_agent_token)
    return AgentInventorySyncResponse(
        host_id=host.id,
        inventory_updated_at=agent.inventory_updated_at,
    )
