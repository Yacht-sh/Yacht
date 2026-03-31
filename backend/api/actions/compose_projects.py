import io
import json
import re
import shutil
import zipfile

import docker
import yaml
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from api.db.models.hosts import Host
from api.utils.compose import (
    find_project_yml_files,
    find_yml_files,
    resolve_compose_file,
    resolve_compose_project_dir,
    resolve_project_compose_manifest,
)
from api.utils.docker_hosts import get_docker_client, host_metadata, resolve_host

PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def _validated_project_name(project_name):
    if not isinstance(project_name, str):
        raise HTTPException(400, "Invalid project name.")

    normalized = project_name.strip()
    if not normalized or not PROJECT_NAME_PATTERN.fullmatch(normalized):
        raise HTTPException(400, "Invalid project name.")
    if "/" in normalized or "\\" in normalized:
        raise HTTPException(400, "Invalid project name.")
    if normalized in {".", ".."}:
        raise HTTPException(400, "Invalid project name.")

    return normalized


def _existing_project_dir(project_name):
    project_dir = resolve_compose_project_dir(project_name)
    if project_dir.exists() and project_dir.is_dir():
        return project_dir
    return None


def _project_metadata_path_for_dir(project_dir):
    return project_dir / ".yacht.json"


def _read_project_metadata(project_name):
    project_dir = _existing_project_dir(project_name)
    if project_dir is None:
        return {}
    metadata_path = _project_metadata_path_for_dir(project_dir)
    if not metadata_path.is_file():
        return {}
    with metadata_path.open("r", encoding="utf-8") as metadata_file:
        try:
            return json.load(metadata_file)
        except json.JSONDecodeError:
            return {}


