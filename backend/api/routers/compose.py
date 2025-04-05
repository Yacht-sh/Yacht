from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from api.actions.compose import (
    get_compose_projects,
    compose_action,
    compose_app_action,
    get_compose,
    write_compose,
    delete_compose,
    generate_support_bundle,
)
from api.auth.auth import auth_check
from api.db.schemas import compose as schemas

router = APIRouter()


@router.get("/")
def get_projects(Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return get_compose_projects()


@router.get("/{project_name}")
def get_project(project_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return get_compose(project_name)


@router.get("/{project_name}/actions/{action}")
def get_compose_action(project_name, action, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    if action == "delete":
        return delete_compose(project_name)
    else:
        return compose_action(project_name, action)


@router.post("/{project_name}/edit", response_model=schemas.ComposeRead)
def write_compose_project(
    project_name, compose: schemas.ComposeWrite, Authorize: AuthJWT = Depends()
):
    auth_check(Authorize)
    return write_compose(compose=compose)


@router.get("/{project_name}/actions/{action}/{app}")
def get_compose_app_action(project_name, action, app, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return compose_app_action(project_name, action, app)


@router.get("/{project_name}/support")
def get_support_bundle(project_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return generate_support_bundle(project_name)
