from fastapi import HTTPException
from fastapi.responses import StreamingResponse
try:
    from sh import docker_compose
except Exception:
    def docker_compose(*args, **kwargs):
        raise RuntimeError("docker-compose not available")
import os
import json
import yaml
import pathlib
import shutil
import docker
import io
import zipfile
import re

from api.db.models.hosts import Host
from api.settings import Settings
from api.utils.compose import find_yml_files, resolve_compose_project_path
from api.utils.docker_hosts import get_docker_client, host_metadata, resolve_host

settings = Settings()
PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def _validated_project_name(project_name):
    if not isinstance(project_name, str):
        raise HTTPException(400, "Invalid project name.")

    normalized = project_name.strip()
    if not normalized or not PROJECT_NAME_PATTERN.fullmatch(normalized):
        raise HTTPException(400, "Invalid project name.")

    return normalized


def _validated_project_dir(project_name):
    return pathlib.Path(
        resolve_compose_project_path(_validated_project_name(project_name))
    )


def _project_metadata_path(project_name):
    return _validated_project_dir(project_name) / ".yacht.json"


def _read_project_metadata(project_name):
    metadata_path = _project_metadata_path(project_name)
    if not metadata_path.exists():
        return {}
    with metadata_path.open("r", encoding="utf-8") as metadata_file:
        try:
            return json.load(metadata_file)
        except json.JSONDecodeError:
            return {}


def _write_project_metadata(project_name, metadata):
    metadata_path = _project_metadata_path(project_name)
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


def _project_host(project_name, db):
    return resolve_host(db, _project_host_id(project_name, db))


def _project_matches_host(project_name, host):
    metadata = _read_project_metadata(project_name)
    if metadata.get("host_id") is None:
        return host.connection_type == "local"
    return metadata["host_id"] == host.id

"""
Runs an action on the specified compose project.
"""


def compose_action(name, action, db, host_id=None):
    files = find_yml_files(settings.COMPOSE_DIR)
    compose = get_compose(name, db, host_id)
    host = _project_host(compose["name"], db)
    if action == "up":
        try:
            _action = docker_compose(
                action,
                "-d",
                _cwd=os.path.dirname(compose["path"]),
                _env=check_dockerhost(host),
            )
        except Exception as exc:
            if hasattr(exc, "stderr"):
                raise HTTPException(400, exc.stderr.decode("UTF-8").rstrip())
            else:
                raise HTTPException(400, exc)
    elif action == "create":
        try:
            _action = docker_compose(
                "up",
                "--no-start",
                _cwd=os.path.dirname(compose["path"]),
                _env=check_dockerhost(host),
            )
        except Exception as exc:
            if hasattr(exc, "stderr"):
                raise HTTPException(400, exc.stderr.decode("UTF-8").rstrip())
            else:
                raise HTTPException(400, exc)
    else:
        try:
            _action = docker_compose(
                action,
                _cwd=os.path.dirname(compose["path"]),
                _env=check_dockerhost(host),
            )
        except Exception as exc:
            if hasattr(exc, "stderr"):
                raise HTTPException(400, exc.stderr.decode("UTF-8").rstrip())
            else:
                raise HTTPException(400, exc)
    if _action.stdout.decode("UTF-8").rstrip():
        _output = _action.stdout.decode("UTF-8").rstrip()
    elif _action.stderr.decode("UTF-8").rstrip():
        _output = _action.stderr.decode("UTF-8").rstrip()
    else:
        _output = "No Output"
    print(f"""Project {compose['name']} {action} successful.""")
    print(f"""Output: """)
    print(_output)
    return get_compose_projects(db, host_id)


"""
Used to include the DOCKER_HOST in the shell env
when someone ups a compose project or returns a
useless var to just clear the shell env.
"""


def check_dockerhost(host):
    if host.connection_type == "docker_api" and host.docker_host:
        return {"DOCKER_HOST": host.docker_host}
    return {"clear_env": "true"}


"""
Used to run docker-compose commands on specific 
apps in compose projects.
"""


