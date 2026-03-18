import os
import uvicorn
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.db.models.settings import TokenBlacklist
from api.settings import Settings
from api.utils.auth import get_db
from api.db.models.containers import TemplateVariables
from api.db.models.settings import SecretKey
from api.db.database import SessionLocal, engine, Base
from api.db.schemas.users import UserCreate
from api.db.crud.settings import generate_secret_key
from api.db.crud.users import create_user, get_users
from api.routers import apps, app_settings, compose, hosts, resources, templates, users
from api.db.crud.templates import read_template_variables, set_template_variables
from api.db.crud.hosts import ensure_local_host

settings = Settings()

docs_enabled = settings.EXPOSE_API_DOCS
app = FastAPI(
    root_path="/api",
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)


class jwtSettings(BaseModel):
    authjwt_secret_key: str = generate_secret_key(db=SessionLocal())
    authjwt_token_location: set = {"headers", "cookies"}
    authjwt_cookie_secure: bool = settings.SECURE_COOKIES
    authjwt_cookie_csrf_protect: bool = True
    authjwt_access_token_expires: int = int(settings.ACCESS_TOKEN_EXPIRES)
    authjwt_refresh_token_expires: int = int(settings.REFRESH_TOKEN_EXPIRES)
    authjwt_cookie_samesite: str = settings.SAME_SITE_COOKIES
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}


@AuthJWT.load_config
def get_config():
    return jwtSettings()


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    db = SessionLocal()
    try:
        jti = decrypted_token["jti"]
        entry = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
        return entry is not None
    finally:
        db.close()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    status_code = exc.status_code
    if (
        exc.message == "Signature verification failed"
        or exc.message == "Signature has expired"
    ):
        status_code = 401
    return JSONResponse(status_code=status_code, content={"detail": exc.message})


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if not settings.ENABLE_SECURITY_HEADERS:
            return response

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), geolocation=(), microphone=()"
        )
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        if settings.SECURE_COOKIES and settings.HSTS_SECONDS > 0:
            response.headers.setdefault(
                "Strict-Transport-Security",
                f"max-age={settings.HSTS_SECONDS}; includeSubDomains",
            )
        return response


if settings.TRUSTED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS)

if settings.ENABLE_HTTPS_REDIRECT:
    app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(SecurityHeadersMiddleware)


app.include_router(users.router, prefix="/auth", tags=["users"])
app.include_router(hosts.router, prefix="/hosts", tags=["hosts"])
app.include_router(apps.router, prefix="/apps", tags=["apps"])
app.include_router(
    resources.router,
    prefix="/resources",
    tags=["resources"],
)
app.include_router(
    templates.router,
    prefix="/templates",
    tags=["templates"],
)
app.include_router(compose.router, prefix="/compose", tags=["compose"])
app.include_router(app_settings.router, prefix="/settings", tags=["settings"])


@app.on_event("startup")
async def startup(db: Session = Depends(get_db)):
    Base.metadata.create_all(bind=engine)
    startup_db = SessionLocal()
    try:
        ensure_local_host(db=startup_db)
        generate_secret_key(db=startup_db)
        users_exist = get_users(db=startup_db)
    finally:
        startup_db.close()
    print(
        "DISABLE_AUTH = "
        + str(settings.DISABLE_AUTH)
        + " ("
        + str(type(settings.DISABLE_AUTH))
        + ")"
    )
    if not users_exist:
        print("No Users. Creating the default user.")
        user = UserCreate(
            username=settings.ADMIN_EMAIL, password=settings.ADMIN_PASSWORD
        )
        create_user_db = SessionLocal()
        try:
            create_user(db=create_user_db, user=user)
        finally:
            create_user_db.close()
    template_db = SessionLocal()
    try:
        template_variables_exist = read_template_variables(template_db)
    finally:
        template_db.close()
    if not template_variables_exist:
        print("No Variables yet!")
        t_vars = settings.BASE_TEMPLATE_VARIABLES
        t_var_list = []
        for t in t_vars:
            template_variables = TemplateVariables(
                variable=t.get("variable"), replacement=t.get("replacement")
            )
            t_var_list.append(template_variables)
        template_update_db = SessionLocal()
        try:
            set_template_variables(new_variables=t_var_list, db=template_update_db)
        finally:
            template_update_db.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=8000,
        reload=True,
    )
