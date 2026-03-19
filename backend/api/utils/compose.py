from ..settings import Settings
from fastapi import HTTPException
import os
import pathlib
import re

settings = Settings()
PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
COMPOSE_FILE_PATTERNS = (
    "compose.yml",
    "compose.yaml",
    "docker-compose.yml",
    "docker-compose.yaml",
)


def get_compose_base_dir():
    base_dir = os.path.realpath(os.path.abspath(settings.COMPOSE_DIR))
    return base_dir.rstrip(os.sep)


def get_compose_base_path():
    return pathlib.Path(get_compose_base_dir())


def _ensure_within_compose_base(path, must_exist=False):
    base_dir = get_compose_base_path().resolve()
    try:
        resolved = pathlib.Path(path).resolve(strict=must_exist)
    except FileNotFoundError as exc:
        raise HTTPException(404, "Project path not found.") from exc

    try:
        resolved.relative_to(base_dir)
    except ValueError as exc:
        raise HTTPException(400, "Invalid project path.") from exc

    return resolved


def _resolve_compose_descendant(*path_parts, must_exist=False):
    base_dir = get_compose_base_path().resolve()
    candidate = base_dir.joinpath(*path_parts)
    return _ensure_within_compose_base(candidate, must_exist=must_exist)


def _validated_project_name(project_name):
    if not isinstance(project_name, str):
        raise HTTPException(400, "Invalid project name.")

    normalized = project_name.strip()
    if not normalized or not PROJECT_NAME_PATTERN.fullmatch(normalized):
        raise HTTPException(400, "Invalid project name.")
    if "/" in normalized or "\\" in normalized:
        raise HTTPException(400, "Invalid project name.")
    if normalized in {".", ".."} or normalized != os.path.basename(normalized):
        raise HTTPException(400, "Invalid project name.")

    return normalized


def resolve_compose_project_path(project_name):
    """
    Resolve a compose project directory from a project name.
    """
    validated_name = _validated_project_name(project_name)
    project_dir = _resolve_compose_descendant(validated_name)
    return os.fspath(project_dir)


def resolve_compose_project_dir(project_name, must_exist=False):
    validated_name = _validated_project_name(project_name)
    return _resolve_compose_descendant(validated_name, must_exist=must_exist)


def resolve_compose_file(project_name, filename="docker-compose.yml", must_exist=False):
    project_dir = resolve_compose_project_dir(project_name, must_exist=must_exist)
    compose_file = _ensure_within_compose_base(
        project_dir / filename,
        must_exist=must_exist,
    )
    return compose_file


def _compose_file_matches(root_dir):
    """
    Find docker compose files inside a validated compose directory.
    """
    safe_root = _ensure_within_compose_base(root_dir)
    if not safe_root.exists():
        return {}

    matches = {}
    for pattern in COMPOSE_FILE_PATTERNS:
        for candidate in safe_root.rglob(pattern):
            candidate = _ensure_within_compose_base(candidate, must_exist=True)
            key = candidate.parent.name
            matches[key] = os.fspath(candidate)
    return matches


def find_yml_files():
    """
    Find docker compose files under the compose base directory.
    """
    return _compose_file_matches(get_compose_base_path())


def find_project_yml_files(project_name):
    """
    Find docker compose files for a single validated project.
    """
    project_dir = resolve_compose_project_dir(project_name)
    return _compose_file_matches(project_dir)


def resolve_project_compose_manifest(project_name):
    files = find_project_yml_files(project_name)
    validated_name = _validated_project_name(project_name)
    if validated_name not in files:
        raise HTTPException(404, f"Project {validated_name} not found.")
    return _ensure_within_compose_base(files[validated_name], must_exist=True)
