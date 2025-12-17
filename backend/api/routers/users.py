from fastapi import APIRouter, Depends, HTTPException, Body, Request, Response
from api.auth.jwt import get_auth_wrapper, create_access_token
from sqlalchemy.orm import Session
from typing import List, Optional

from api.utils.auth import get_db
from api.auth.auth import auth_check, check_permission
from api.settings import Settings
from api.db.crud import users as crud
from api.db.models import users as models
from api.db.schemas import users as schemas
from api.utils.security import check_ip_restriction, record_login_attempt
import pyotp

router = APIRouter()
settings = Settings()

# Add list users endpoint for admin
@router.get("/users", response_model=List[schemas.User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    Authorize: get_auth_wrapper = Depends(get_auth_wrapper)
):
    auth_check(Authorize)
    # Ensure only superuser can list users (or define a new permission perm_manage_users)
    username = Authorize.get_jwt_subject()
    user = crud.get_user_by_name(db, username)
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.get_users(db, skip=skip, limit=limit)

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    Authorize: get_auth_wrapper = Depends(get_auth_wrapper)
):
    auth_check(Authorize)
    username = Authorize.get_jwt_subject()
    user = crud.get_user_by_name(db, username)
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    user_to_delete = crud.get_user(db, user_id)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user_to_delete)
    db.commit()
    return {"message": "User deleted"}

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user_admin(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    Authorize: get_auth_wrapper = Depends(get_auth_wrapper)
):
    auth_check(Authorize)
    username = Authorize.get_jwt_subject()
    current_user = crud.get_user_by_name(db, username)
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_user = crud.update_user_by_id(db, user_id, user_update)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@router.post("/create", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    Authorize: get_auth_wrapper = Depends(get_auth_wrapper),
    db: Session = Depends(get_db),
):
    auth_check(Authorize)
    # Check permissions (only admin/superuser can create users?)
    # For now, allowing existing check to pass if they are authenticated
    # Ideally should check for 'admin' role or is_superuser

    # Check if creator is superuser if they are setting superuser/active/permissions
    # For simplicity, we enforce superuser check for user creation via this route if we are managing users.
    # But self-registration might be a thing? Assuming NO for Yacht (it's a server manager).
    # So creation should be restricted to Admins.
    username = Authorize.get_jwt_subject()
    creator = crud.get_user_by_name(db, username)
    if not creator or not creator.is_superuser:
         raise HTTPException(status_code=403, detail="Not authorized to create users")

    db_user = crud.get_user_by_name(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already in use")
    return crud.create_user(db=db, user=user)

@router.post("/login")
def login(
    request: Request,
    user: schemas.UserCreate,
    otp_token: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    Authorize: get_auth_wrapper = Depends(get_auth_wrapper),
):
    # Security Check
    client_ip = check_ip_restriction(request, db, user.username)

    _user = (
        db.query(models.User)
        .filter(models.User.username == user.username.casefold())
        .first()
    )
    if _user is not None and crud.verify_password(user.password, _user.hashed_password):

        # Check 2FA
        if _user.is_2fa_enabled:
            if not otp_token:
                return {
                    "login": "2fa_required",
                    "username": _user.username
                }
            else:
                totp = pyotp.TOTP(_user.otp_secret)
                if not totp.verify(otp_token):
                    record_login_attempt(db, client_ip, user.username, False)
                    raise HTTPException(status_code=400, detail="Invalid 2FA code")

        # Success
        record_login_attempt(db, client_ip, user.username, True)
        access_token = create_access_token(data={"sub": _user.username})

        return {
            "login": "successful",
            "username": _user.username,
            "access_token": access_token,
        }
    else:
        record_login_attempt(db, client_ip, user.username, False)
        raise HTTPException(status_code=400, detail="Invalid Username or Password.")

@router.post("/login_cookie")
def login_cookie(
    request: Request,
    response: Response,
    user: schemas.UserCreate,
    otp_token: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    Authorize: get_auth_wrapper = Depends(get_auth_wrapper),
):
    # Security Check
    client_ip = check_ip_restriction(request, db, user.username)

    _user = (
        db.query(models.User)
        .filter(models.User.username == user.username.casefold())
        .first()
    )
    if _user is not None and crud.verify_password(user.password, _user.hashed_password):
        if _user.is_2fa_enabled:
             if not otp_token:
                return {"login": "2fa_required", "username": _user.username}
             totp = pyotp.TOTP(_user.otp_secret)
             if not totp.verify(otp_token):
                 record_login_attempt(db, client_ip, user.username, False)
                 raise HTTPException(status_code=400, detail="Invalid 2FA code")

        record_login_attempt(db, client_ip, user.username, True)
        access_token = create_access_token(data={"sub": _user.username})
        Authorize.set_access_cookies(access_token, response)
        return {"login": "successful", "username": _user.username}
    else:
        record_login_attempt(db, client_ip, user.username, False)
        raise HTTPException(status_code=400, detail="Invalid Username or Password.")


@router.post("/refresh")
def refresh(Authorize: get_auth_wrapper = Depends(get_auth_wrapper)):
    current_user = Authorize.get_jwt_subject()
    new_access_token = create_access_token(data={"sub": current_user})
    return {"refresh": "successful", "access_token": new_access_token}


@router.get("/api/keys", response_model=List[schemas.APIKEY])
def get_api_keys(db: Session = Depends(get_db), Authorize: get_auth_wrapper = Depends(get_auth_wrapper)):
    auth_check(Authorize)
    current_user = Authorize.get_jwt_subject()
    if current_user is not None:
        user = crud.get_user_by_name(db=db, username=current_user)
    else:
        raise HTTPException(status_code=401, detail="Not logged in.")
    return crud.get_keys(user, db)


@router.post("/api/keys/new", response_model=schemas.DisplayAPIKEY)
def create_api_key(
    key: schemas.GenerateAPIKEY,
    db: Session = Depends(get_db),
    Authorize: get_auth_wrapper = Depends(get_auth_wrapper),
):
    name = key.key_name
    auth_check(Authorize)
    username = Authorize.get_jwt_subject()
    if username is not None:
        user = crud.get_user_by_name(db=db, username=username)
    else:
        raise HTTPException(status_code=401, detail="Not logged in.")
    return crud.create_key(name, user, Authorize, db)


@router.get("/api/keys/{key_id}")
def delete_api_key(
    key_id, db: Session = Depends(get_db), Authorize: get_auth_wrapper = Depends(get_auth_wrapper)
):
    auth_check(Authorize)
    return crud.blacklist_api_key(key_id, db)


@router.get("/me", response_model=schemas.User)
def get_user(db: Session = Depends(get_db), Authorize: get_auth_wrapper = Depends(get_auth_wrapper)):
    auth_check(Authorize)
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
        Authorize.jwt_required()
        current_user_name = Authorize.get_jwt_subject()
        if current_user_name is not None:
            return crud.get_user_by_name(db=db, username=current_user_name)
        else:
            raise HTTPException(status_code=401, detail="Not logged in.")


@router.post("/me", response_model=schemas.User)
def update_user(
    user: schemas.UserUpdate, # Updated schema
    db: Session = Depends(get_db),
    Authorize: get_auth_wrapper = Depends(get_auth_wrapper),
):
    auth_check(Authorize)
    current_user = Authorize.get_jwt_subject()
    return crud.update_user(db=db, user=user, current_user=current_user)


@router.get("/logout")
def logout(response: Response, Authorize: get_auth_wrapper = Depends(get_auth_wrapper), db: Session = Depends(get_db)):
    Authorize.unset_jwt_cookies(response)
    return {"msg": "Logout Successful"}


@router.get("/logout/refresh")
def logout_refresh(response: Response, Authorize: get_auth_wrapper = Depends(get_auth_wrapper), db: Session = Depends(get_db)):
    Authorize.unset_jwt_cookies(response)
    return {"msg": "Logout Successful"}
