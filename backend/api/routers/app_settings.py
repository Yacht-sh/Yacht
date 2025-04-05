from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from typing import List

from sqlalchemy.orm import Session

from api.utils.auth import get_db
from api.auth.auth import auth_check

from api.db.crud import templates as crud
from api.db.crud import settings as scrud
from api.db.schemas import templates as schemas
from api.db.models import containers
from api.db.database import engine

from api.actions import resources
from api.actions.apps import _update_self, check_self_update

from api.settings import Settings

from fastapi_jwt_auth import AuthJWT


containers.Base.metadata.create_all(bind=engine)

settings = Settings()

router = APIRouter()


@router.get(
    "/variables",
    response_model=List[schemas.TemplateVariables],
    operation_id="authorize",
)
def read_template_variables(
    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    auth_check(Authorize)
    return crud.read_template_variables(db=db)


@router.post(
    "/variables",
    response_model=List[schemas.TemplateVariables],
)
def set_template_variables(
    new_variables: List[schemas.TemplateVariables],
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return crud.set_template_variables(new_variables=new_variables, db=db)


@router.get(
    "/export",
    response_model=schemas.Import_Export,
)
def export_settings(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return scrud.export_settings(db=db)


@router.post(
    "/export",
)
def import_settings(
    db: Session = Depends(get_db),
    upload: UploadFile = File(...),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return scrud.import_settings(db=db, upload=upload)


@router.get(
    "/prune/{resource}",
)
def prune_resources(resource: str, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.prune_resources(resource)


@router.get(
    "/update",
)
def update_self(background_tasks: BackgroundTasks, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return _update_self(background_tasks)


@router.get(
    "/check/update",
)
def _check_self_update(Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return check_self_update()
