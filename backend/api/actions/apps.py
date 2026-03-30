from fastapi import HTTPException

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
)
from api.utils.docker_hosts import get_docker_client, host_metadata, resolve_host
from api.db.crud.agents import get_agent_for_host
from api.actions.apps_runtime import (
    _update_self,
    all_stat_generator,
    app_action as runtime_app_action,
    app_update as runtime_app_update,
    check_self_update,
    generate_support_bundle,
    launch_app,
    log_generator,
    update_self_in_background,
)
from api.utils.templates import conv2dict

import docker


"""
Returns all running apps in a list
"""


def _annotate_with_host(attrs, host):
    attrs.update(conv2dict("YachtHost", host_metadata(host)))
    return attrs


def _cached_agent_apps(db, host_id=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type != "agent":
        return None, host
    agent = get_agent_for_host(db, host.id)
    apps = [_annotate_with_host(dict(app), host) for app in (agent.containers or [])]
    return apps, host


def get_running_apps(db, host_id=None):
    apps, _host = _cached_agent_apps(db, host_id)
    if apps is not None:
        return [app for app in apps if app.get("State", {}).get("Running")]
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
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Update checks are not implemented for agent hosts."
        )
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
    apps, _host = _cached_agent_apps(db, host_id)
    if apps is not None:
        return apps
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
    apps, _host = _cached_agent_apps(db, host_id)
    if apps is not None:
        for app in apps:
            if app.get("name") == app_name:
                return app
        raise HTTPException(status_code=404, detail="Container not found.")
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
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Process inspection is not implemented for agent hosts."
        )
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
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Logs are not implemented for agent hosts."
        )
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


def app_action(app_name, action, db, host_id=None):
    return runtime_app_action(
        app_name, action, db, host_id=host_id, apps_getter=get_apps
    )


def app_update(app_name, db, host_id=None):
    return runtime_app_update(app_name, db, host_id=host_id, apps_getter=get_apps)
