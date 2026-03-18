from os import stat
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from api.db.schemas.apps import DeployLogs, DeployForm, AppLogs, Processes
from api.utils.apps import (
    conv_caps2data,
    conv_devices2data,
    conv_env2data,
    conv_image2data,
    conv_labels2data,
    conv_portlabels2data,
    conv_ports2data,
    conv_restart2data,
    conv_sysctls2data,
    conv_volumes2data,
    conv_cpus2data,
    _check_updates,
    calculate_cpu_percent,
    calculate_cpu_percent2,
    format_bytes,
)
from api.utils.docker_hosts import (
    docker_base_url,
    get_docker_client,
    host_metadata,
    resolve_host,
)
from api.utils.templates import conv2dict

import yaml
import json
import io
import zipfile
import time
import re
import docker
import asyncio
import aiostream
import aiodocker
from aiodocker.containers import DockerContainer


"""
Returns all running apps in a list
"""


def _annotate_with_host(attrs, host):
    attrs.update(conv2dict("YachtHost", host_metadata(host)))
    return attrs


def get_running_apps(db, host_id=None):
    apps_list = []
    host, dclient = get_docker_client(db, host_id)
    apps = dclient.containers.list()
    for app in apps:
        attrs = app.attrs
        attrs.update(conv2dict("name", app.name))
        attrs.update(conv2dict("ports", app.ports))
        attrs.update(conv2dict("short_id", app.short_id))
        apps_list.append(_annotate_with_host(attrs, host))

    return apps_list


"""
Checks repo digest for app and compares it to image
digest to see if there's an update available.

Limitation: this assumes a single repo digest for the image.
"""


def check_app_update(app_name, db, host_id=None):
    host, dclient = get_docker_client(db, host_id)
    try:
        app = dclient.containers.get(app_name)
    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )

    if app.attrs["Config"]["Image"]:
        if _check_updates(app.attrs["Config"]["Image"], dclient=dclient):
            app.attrs.update(conv2dict("isUpdatable", True))
    app.attrs.update(conv2dict("name", app.name))
    app.attrs.update(conv2dict("ports", app.ports))
    app.attrs.update(conv2dict("short_id", app.short_id))
    return _annotate_with_host(app.attrs, host)


"""
Gets all apps in a list and add some easy access to
properties that aren't in the app attributes
"""


def get_apps(db, host_id=None):
    apps_list = []
    try:
        host, dclient = get_docker_client(db, host_id)
    except docker.errors.DockerException as exc:
        raise HTTPException(status_code=500, detail=exc.args)
    try:
        apps = dclient.containers.list(all=True)
    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )
    for app in apps:
        attrs = app.attrs

        attrs.update(conv2dict("name", app.name))
        attrs.update(conv2dict("ports", app.ports))
        attrs.update(conv2dict("short_id", app.short_id))
        apps_list.append(_annotate_with_host(attrs, host))

    return apps_list


"""
Get a single app by the container name and some easy 
access to properties that aren't in the app 
attributes
"""


def get_app(app_name, db, host_id=None):
    host, dclient = get_docker_client(db, host_id)
    try:
        app = dclient.containers.get(app_name)
    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )
    attrs = app.attrs

    attrs.update(conv2dict("ports", app.ports))
    attrs.update(conv2dict("short_id", app.short_id))
    attrs.update(conv2dict("name", app.name))

    return _annotate_with_host(attrs, host)


"""
Get processes running in an app.
"""


def get_app_processes(app_name, db, host_id=None):
    _, dclient = get_docker_client(db, host_id)
    app = dclient.containers.get(app_name)
    if app.status == "running":
        processes = app.top()
        return Processes(Processes=processes["Processes"], Titles=processes["Titles"])
    else:
        return None


"""
Get app logs (this isn't in use as logs are served
via a websocket in routers so they're realtime)
"""


def get_app_logs(app_name, db, host_id=None):
    _, dclient = get_docker_client(db, host_id)
    app = dclient.containers.get(app_name)
    if app.status == "running":
        return AppLogs(logs=app.logs())
    else:
        return None


"""
Deploy a new app. Format is available in 
../db/schemas/apps.py
"""


def deploy_app(template: DeployForm, db):
    try:
        launch = launch_app(
            db,
            template.name,
            conv_image2data(template.image),
            conv_restart2data(template.restart_policy),
            template.command,
            conv_ports2data(template.ports, template.network, template.network_mode),
            conv_portlabels2data(template.ports),
            template.network_mode,
            template.network,
            conv_volumes2data(template.volumes),
            conv_env2data(template.env),
            conv_devices2data(template.devices),
            conv_labels2data(template.labels),
            conv_sysctls2data(template.sysctls),
            conv_caps2data(template.cap_add),
            conv_cpus2data(template.cpus),
            template.mem_limit,
            edit=template.edit or False,
            _id=template.id or None,
            host_id=template.host_id,
        )
    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )
    print("done deploying")

    return DeployLogs(logs=launch.logs())