def _write_project_metadata(project_dir, metadata):
    metadata_path = _project_metadata_path_for_dir(project_dir)
    with metadata_path.open("w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file)


def _project_host_id(project_name, db):
    metadata = _read_project_metadata(project_name)
    if metadata.get("host_id") is not None:
        return metadata["host_id"]
    local_host = db.query(Host).filter(Host.connection_type == "local").first()
    if local_host is None:
        return resolve_host(db).id
    return local_host.id


def get_project_host(project_name, db):
    return resolve_host(db, _project_host_id(project_name, db))


def _project_matches_host(project_name, host):
    metadata = _read_project_metadata(project_name)
    if metadata.get("host_id") is None:
        return host.connection_type == "local"
    return metadata["host_id"] == host.id


def _load_compose_yaml(compose_path):
    try:
        with open(compose_path, encoding="utf-8") as compose_file:
            return yaml.load(compose_file, Loader=yaml.SafeLoader)
    except yaml.scanner.ScannerError as exc:
        raise HTTPException(
            422, f"{exc.problem_mark.line}:{exc.problem_mark.column} - {exc.problem}"
        ) from exc
    except OSError as exc:
        raise HTTPException(400, exc.strerror) from exc


def _manifest_details(project_name, compose_path, host):
    loaded_compose = _load_compose_yaml(compose_path)
    if not loaded_compose:
        raise HTTPException(422, "Compose file is invalid or empty.")

    services = loaded_compose.get("services") or {}
    volumes = list((loaded_compose.get("volumes") or {}).keys())
    networks = list((loaded_compose.get("networks") or {}).keys())

    return {
        "name": project_name,
        "path": compose_path,
        "version": loaded_compose.get("version", "3.9"),
        "services": services,
        "volumes": volumes,
        "networks": networks,
        "host_id": host.id,
        "YachtHost": host_metadata(host),
    }


def get_compose_projects(db, host_id=None):
    files = find_yml_files()
    host = resolve_host(db, host_id)

    projects = []
    for project_name, compose_path in files.items():
        if not _project_matches_host(project_name, host):
            continue
        try:
            projects.append(_manifest_details(project_name, compose_path, host))
        except HTTPException as exc:
            if exc.status_code == 422:
                print(f"ERROR: {compose_path} is invalid or empty!")
                continue
            raise
    return projects


def get_compose(name, db, host_id=None):
    try:
        project_host = get_project_host(name, db)
        if host_id is not None and project_host.id != host_id:
            raise HTTPException(404, "Project not found on selected host.")
        files = find_project_yml_files(name)
    except HTTPException:
        raise

    for project_name, compose_path in files.items():
        if name != project_name:
            continue
        compose_object = _manifest_details(project_name, compose_path, project_host)
        with open(compose_path, encoding="utf-8") as content_file:
            compose_object["content"] = content_file.read()
        if compose_object["version"] == "3.9":
            compose_object["version"] = "-"
        return compose_object

    raise HTTPException(404, "Project " + name + " not found")


def write_compose(compose, db):
    project_name = _validated_project_name(compose.name)
    project_dir = resolve_compose_project_dir(project_name)
    host = resolve_host(db, compose.host_id)

    if not project_dir.exists():
        try:
            project_dir.mkdir(parents=True)
        except OSError as exc:
            raise HTTPException(400, exc.strerror) from exc

    compose_file = resolve_compose_file(project_name)
    with compose_file.open("w", encoding="utf-8") as compose_handle:
        try:
            compose_handle.write(compose.content)
        except TypeError as exc:
            if exc.args[0] == "write() argument must be str, not None":
                raise HTTPException(422, detail="Compose file cannot be empty.")
            raise HTTPException(422, "Invalid compose content.") from exc
        except OSError as exc:
            raise HTTPException(400, exc.strerror) from exc

    _write_project_metadata(project_dir, {"host_id": host.id})
    return get_compose(name=compose.name, db=db, host_id=host.id)


def delete_compose(project_name, db, host_id=None):
    project_name = _validated_project_name(project_name)
    project_dir = resolve_compose_project_dir(project_name, must_exist=True)
    compose_file = resolve_project_compose_manifest(project_name)
    project_host = get_project_host(project_name, db)
    if host_id is not None and project_host.id != host_id:
        raise HTTPException(404, "Project not found on selected host.")

    if not compose_file.is_file():
        raise HTTPException(404, "Project compose manifest not found.")

    try:
        shutil.rmtree(project_dir)
    except OSError as exc:
        raise HTTPException(400, exc.strerror) from exc

    return get_compose_projects(db, host_id)


def _resolve_service_container(dclient, compose, project_name, service_name):
    service_config = compose["services"][service_name]
    container_name = service_config.get("container_name")
    if container_name:
        lookup_name = container_name
    elif len(compose["services"].keys()) < 2:
        lookup_name = service_name
    else:
        lookup_name = f"{project_name.lower()}_{service_name}_1"

    try:
        return dclient.containers.get(lookup_name)
    except docker.errors.NotFound as exc:
        raise HTTPException(exc.status_code, detail=f"container {service_name} not found") from exc


def generate_support_bundle(project_name, db, host_id=None):
    project_name = _validated_project_name(project_name)
    compose_path = resolve_project_compose_manifest(project_name)
    project_host = get_project_host(project_name, db)
    if host_id is not None and project_host.id != host_id:
        raise HTTPException(404, "Project not found on selected host.")

    _, dclient = get_docker_client(db, project_host.id)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive, compose_path.open(
        "r", encoding="utf-8"
    ) as compose_file:
        compose = yaml.load(compose_file, Loader=yaml.SafeLoader)
        for service_name in compose.get("services") or {}:
            service = _resolve_service_container(dclient, compose, project_name, service_name)
            archive.writestr(f"{service_name}.log", service.logs())
        compose_file.seek(0)
        archive.writestr("docker-compose.yml", compose_file.read())

    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/x-zip-compressed",
        headers={
            "Content-Disposition": f"attachment;filename={project_name}_bundle.zip"
        },
    )
