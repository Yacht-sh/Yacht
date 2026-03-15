from ..settings import Settings
from fastapi import HTTPException
import os
import fnmatch
import pathlib

settings = Settings()


def get_compose_base_dir():
    base_dir = os.path.realpath(os.path.abspath(settings.COMPOSE_DIR))
    return base_dir.rstrip(os.sep)


def resolve_compose_path(path):
    """
    Resolve a path and ensure it stays inside COMPOSE_DIR.
    """
    base_dir = get_compose_base_dir()
    if not os.path.isabs(path):
        candidate = os.path.join(base_dir, path)
    else:
        candidate = path
    resolved = os.path.realpath(os.path.abspath(candidate))
    try:
        common = os.path.commonpath([base_dir, resolved])
    except ValueError:
        raise HTTPException(400, "Invalid compose path.")
    base_dir_with_sep = base_dir if base_dir.endswith(os.sep) else base_dir + os.sep
    if common != base_dir or not (
        resolved == base_dir or resolved.startswith(base_dir_with_sep)
    ):
        raise HTTPException(400, "Path escapes compose directory.")
    return resolved


def ensure_compose_path(path):
    base_dir = pathlib.Path(get_compose_base_dir()).resolve()
    resolved_path = pathlib.Path(resolve_compose_path(path)).resolve()
    try:
        resolved_path.relative_to(base_dir)
    except ValueError as exc:
        raise HTTPException(400, "Path escapes compose directory.") from exc
    return resolved_path


def resolve_compose_project_path(project_name):
    """
    Resolve a compose project directory from a project name.
    """
    if not project_name or project_name.strip() == "":
        raise HTTPException(400, "Project name cannot be empty.")
    if "/" in project_name or "\\" in project_name:
        raise HTTPException(400, "Invalid project name.")
    if project_name in {".", ".."} or project_name != os.path.basename(project_name):
        raise HTTPException(400, "Invalid project name.")
    return resolve_compose_path(os.path.join(get_compose_base_dir(), project_name))


def _find_yml_files_in_dir(root_dir):
    """
    Find docker compose files inside a validated compose directory.
    """
    safe_root_dir = ensure_compose_path(root_dir)
    matches = {}
    for root, _, filenames in os.walk(os.fspath(safe_root_dir), followlinks=False):
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
    return _find_yml_files_in_dir(get_compose_base_dir())


def find_project_yml_files(project_name):
    """
    Find docker compose files for a single validated project.
    """
    return _find_yml_files_in_dir(resolve_compose_project_path(project_name))


def get_readme_file(path):
    """
    find case insensitive readme.md in path and return the contents
    """

    readme = None

    safe_path = resolve_compose_path(path)
    for file in os.listdir(safe_path):
        file_path = os.path.join(safe_path, file)
        if file.lower() == "readme.md" and os.path.isfile(file_path):
            with open(file_path) as readme_file:
                readme = readme_file.read()
            break

    return readme


def get_logo_file(path):
    """
    find case insensitive logo.png in path and return the contents
    """

    logo = None

    safe_path = resolve_compose_path(path)
    for file in os.listdir(safe_path):
        file_path = os.path.join(safe_path, file)
        if file.lower() == "logo.png" and os.path.isfile(file_path):
            with open(file_path) as logo_file:
                logo = logo_file.read()
            break

    return logo