"""
Merge utility used for combining portlabels and
labels into a single variable
"""


def Merge(dict1, dict2):
    if dict1 and dict2:
        dict2.update(dict1)
        return dict2
    elif dict1:
        return dict1
    elif dict2:
        return dict2
    else:
        return None


def _current_container_id():
    try:
        with open("/proc/self/cgroup", encoding="utf-8") as cgroup_file:
            for line in cgroup_file:
                candidate = line.strip().split("/")[-1]
                if not candidate:
                    continue
                if candidate.endswith(".scope"):
                    candidate = candidate[:-6]
                for prefix in ("docker-", "libpod-", "cri-containerd-"):
                    if candidate.startswith(prefix):
                        candidate = candidate[len(prefix) :]
                        break
                if re.fullmatch(r"[0-9a-f]{12,64}", candidate):
                    return candidate
    except OSError as exc:
        raise HTTPException(500, f"Unable to read container metadata: {exc.strerror}") from exc

    raise HTTPException(500, "Unable to determine Yacht container ID")


"""
This function actually runs the docker run command.
It also checks if edit is set to true so it can 
remove the container you're editing before deploying
a new one.
"""


def launch_app(
    db,
    name,
    image,
    restart_policy,
    command,
    ports,
    portlabels,
    network_mode,
    network,
    volumes,
    env,
    devices,
    labels,
    sysctls,
    caps,
    cpus,
    mem_limit,
    edit,
    _id,
    host_id=None,
):
    _, dclient = get_docker_client(db, host_id)
    if edit == True:
        try:
            running_app = dclient.containers.get(_id)
            try:
                running_app.remove(force=True)
            except docker.errors.DockerException:
                raise
        except docker.errors.NotFound:
            # User probably changed the name so it doesn't conflict. If this is the case we'll just spin up a second container.
            running_app = None

    combined_labels = Merge(portlabels, labels)
    try:
        lauch = dclient.containers.run(
            name=name,
            image=image,
            restart_policy=restart_policy,
            command=command,
            ports=ports,
            network=network,
            network_mode=network_mode,
            volumes=volumes,
            environment=env,
            sysctls=sysctls,
            labels=combined_labels,
            devices=devices,
            cap_add=caps,
            nano_cpus=cpus,
            mem_limit=mem_limit,
            detach=True,
        )
    except docker.errors.APIError as e:
        if e.status_code == 500:
            failed_app = dclient.containers.get(name)
            failed_app.remove()
        raise HTTPException(
            status_code=e.status_code, detail=e.explanation
        )

    print(
        f"""Container started successfully.
       Name: {name},
      Image: {image},
      Ports: {ports},
    Volumes: {volumes},
        Env: {env}"""
    )
    return lauch


"""
Runs an app action (ie. docker stop, docker start, etc.)
"""


def app_action(app_name, action, db, host_id=None):
    err = None
    _, dclient = get_docker_client(db, host_id)
    app = dclient.containers.get(app_name)
    _action = getattr(app, action)
    if action == "remove":
        try:
            _action(force=True)
        except Exception as exc:
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.explanation
            )
    else:
        try:
            _action()
        except Exception as exc:
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.explanation
            )
    apps_list = get_apps(db=db, host_id=host_id)
    return apps_list


"""
Spins up a watchtower container that uses the --run-once
and --cleanup flags and targets a container by name
"""


def app_update(app_name, db, host_id=None):
    _, dclient = get_docker_client(db, host_id)
    try:
        old = dclient.containers.get(app_name)
    except Exception as exc:
        print(exc)
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail="Unable to get container ID",
            )
        else:
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.explanation
            )

    volumes = {"/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}}
    try:
        updater = dclient.containers.run(
            image="ghcr.io/nicholas-fedor/watchtower:latest",
            command="--cleanup --run-once " + old.name,
            remove=True,
            detach=True,
            volumes=volumes,
        )
    except Exception as exc:
        print(exc)
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )

    print("**** Updating " + old.name + "****")
    result = updater.wait(timeout=120)
    print(result)
    time.sleep(1)
    return get_apps(db=db, host_id=host_id)


"""
Checks for current docker id (the one yacht is running
in) and then launches the next function in a 
background task.
"""


def _update_self(background_tasks):
    dclient = docker.from_env()
    yacht_id = _current_container_id()
    try:
        yacht = dclient.containers.get(yacht_id)
    except Exception as exc:
        print(exc)
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail="Unable to get Yacht container ID",
            )
        else:
            status_code = 500
            detail = exc.args[0]
            raise HTTPException(status_code=status_code, detail=detail)
    background_tasks.add_task(update_self_in_background, yacht)
    return {"result": "successful"}


