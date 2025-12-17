import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from api.settings import Settings

settings = Settings()

# Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    # Add other claims if needed

# JWT Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRES) / 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        return token_data
    except jwt.PyJWTError:
        raise credentials_exception

def get_current_user_token(request: Request):
    # Check header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    # Check cookie
    token = request.cookies.get("access_token_cookie")
    if token:
        # Some frameworks might prefix with Bearer in cookie, usually not but handle if needed.
        # Here we assume just the token.
        # But wait, fastapi-jwt-auth (which we replaced) might have used 'access_token_cookie'
        # We should check how the frontend sends it.
        # The frontend likely expects the cookie to be set.
        return token
    return None

def get_current_user(token: str = Depends(get_current_user_token)):
    auth_setting = str(settings.DISABLE_AUTH)
    if auth_setting.lower() == "true":
        return "admin" # Mock user when auth disabled

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    return verify_token(token, credentials_exception)

# Dependency wrapper to mimic the old Authorize style if we want to minimize refactoring,
# or we can refactor routes to use `Depends(get_current_user)` directly.
# Given the existing code uses `Authorize: AuthJWT = Depends()`, let's try to adapt.

class AuthWrapper:
    def __init__(self, request: Request):
        self.request = request
        self.user = None

    def jwt_required(self):
        token = get_current_user_token(self.request)
        self.user = get_current_user(token)
        return self.user

    def get_jwt_subject(self):
        if self.user:
            return self.user.username
        # If jwt_required wasn't called (it should have been), call it
        return self.jwt_required().username

    def unset_jwt_cookies(self, response):
        response.delete_cookie("access_token_cookie")

    def set_access_cookies(self, token, response, max_age=None):
        # We need to set the cookie.
        # Using settings from main.py / settings.py
        response.set_cookie(
            key="access_token_cookie",
            value=token,
            httponly=True,
            max_age=max_age or int(settings.ACCESS_TOKEN_EXPIRES),
            samesite=settings.SAME_SITE_COOKIES,
            secure=False # Should be True in prod if https
        )

def get_auth_wrapper(request: Request):
    return AuthWrapper(request)