def compose_app_action(
    name,
    action,
    app,
    db,
    host_id=None,
):

    files = find_yml_files(settings.COMPOSE_DIR)
    compose = get_compose(name, db, host_id)
    host = _project_host(compose["name"], db)
    print("RUNNING: " + compose["path"] + " docker-compose " + " " + action + " " + app)
    if action == "up":
        try:
            _action = docker_compose(
                "up",
                "-d",
                app,
                _cwd=os.path.dirname(compose["path"]),
                _env=check_dockerhost(host),
            )
        except Exception as exc:
            if hasattr(exc, "stderr"):
                raise HTTPException(400, exc.stderr.decode("UTF-8").rstrip())
            else:
                raise HTTPException(400, exc)
    elif action == "create":
        try:
            _action = docker_compose(
                "up",
                "--no-start",
                app,
                _cwd=os.path.dirname(compose["path"]),
                _env=check_dockerhost(host),
            )
        except Exception as exc:
            if hasattr(exc, "stderr"):
                raise HTTPException(400, exc.stderr.decode("UTF-8").rstrip())
            else:
                raise HTTPException(400, exc)
    elif action == "rm":
        try:
            _action = docker_compose(
                "rm",
                "--force",
                "--stop",
                app,
                _cwd=os.path.dirname(compose["path"]),
                _env=check_dockerhost(host),
            )
        except Exception as exc:
            if hasattr(exc, "stderr"):
                raise HTTPException(400, exc.stderr.decode("UTF-8").rstrip())
            else:
                raise HTTPException(400, exc)
    else:
        try:
            _action = docker_compose(
                action,
                app,
                _cwd=os.path.dirname(compose["path"]),
                _env=check_dockerhost(host),
            )
        except Exception as exc:
            if hasattr(exc, "stderr"):
                raise HTTPException(400, exc.stderr.decode("UTF-8").rstrip())
            else:
                raise HTTPException(400, exc)
    if _action.stdout.decode("UTF-8").rstrip():
        output = _action.stdout.decode("UTF-8").rstrip()
    elif _action.stderr.decode("UTF-8").rstrip():
        output = _action.stderr.decode("UTF-8").rstrip()
    else:
        output = "No Output"
    print(f"""Project {compose['name']} App {name} {action} successful.""")
    print(f"""Output: """)
    print(output)
    return get_compose_projects(db, host_id)


"""
Checks for compose projects in the COMPOSE_DIR and
returns most of the info inside them.
"""


def get_compose_projects(db, host_id=None):
    files = find_yml_files(settings.COMPOSE_DIR)
    host = resolve_host(db, host_id)

    projects = []
    for project, file in files.items():
        if not _project_matches_host(project, host):
            continue
        volumes = []
        networks = []
        services = {}
        compose = open(file)
        loaded_compose = yaml.load(compose, Loader=yaml.SafeLoader)
        if loaded_compose:
            if loaded_compose.get("volumes"):
                for volume in loaded_compose.get("volumes"):
                    volumes.append(volume)
            if loaded_compose.get("networks"):
                for network in loaded_compose.get("networks"):
                    networks.append(network)
            if loaded_compose.get("services"):
                for service in loaded_compose.get("services"):
                    services[service] = loaded_compose["services"][service]
            _project = {
                "name": project,
                "path": file,
                "version": loaded_compose.get("version", "3.9"),
                "services": services,
                "volumes": volumes,
                "networks": networks,
                "host_id": host.id,
                "YachtHost": host_metadata(host),
            }
            projects.append(_project)
        else:
            print("ERROR: " + file + " is invalid or empty!")
    return projects


"""
Returns detailed information on a specific compose
project.
"""


def get_compose(name, db, host_id=None):
    try:
        project_dir = resolve_compose_project_path(name)
        project_host = _project_host(name, db)
        if host_id is not None and project_host.id != host_id:
            raise HTTPException(404, "Project not found on selected host.")
        files = find_yml_files(project_dir)
    except Exception as exc:
        raise HTTPException(exc.status_code, exc.detail)
    for project, file in files.items():
        if name == project:
            networks = []
            volumes = []
            services = {}
            compose = open(file)
            try:
                loaded_compose = yaml.load(compose, Loader=yaml.SafeLoader)
            except yaml.scanner.ScannerError as exc:
                raise HTTPException(422, f"{exc.problem_mark.line}:{exc.problem_mark.column} - {exc.problem}")
            if loaded_compose.get("volumes"):
                for volume in loaded_compose.get("volumes"):
                    volumes.append(volume)
            if loaded_compose.get("networks"):
                for network in loaded_compose.get("networks"):
                    networks.append(network)
            if loaded_compose.get("services"):
                for service in loaded_compose.get("services"):
                    services[service] = loaded_compose["services"][service]
            _content = open(file)
            content = _content.read()
            compose_object = {
                "name": project,
                "path": file,
                "version": loaded_compose.get("version", "-"),
                "services": services,
                "volumes": volumes,
                "networks": networks,
                "content": content,
                "host_id": project_host.id,
                "YachtHost": host_metadata(project_host),
            }
            return compose_object
    else:
        raise HTTPException(404, "Project " + name + " not found")


