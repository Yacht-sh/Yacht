from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
import logging


logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session

from api.auth.auth import auth_check
from api.db.crud.agents import get_agent_for_host, get_agent_for_host_optional
from api.db.crud.hosts import create_host, delete_host_and_agent, get_host, get_hosts
from api.db.schemas.agents import AgentRead
from api.db.schemas.hosts import HostCreate, HostRead
from api.utils.auth import get_db
from api.utils.docker_hosts import get_docker_client

router = APIRouter()


@router.get("/", response_model=list[HostRead])
def index(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return get_hosts(db)


@router.get("/{host_id}/agent", response_model=dict)
def host_agent(
    host_id: int,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    host = get_host(db, host_id)
    if host.connection_type != "agent":
        raise HTTPException(status_code=404, detail="Host is not agent-managed.")
    agent = get_agent_for_host_optional(db, host.id)
    if agent is None:
        return {"agent": None}
    return {
        "agent": AgentRead(
            id=agent.id,
            host_id=agent.host_id,
            host_name=host.name,
            hostname=agent.hostname,
            version=agent.version,
            docker_version=agent.docker_version,
            capabilities=agent.capabilities or {},
            last_heartbeat=agent.last_heartbeat,
            inventory_updated_at=agent.inventory_updated_at,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        ).model_dump()
    }


@router.post("/", response_model=HostRead, status_code=status.HTTP_201_CREATED)
def create(
    host: HostCreate,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    created = create_host(db, host)
    try:
        _, client = get_docker_client(db, created.id)
        client.close()
    except Exception as exc:
        logger.exception("Unhandled exception")
        db.delete(created)
        db.commit()
        raise
    return created


@router.delete("/{host_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_host(
    host_id: int,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    host = get_host(db, host_id)
    if host.is_default:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the default host. Set another host as default first.",
        )
    delete_host_and_agent(db, host)
    return
