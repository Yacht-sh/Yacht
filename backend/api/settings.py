import os
import secrets
from pydantic import BaseSettings

basedir = os.path.abspath(os.path.dirname(__file__))


def compose_dir_check():
    if not os.environ.get("COMPOSE_DIR", "/config/compose/").endswith("/"):
        os.environ["COMPOSE_DIR"] += "/"
    return os.environ.get("COMPOSE_DIR", "/config/compose/")


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str) -> list[str]:
    value = os.environ.get(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    app_name: str = "Yacht API"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    ADMIN_PASSWORD: str = os.environ.get("ADMIN_PASSWORD", "pass")
    ADMIN_EMAIL: str = os.environ.get("ADMIN_EMAIL", "admin@yacht.local")
    ACCESS_TOKEN_EXPIRES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRES", 900))
    REFRESH_TOKEN_EXPIRES: int = int(
        os.environ.get("REFRESH_TOKEN_EXPIRES", 2592000)
    )
    SAME_SITE_COOKIES: str = os.environ.get("SAME_SITE_COOKIES", "lax")
    DISABLE_AUTH: bool = env_bool("DISABLE_AUTH", False)
    SECURE_COOKIES: bool = env_bool("SECURE_COOKIES", False)
    ENABLE_SECURITY_HEADERS: bool = env_bool("ENABLE_SECURITY_HEADERS", True)
    ENABLE_HTTPS_REDIRECT: bool = env_bool("ENABLE_HTTPS_REDIRECT", False)
    EXPOSE_API_DOCS: bool = env_bool("EXPOSE_API_DOCS", False)
    HSTS_SECONDS: int = int(os.environ.get("HSTS_SECONDS", 31536000))
    TRUSTED_HOSTS: list[str] = env_list("TRUSTED_HOSTS")
    BASE_TEMPLATE_VARIABLES = [
        {"variable": "!config", "replacement": "/yacht/AppData/Config"},
        {"variable": "!data", "replacement": "/yacht/AppData/Data"},
        {"variable": "!media", "replacement": "/yacht/Media/"},
        {"variable": "!downloads", "replacement": "/yacht/Downloads/"},
        {"variable": "!music", "replacement": "/yacht/Media/Music"},
        {"variable": "!playlists", "replacement": "/yacht/Media/Playlists"},
        {"variable": "!podcasts", "replacement": "/yacht/Media/Podcasts"},
        {"variable": "!books", "replacement": "/yacht/Media/Books"},
        {"variable": "!comics", "replacement": "/yacht/Media/Comics"},
        {"variable": "!tv", "replacement": "/yacht/Media/TV"},
        {"variable": "!movies", "replacement": "/yacht/Media/Movies"},
        {"variable": "!pictures", "replacement": "/yacht/Media/Photos"},
        {"variable": "!localtime", "replacement": "/etc/localtime"},
        {"variable": "!logs", "replacement": "/yacht/AppData/Logs"},
        {"variable": "!PUID", "replacement": "1000"},
        {"variable": "!PGID", "replacement": "100"},
    ]
    if os.environ.get("BASE_TEMPLATE", None):
        BASE_TEMPLATE = os.environ.get("BASE_TEMPLATE")
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:////config/data.sqlite"
    )
    COMPOSE_DIR: str = compose_dir_check()