"""
Creates a compose directory (if one isn't there
already) with the name of the project. Then writes
the content of compose.content to it.
"""


def write_compose(compose, db):
    project_name = _validated_project_name(compose.name)
    project_dir = _validated_project_dir(project_name)
    host = resolve_host(db, compose.host_id)
    if not project_dir.exists():
        try:
            project_dir.mkdir(parents=True)
        except Exception as exc:
            raise HTTPException(exc.status_code, exc.detail)
    compose_file = project_dir / "docker-compose.yml"
    with compose_file.open("w", encoding="utf-8") as f:
        try:
            f.write(compose.content)
            f.close()
        except TypeError as exc:
            if exc.args[0] == "write() argument must be str, not None":
                raise HTTPException(
                    status_code=422, detail="Compose file cannot be empty."
                )
        except Exception as exc:
            raise HTTPException(exc.status_code, exc.detail)
    _write_project_metadata(project_name, {"host_id": host.id})

    return get_compose(name=compose.name, db=db, host_id=host.id)


"""
Deletes a compose project after checking to see if
it exists. This also deletes all files in the folder.
"""


def delete_compose(project_name, db, host_id=None):
    project_name = _validated_project_name(project_name)
    project_dir = _validated_project_dir(project_name)
    compose_file = project_dir / "docker-compose.yml"
    project_host = _project_host(project_name, db)
    if host_id is not None and project_host.id != host_id:
        raise HTTPException(404, "Project not found on selected host.")

    if not project_dir.exists():
        raise HTTPException(404, "Project directory not found.")
    elif not compose_file.exists():
        raise HTTPException(404, "Project docker-compose.yml not found.")
    else:
        try:
            with compose_file.open("r", encoding="utf-8"):
                pass
        except OSError as exc:
            raise HTTPException(400, exc.strerror)
    try:
        shutil.rmtree(project_dir)
    except Exception as exc:
        raise HTTPException(exc.status_code, exc.strerror)
    return get_compose_projects(db, host_id)


def generate_support_bundle(project_name, db, host_id=None):
    project_name = _validated_project_name(project_name)
    project_dir = _validated_project_dir(project_name)
    files = find_yml_files(project_dir)
    if project_name in files:
        project_host = _project_host(project_name, db)
        if host_id is not None and project_host.id != host_id:
            raise HTTPException(404, "Project not found on selected host.")
        _, dclient = get_docker_client(db, project_host.id)
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as zf, open(files[project_name], "r") as fp:
            compose = yaml.load(fp, Loader=yaml.SafeLoader)
            # print(compose)
            # print(compose.get("services"))
            for _service in compose.get("services"):
                print()
                if len(compose.get("services").keys()) < 2:
                    try:
                        if compose.get("services")[_service].get("container_name"):
                            service = dclient.containers.get(
                                compose.get("services")[_service].get("container_name")
                            )
                        else:
                            service = dclient.containers.get(_service)
                    except docker.errors.NotFound as exc:
                        raise HTTPException(
                            exc.status_code,
                            detail="container " + _service + " not found",
                        )
                else:
                    try:
                        if compose.get("services")[_service].get("container_name"):
                            service = dclient.containers.get(
                                compose.get("services")[_service].get("container_name")
                            )
                        else:
                            service = dclient.containers.get(
                                project_name.lower() + "_" + _service + "_1"
                            )
                    except docker.errors.NotFound as exc:
                        raise HTTPException(
                            exc.status_code,
                            detail="container " + _service + " not found",
                        )
                service_log = service.logs()
                zf.writestr(f"{_service}.log", service_log)
            fp.seek(0)
            # It is possible that ".write(...)" has better memory management here.
            zf.writestr("docker-compose.yml", fp.read())
        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type="application/x-zip-compressed",
            headers={
                "Content-Disposition": f"attachment;filename={project_name}_bundle.zip"
            },
        )
    else:
        raise HTTPException(404, f"Project {project_name} not found.")
