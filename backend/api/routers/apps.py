from typing import Optional

from fastapi import APIRouter, Depends, status, Request
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from api.db.schemas import apps as schemas
import api.actions.apps as actions
from api.settings import Settings
from api.auth.auth import auth_check
from api.utils.apps import calculate_cpu_percent, calculate_cpu_percent2, format_bytes
from api.utils.auth import get_db

from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
import aiodocker
import json
import asyncio

settings = Settings()

router = APIRouter()


@router.get("/")
def index(
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return actions.get_apps(db=db, host_id=host_id)


@router.get("/{app_name}/updates")
def check_app_updates(
    app_name,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return actions.check_app_update(app_name, db=db, host_id=host_id)


@router.get("/{app_name}/update")
def update_container(
    app_name,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return actions.app_update(app_name, db=db, host_id=host_id)

@router.get("/stats")
async def all_sse_stats(
    request: Request,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    stat_generator = actions.all_stat_generator(request, db=db, host_id=host_id)
    return EventSourceResponse(stat_generator)

@router.get("/{app_name}")
def get_container_details(
    app_name,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return actions.get_app(app_name=app_name, db=db, host_id=host_id)


@router.get("/{app_name}/processes", response_model=schemas.Processes)
def get_container_processes(
    app_name,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return actions.get_app_processes(app_name=app_name, db=db, host_id=host_id)


@router.get("/{app_name}/support")
def get_support_bundle(
    app_name,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return actions.generate_support_bundle(app_name, db=db, host_id=host_id)


@router.get("/actions/{app_name}/{action}")
def container_actions(
    app_name,
    action,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return actions.app_action(app_name, action, db=db, host_id=host_id)


@router.post("/deploy", response_model=schemas.DeployLogs)
def deploy_app(
    template: schemas.DeployForm,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return actions.deploy_app(template=template, db=db)

@router.get("/{app_name}/logs")
async def logs(
    app_name: str,
    request: Request,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    log_generator = actions.log_generator(request, app_name, db=db, host_id=host_id)
    return EventSourceResponse(log_generator)


@router.get("/{app_name}/stats")
async def sse_stats(
    app_name: str,
    request: Request,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    stat_generator = actions.stat_generator(request, app_name, db=db, host_id=host_id)
    return EventSourceResponse(stat_generator)
