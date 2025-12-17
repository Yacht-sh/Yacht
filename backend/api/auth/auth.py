from api.settings import Settings
from fastapi import HTTPException, Depends, status
from api.auth.jwt import get_auth_wrapper
from sqlalchemy.orm import Session
from api.db.database import SessionLocal
from api.db.models.users import User

settings = Settings()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# This is a compatibility layer to replace fastapi-jwt-auth usage in other files
# The function `auth_check` was used in routers.
# Original signature: def auth_check(Authorize):
# Now Authorize will be our AuthWrapper.

def auth_check(Authorize: get_auth_wrapper = Depends(get_auth_wrapper)):
    auth_setting = str(settings.DISABLE_AUTH)
    if auth_setting.lower() == "true":
        return
    else:
        # AuthWrapper.jwt_required() raises HTTPException if invalid
        Authorize.jwt_required()

def check_permission(permission_name: str, Authorize: get_auth_wrapper, db: Session):
    """
    Checks if the current user has the specified permission.
    Admins (is_superuser) always have access.
    """
    auth_setting = str(settings.DISABLE_AUTH)
    if auth_setting.lower() == "true":
        return True

    username = Authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if user.is_superuser:
        return True

    if getattr(user, permission_name, False):
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"User lacks permission: {permission_name}"
    )
