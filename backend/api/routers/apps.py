from fastapi import APIRouter, Depends, status, Request
from sse_starlette.sse import EventSourceResponse

from api.db.schemas import apps as schemas
import api.actions.apps as actions
from api.settings import Settings
from api.auth.auth import auth_check
from api.utils.apps import calculate_cpu_percent, calculate_cpu_percent2, format_bytes

from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
import aiodocker
import json
import asyncio

settings = Settings()

router = APIRouter()


@router.get("/")
def index(Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return actions.get_apps()


@router.get("/{app_name}/updates")
def check_app_updates(app_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return actions.check_app_update(app_name)


@router.get("/{app_name}/update")
def update_container(app_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return actions.app_update(app_name)

@router.get("/stats")
async def all_sse_stats(request: Request, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    stat_generator = actions.all_stat_generator(request)
    return EventSourceResponse(stat_generator)

@router.get("/{app_name}")
def get_container_details(app_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return actions.get_app(app_name=app_name)


@router.get("/{app_name}/processes", response_model=schemas.Processes)
def get_container_processes(app_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return actions.get_app_processes(app_name=app_name)


@router.get("/{app_name}/support")
def get_support_bundle(app_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return actions.generate_support_bundle(app_name)


@router.get("/actions/{app_name}/{action}")
def container_actions(app_name, action, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return actions.app_action(app_name, action)


@router.post("/deploy", response_model=schemas.DeployLogs)
def deploy_app(template: schemas.DeployForm, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return actions.deploy_app(template=template)

@router.get("/{app_name}/logs")
async def logs(app_name: str, request: Request, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    log_generator = actions.log_generator(request, app_name)
    return EventSourceResponse(log_generator)


@router.get("/{app_name}/stats")
async def sse_stats(app_name: str, request: Request, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    stat_generator = actions.stat_generator(request, app_name)
    return EventSourceResponse(stat_generator)