"""
Spins up a watchtower instance with --cleanup and 
--run-once pointed at the current ID of yacht.
"""


def update_self_in_background(yacht):
    dclient = docker.from_env()
    volumes = {"/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}}
    print("**** Updating " + yacht.name + "****")
    dclient.containers.run(
        image="ghcr.io/nicholas-fedor/watchtower:latest",
        command="--cleanup --run-once " + yacht.name,
        remove=True,
        detach=True,
        volumes=volumes,
    )


"""
Checks current docker id and compares the repo digest
to the local digest to see if there's an updata available.
"""


def check_self_update():
    dclient = docker.from_env()
    yacht_id = _current_container_id()
    try:
        yacht = dclient.containers.get(yacht_id)
    except Exception as exc:
        print(exc)
        if hasattr(exc, "response") and exc.response.status_code == 404:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail="Unable to get Yacht container ID",
            )
        elif hasattr(exc, "response"):
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.explanation
            )
        else:
            raise HTTPException(status_code=400, detail=exc.args)

    return _check_updates(yacht.image.tags[0])


def generate_support_bundle(app_name, db, host_id=None):
    _, dclient = get_docker_client(db, host_id)
    if dclient.containers.get(app_name):
        app = dclient.containers.get(app_name)
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as zf:
            # print(compose)
            # print(compose.get("services"))
            attrs = app.attrs
            service_log = app.logs()
            zf.writestr(f"{app_name}.log", service_log)
            zf.writestr(f"{app_name}-config.yml", yaml.dump(attrs))
            # It is possible that ".write(...)" has better memory management here.
        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type="application/x-zip-compressed",
            headers={
                "Content-Disposition": f"attachment;filename={app_name}_bundle.zip"
            },
        )
    else:
        raise HTTPException(404, f"App {app_name} not found.")


async def log_generator(request, app_name, db, host_id=None):
    host = resolve_host(db, host_id)
    while True:
        async with aiodocker.Docker(url=docker_base_url(host)) as docker:
            container: DockerContainer = await docker.containers.get(app_name)
            if container._container["State"]["Status"] == "running":
                logs_generator = container.log(
                    stdout=True, stderr=True, follow=True, tail=200
                )
                async for line in logs_generator:
                    yield {"event": "update", "retry": 3000, "data": line}

            if await request.is_disconnected():
                break


async def stat_generator(request, app_name, db, host_id=None):
    prev_stats = None
    host = resolve_host(db, host_id)
    while True:
        async with aiodocker.Docker(url=docker_base_url(host)) as adocker:
            container: DockerContainer = await adocker.containers.get(app_name)
            if container._container["State"]["Status"] == "running":
                stats_generator = container.stats(stream=True)
                prev_stats = None

                async for line in stats_generator:
                    current_stats = await process_app_stats(line, app_name)
                    if prev_stats != current_stats:
                        yield {
                            "event": "update",
                            "retry": 3000,
                            "data": json.dumps(current_stats),
                        }
                        prev_stats = current_stats

            if await request.is_disconnected():
                break

            # Stats are generated every second by docker
            # so there's no point in checking more often than that
            await asyncio.sleep(1)

async def all_stat_generator(request, db, host_id=None):
    host = resolve_host(db, host_id)
    async with aiodocker.Docker(url=docker_base_url(host)) as docker:
        containers = []
        _containers = await docker.containers.list()
        for _app in _containers:
            if _app._container["State"] == "running":
                containers.append(_app)
        loops = [
            stat_generator(request, app._container["Names"][0][1:], db, host_id)
            for app in containers
        ]
        async with aiostream.stream.merge(*loops).stream() as merged:
            async for event in merged:
                yield event


async def process_app_stats(line, app_name):
    cpu_total = 0.0
    cpu_system = 0.0
    cpu_percent = 0.0
    if line["memory_stats"]:
        mem_current = line["memory_stats"]["usage"]
        mem_total = line["memory_stats"]["limit"]
        mem_percent = (mem_current / mem_total) * 100.0
    else:
        mem_current = None
        mem_total = None
        mem_percent = None

    try:
        cpu_percent, cpu_system, cpu_total = await calculate_cpu_percent2(
            line, cpu_total, cpu_system
        )
    except KeyError:
        print("error while getting new CPU stats: %r, falling back")
        cpu_percent = await calculate_cpu_percent(line)

    full_stats = {
        "time": line["read"],
        "name": app_name,
        "mem_total": mem_total,
        "cpu_percent": round(cpu_percent, 1),
        "mem_current": mem_current,
        "mem_percent": round(mem_percent, 1),
    }
    return full_stats
