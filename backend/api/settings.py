import os
import secrets
from pydantic import BaseSettings

basedir = os.path.abspath(os.path.dirname(__file__))


def compose_dir_check():
    if not os.environ.get("COMPOSE_DIR", "config/compose/").endswith("/"):
        os.environ["COMPOSE_DIR"] += "/"
    return os.environ.get("COMPOSE_DIR", "config/compose/")


class Settings(BaseSettings):
    app_name: str = "Yacht API"
    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(16))
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "pass")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@yacht.local")
    ACCESS_TOKEN_EXPIRES = os.environ.get("ACCESS_TOKEN_EXPIRES", 900)
    REFRESH_TOKEN_EXPIRES = os.environ.get("REFRESH_TOKEN_EXPIRES", 2592000)
    SAME_SITE_COOKIES = os.environ.get("SAME_SITE_COOKIES", "lax")
    DISABLE_AUTH = os.environ.get("DISABLE_AUTH", False)
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
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///config/data.sqlite"
    )
    COMPOSE_DIR = compose_dir_check()
