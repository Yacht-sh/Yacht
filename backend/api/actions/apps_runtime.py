import asyncio
import io
import json
import re
import time
import zipfile

import aiodocker
import aiostream
import docker
import yaml
from aiodocker.containers import DockerContainer
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from api.db.crud.agents import queue_agent_job, wait_for_agent_job
from api.utils.apps import _check_updates, calculate_cpu_percent, calculate_cpu_percent2
from api.utils.docker_hosts import docker_base_url, get_docker_client, resolve_host


def merge_dicts(dict1, dict2):
    if dict1 and dict2:
        dict2.update(dict1)
        return dict2
    if dict1:
        return dict1
    if dict2:
        return dict2
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
        raise HTTPException(
            500, f"Unable to read container metadata: {exc.strerror}"
        ) from exc

    raise HTTPException(500, "Unable to determine Yacht container ID")


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
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Deploy is not implemented for agent hosts."
        )
    _, dclient = get_docker_client(db, host_id)
    if edit is True:
        try:
            running_app = dclient.containers.get(_id)
            try:
                running_app.remove(force=True)
            except docker.errors.DockerException:
                raise
        except docker.errors.NotFound:
            running_app = None

    combined_labels = merge_dicts(portlabels, labels)
    try:
        launch = dclient.containers.run(
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
    except docker.errors.APIError as exc:
        if exc.status_code == 500:
            failed_app = dclient.containers.get(name)
            failed_app.remove()
        raise HTTPException(status_code=exc.status_code, detail=exc.explanation)

    print(
        f"""Container started successfully.
       Name: {name},
      Image: {image},
      Ports: {ports},
    Volumes: {volumes},
        Env: {env}"""
    )
    return launch


def app_action(app_name, action, db, host_id=None, apps_getter=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        allowed_actions = {"start", "stop", "restart", "remove", "kill"}
        if action not in allowed_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported container action for agent hosts: {action}",
            )
        job = queue_agent_job(
            db,
            host.id,
            "container_action",
            {"container": app_name, "action": action},
        )
        completed_job = wait_for_agent_job(db, job.id)
        if completed_job.status == "failed":
            raise HTTPException(
                status_code=502,
                detail=completed_job.error or "Agent job failed.",
            )
        db.expire_all()
        return apps_getter(db=db, host_id=host_id) if apps_getter else None

    _, dclient = get_docker_client(db, host_id)
    app = dclient.containers.get(app_name)
    app_method = getattr(app, action)

    try:
        if action == "remove":
            app_method(force=True)
        else:
            app_method()
    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )

    return apps_getter(db=db, host_id=host_id) if apps_getter else None


def app_update(app_name, db, host_id=None, apps_getter=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501,
            detail="Container updates are not implemented for agent hosts.",
        )
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
        raise HTTPException(status_code=exc.response.status_code, detail=exc.explanation)

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
        raise HTTPException(status_code=exc.response.status_code, detail=exc.explanation)

    print("**** Updating " + old.name + "****")
    result = updater.wait(timeout=120)
    print(result)
    time.sleep(1)
    return apps_getter(db=db, host_id=host_id) if apps_getter else None


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
        status_code = 500
        detail = exc.args[0]
        raise HTTPException(status_code=status_code, detail=detail)
    background_tasks.add_task(update_self_in_background, yacht)
    return {"result": "successful"}


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
        if hasattr(exc, "response"):
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.explanation
            )
        raise HTTPException(status_code=400, detail=exc.args)

    return _check_updates(yacht.image.tags[0])


def generate_support_bundle(app_name, db, host_id=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501,
            detail="Support bundles are not implemented for agent hosts.",
        )
    _, dclient = get_docker_client(db, host_id)
    if dclient.containers.get(app_name):
        app = dclient.containers.get(app_name)
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as zf:
            attrs = app.attrs
            service_log = app.logs()
            zf.writestr(f"{app_name}.log", service_log)
            zf.writestr(f"{app_name}-config.yml", yaml.dump(attrs))
        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type="application/x-zip-compressed",
            headers={
                "Content-Disposition": f"attachment;filename={app_name}_bundle.zip"
            },
        )

    raise HTTPException(404, f"App {app_name} not found.")


async def log_generator(request, app_name, db, host_id=None):
    host = resolve_host(db, host_id)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Logs are not implemented for agent hosts."
        )
    while True:
        async with aiodocker.Docker(url=docker_base_url(host)) as docker_client:
            container: DockerContainer = await docker_client.containers.get(app_name)
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
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Stats are not implemented for agent hosts."
        )
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

            await asyncio.sleep(1)


async def all_stat_generator(request, db, host_id=None):
    host = resolve_host(db, host_id)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Stats are not implemented for agent hosts."
        )
    async with aiodocker.Docker(url=docker_base_url(host)) as docker_client:
        containers = []
        listed_containers = await docker_client.containers.list()
        for app in listed_containers:
            if app._container["State"] == "running":
                containers.append(app)
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

    return {
        "time": line["read"],
        "name": app_name,
        "mem_total": mem_total,
        "cpu_percent": round(cpu_percent, 1),
        "mem_current": mem_current,
        "mem_percent": round(mem_percent, 1),
    }
