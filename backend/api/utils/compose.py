from ..settings import Settings
from fastapi import HTTPException
import os
import fnmatch
import pathlib
import re

settings = Settings()
PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def get_compose_base_dir():
    base_dir = os.path.realpath(os.path.abspath(settings.COMPOSE_DIR))
    return base_dir.rstrip(os.sep)


def get_compose_base_path():
    return pathlib.Path(get_compose_base_dir())


def _validated_project_name(project_name):
    if not isinstance(project_name, str):
        raise HTTPException(400, "Invalid project name.")

    normalized = project_name.strip()
    if not normalized or not PROJECT_NAME_PATTERN.fullmatch(normalized):
        raise HTTPException(400, "Invalid project name.")
    if normalized in {".", ".."} or normalized != os.path.basename(normalized):
        raise HTTPException(400, "Invalid project name.")

    return normalized


def resolve_compose_project_path(project_name):
    """
    Resolve a compose project directory from a project name.
    """
    validated_name = _validated_project_name(project_name)
    return os.fspath(get_compose_base_path() / validated_name)


def _collect_yml_files(root_dir):
    """
    Find docker compose files inside a validated compose directory.
    """
    matches = {}
    for root, _, filenames in os.walk(os.fspath(root_dir), followlinks=False):
        for _ in set().union(
            fnmatch.filter(filenames, "compose.yml"),
            fnmatch.filter(filenames, "compose.yaml"),
            fnmatch.filter(filenames, "docker-compose.yml"),
            fnmatch.filter(filenames, "docker-compose.yaml"),
        ):
            key = os.path.basename(root)
            matches[key] = os.path.realpath(os.path.join(root, _))
    return matches


def find_yml_files():
    """
    Find docker compose files under the compose base directory.
    """
    return _collect_yml_files(get_compose_base_path())


def find_project_yml_files(project_name):
    """
    Find docker compose files for a single validated project.
    """
    return _collect_yml_files(get_compose_base_path() / _validated_project_name(project_name))
