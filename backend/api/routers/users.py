from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from typing import List

from api.utils.auth import get_db
from api.auth.auth import auth_check
from api.settings import Settings
from api.db.crud import users as crud
from api.db.models import users as models
from api.db.schemas import users as schemas

router = APIRouter()
settings = Settings()


@router.post(
    "/create",
    response_model=schemas.User,
    dependencies=[Depends(auth_check)],
)
def create_user(
    user: schemas.UserCreate,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    db_user = crud.get_user_by_name(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already in use")
    return crud.create_user(db=db, user=user)


@router.post("/login")
def login(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    crud.prune_blacklist(db)
    _user = (
        db.query(models.User)
        .filter(models.User.username == user.username.casefold())
        .first()
    )
    if _user is not None and crud.verify_password(user.password, _user.hashed_password):
        # Create Tokens
        access_token = Authorize.create_access_token(subject=user.username)
        refresh_token = Authorize.create_refresh_token(subject=user.username)

        # Assign cookies
        Authorize.set_access_cookies(access_token)
        Authorize.set_refresh_cookies(refresh_token)
        return {
            "login": "successful",
            "username": _user.username,
            "access_token": access_token,
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid Username or Password.")


@router.post("/refresh")
async def refresh(Authorize: AuthJWT = Depends()):
    await Authorize.jwt_refresh_token_required()

    current_user = await Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)

    Authorize.set_access_cookies(new_access_token)
    return {"refresh": "successful", "access_token": new_access_token}


@router.get(
    "/api/keys",
    response_model=List[schemas.APIKEY],
    dependencies=[Depends(auth_check)],
)
async def get_api_keys(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = await Authorize.get_jwt_subject()
    if current_user is not None:
        user = crud.get_user_by_name(db=db, username=current_user)
    else:
        raise HTTPException(status_code=401, detail="Not logged in.")
    return crud.get_keys(user, db)


@router.post(
    "/api/keys/new",
    response_model=schemas.DisplayAPIKEY,
    dependencies=[Depends(auth_check)],
)
async def create_api_key(
    key: schemas.GenerateAPIKEY,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    name = key.key_name
    current_user = await Authorize.get_jwt_subject()
    if current_user is not None:
        user = crud.get_user_by_name(db=db, username=current_user)
    else:
        raise HTTPException(status_code=401, detail="Not logged in.")
    return crud.create_key(name, user, Authorize, db)


@router.get("/api/keys/{key_id}", dependencies=[Depends(auth_check)])
def delete_api_key(
    key_id, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    return crud.blacklist_api_key(key_id, db)


@router.get(
    "/me",
    response_model=schemas.User,
    dependencies=[Depends(auth_check)],
)
async def get_user(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    auth_setting = str(settings.DISABLE_AUTH)
    if auth_setting.lower() == "true":
        current_user = schemas.User
        current_user.authDisabled = True
        current_user.id = 0
        current_user.username = "user"
        current_user.is_active = True
        current_user.is_superuser = True
        return current_user
    else:
        current_user = await Authorize.get_jwt_subject()
        if current_user is not None:
            return crud.get_user_by_name(db=db, username=current_user)
        else:
            raise HTTPException(status_code=401, detail="Not logged in.")


@router.post(
    "/me",
    response_model=schemas.User,
    dependencies=[Depends(auth_check)],
)
async def update_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    current_user = await Authorize.get_jwt_subject()
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not logged in.")

    updated_user = crud.update_user(db=db, user=user, current_user=current_user)

    # If username/email changes, rotate tokens so the current session remains valid.
    if updated_user.username != current_user:
        access_token = Authorize.create_access_token(subject=updated_user.username)
        refresh_token = Authorize.create_refresh_token(subject=updated_user.username)
        Authorize.set_access_cookies(access_token)
        Authorize.set_refresh_cookies(refresh_token)

    return updated_user


@router.get("/logout", dependencies=[Depends(auth_check)])
def logout(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    crud.blacklist_login_token(Authorize, db)
    return {"msg": "Logout Successful"}


@router.get("/logout/refresh")
async def logout(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    await Authorize.jwt_refresh_token_required()
    Authorize.unset_jwt_cookies()
    crud.blacklist_login_token(Authorize, db)
    return {"msg": "Logout Successful"}
