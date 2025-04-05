from typing import Tuple

from api.settings import Settings

from fastapi import HTTPException
from fastapi_jwt_auth.exceptions import JWTDecodeError

from passlib import pwd
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = Settings()


def verify_and_update_password(
    plain_password: str, hashed_password: str
) -> Tuple[bool, str]:
    return pwd_context.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_password() -> str:
    return pwd.genword()


def auth_check(Authorize):
    auth_setting = str(settings.DISABLE_AUTH)
    if auth_setting.lower() == "true":
        return
    else:
        try:
            return Authorize.jwt_required()
        except JWTDecodeError as exc:
            status_code = exc.status_code
            if (
                exc.message == "Signature verification failed"
                or exc.message == "Signature has expired"
            ):
                status_code = 401
            raise HTTPException(status_code=status_code, detail=exc.message)
