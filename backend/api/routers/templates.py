from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from sqlalchemy.orm import Session

import api.db.crud.templates as crud
import api.db.schemas.templates as schemas
from api.db.models.containers import Base
from api.db.database import engine
from api.utils.auth import get_db
from api.auth.auth import auth_check

from fastapi_jwt_auth import AuthJWT

Base.metadata.create_all(bind=engine)


router = APIRouter()


@router.get(
    "/",
    response_model=List[schemas.TemplateRead],
)
def index(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    templates = crud.get_templates(db=db)
    return templates


@router.get(
    "/{id}",
    response_model=schemas.TemplateItems,
)
def show(id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    template = crud.get_template_by_id(db=db, id=id)
    return template


@router.delete(
    "/{id}",
    response_model=schemas.TemplateRead,
)
def delete(id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return crud.delete_template(db=db, template_id=id)


@router.post("/", response_model=schemas.TemplateRead)
def add_template(
    template: schemas.TemplateBase,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    existing_template = crud.get_template(db=db, url=template.url)
    if existing_template:
        raise HTTPException(status_code=400, detail="Template already in Database.")
    return crud.add_template(db=db, template=template)


@router.get(
    "/{id}/refresh",
    response_model=schemas.TemplateRead,
)
def refresh_template(
    id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    auth_check(Authorize)
    return crud.refresh_template(db=db, template_id=id)


@router.get(
    "/app/{id}",
    response_model=schemas.TemplateItem,
)
def read_app_template(
    id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    auth_check(Authorize)
    return crud.read_app_template(db=db, app_id=id)
