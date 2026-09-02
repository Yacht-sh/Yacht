import os
import subprocess  # nosec B404 - required to invoke the Docker Compose CLI

from fastapi import HTTPException
import logging

from api.actions.compose_projects import (
    delete_compose,
    generate_support_bundle,
    get_compose,
    get_compose_projects,
    get_project_host,
    write_compose,
)

logger = logging.getLogger(__name__)
class _ComposeResult:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

def _run_docker_compose(*args, cwd=None, env=None):
    command = ["docker", "compose", *args]
    completed = subprocess.run(  # nosec B603 - command is built without a shell
        command,
        cwd=cwd,
        env=env if env is not None else os.environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return _ComposeResult(completed.returncode, completed.stdout, completed.stderr)

"""
Runs an action on the specified compose project.
"""


def compose_action(name, action, db, host_id=None):
    compose = get_compose(name, db, host_id)
    host = get_project_host(compose["name"], db)
    if action == "up":
        _action = _run_compose_command(host, compose, action, "-d")
    elif action == "create":
        _action = _run_compose_command(host, compose, "up", "--no-start")
    else:
        _action = _run_compose_command(host, compose, action)
    _output = _compose_output(_action)
    logger.info(f"""Project {compose['name']} {action} successful.""")

    logger.info(f"""Output: """)

    logger.info(_output)

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
    compose = get_compose(name, db, host_id)
    host = get_project_host(compose["name"], db)
    logger.info("RUNNING: " + compose["path"] + " docker-compose " + " " + action + " " + app)

    if action == "up":
        _action = _run_compose_command(host, compose, "up", "-d", app)
    elif action == "create":
        _action = _run_compose_command(host, compose, "up", "--no-start", app)
    elif action == "rm":
        _action = _run_compose_command(host, compose, "rm", "--force", "--stop", app)
    else:
        _action = _run_compose_command(host, compose, action, app)
    output = _compose_output(_action)
    logger.info(f"""Project {compose['name']} App {name} {action} successful.""")

    logger.info(f"""Output: """)

    logger.info(output)

    return get_compose_projects(db, host_id)


def _run_compose_command(host, compose, *args):
    try:
        return _run_docker_compose(
            *args,
            cwd=os.path.dirname(compose["path"]),
            env=check_dockerhost(host),
        )
    except Exception as exc:
        if hasattr(exc, "stderr"):
            raise HTTPException(400, exc.stderr.decode("UTF-8").rstrip())
        raise HTTPException(400, exc)


def _compose_output(action_result):
    if action_result.stdout:
        return action_result.stdout.decode("UTF-8").rstrip()
    if action_result.stderr:
        return action_result.stderr.decode("UTF-8").rstrip()
    return "No Output"
