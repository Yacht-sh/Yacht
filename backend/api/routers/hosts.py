from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from api.auth.auth import auth_check
from api.db.crud.hosts import create_host, get_hosts
from api.db.schemas.hosts import HostCreate, HostRead
from api.utils.auth import get_db
from api.utils.docker_hosts import get_docker_client

router = APIRouter()


@router.get("/", response_model=list[HostRead])
def index(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return get_hosts(db)


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
    except Exception:
        db.delete(created)
        db.commit()
        raise
    return created
