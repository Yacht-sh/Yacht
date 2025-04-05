import api.db.models.containers as models
from api.db.database import SessionLocal
from api.settings import Settings

import aiodocker
import docker
from docker.errors import APIError
import json
from fastapi import HTTPException

settings = Settings()

# For Deploy Form

# Input Format:
# [
#     {
#         'cport': '53',
#         'hport': '53',
#         'proto': 'tcp',
#     },
#     ...
# ]
# Result Format:
# {
#     '53/tcp': ('0.0.0.0', 53),
# }


def conv_ports2data(data, network, network_mode):
    ports = {}
    for d in data:
        cport = d.cport
        hport = d.hport
        proto = d.proto
        if not hport:
            hport = None
        ports.update({str(cport) + "/" + proto: hport for d in data})
    return ports


def conv_portlabels2data(data):
    labels = {}
    for d in data:
        if d.label and d.hport:
            labels.update({"local.yacht.port." + d.hport: d.label})
        elif d.label:
            print("in order to have a label the hostport must be set")
            return None
    return labels


# Input Format:
# [
#     {
#         'container': '/mnt/vol2',
#         'bind': '/home/user1'
#     }
#     ...
# ]
# Result Format:
# {
#     '/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},
#     '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}
# }


def conv_volumes2data(data):
    db = SessionLocal()
    t_variables = db.query(models.TemplateVariables).all()

    for volume in data:
        if volume.bind:
            for t_var in t_variables:
                if t_var.variable in volume.bind:
                    new_path = volume.bind.replace(t_var.variable, t_var.replacement)
                    volume.bind = new_path
    volume_data = dict((d.bind, {"bind": d.container, "mode": "rw"}) for d in data)

    return volume_data


# Input Format:
# [
#     {
#         'name': 'SOMEVARIABLE',
#         'default': '1000'
#     }
#     ...
# ]
# Result Format:
# [
#     "SOMEVARIABLE=xxx", "OTHERVARIABLE=yyy"
# ]
def conv_env2data(data):
    # Set is depracated. Name is the actual value. Label is the name of the field.
    # Label is the label of the label field.
    db = SessionLocal()
    t_variables = db.query(models.TemplateVariables).all()

    for i, variable in enumerate(data):
        for t_var in t_variables:
            if variable.default:
                if t_var.variable in variable.default:
                    new_var = data[i].default.replace(t_var.variable, t_var.replacement)
                    variable.default = new_var
                    break
        else:
            if variable.default.startswith("!"):
                raise HTTPException(
                    400, "Unset template variable used: " + variable.default
                )
    delim = "="
    return [delim.join((d.name, d.default)) for d in data if d.default]


def conv_sysctls2data(data):
    if data:
        return dict((d.name, d.value) for d in data)
    else:
        sysctls = None
        return sysctls


def conv_devices2data(data):
    if data:
        devicelist = []
        for d in data:
            devicelist.append(d.host + ":" + d.container + ":rwm")
        return devicelist
    else:
        devices = None
        return devices


# def conv_labels2data(data):
#     # Set is depracated. Name is the actual value. Label is the name of the field.
#     # Label is the label of the label field.
#     if not data:
#         labels = {}
#         return labels
#     db = SessionLocal()
#     t_variables = db.query(models.TemplateVariables).all()

#     for i, variable in enumerate(data):
#         for t_var in t_variables:
#             if variable.label:
#                 if t_var.variable in variable.label:
#                     new_var = data[i].label.replace(t_var.variable, t_var.replacement)
#                     variable.label = new_var
#                     continue
#             if variable.value:
#                 if t_var.variable in variable.value:
#                     new_var = data[i].value.replace(t_var.variable, t_var.replacement)
#                     variable.value = new_var
#                     continue
#         else:
#             if variable.value.startswith("!"):
#                 raise HTTPException(
#                     400, "Unset template variable used: " + variable.value
#                 )
#             if variable.label.startswith("!"):
#                 raise HTTPException(
#                     400, "Unset template variable used: " + variable.label
#                 )
#     delim = "="
#     return {delim.join((d.label, d.value)) for d in data if d.value}


def conv_labels2data(data):
    # grab template variables
    db = SessionLocal()
    t_variables = db.query(models.TemplateVariables).all()

    # if we have nothing return an empty dictionary
    if not data:
        return {}

    # iterate over template variables and labels and replace templated fields
    for label in data:
        for t_var in t_variables:
            if t_var.variable in label.label:
                label.label = label.label.replace(t_var.variable, t_var.replacement)
            if t_var.variable in label.value:
                label.value = label.value.replace(t_var.variable, t_var.replacement)

    # generate dictionary from de-templated local data
    return dict((d.label, d.value) for d in data)


def conv_caps2data(data):
    if data:
        return data
    else:
        caps = None
        return caps


def conv_image2data(data):
    if data:
        if ":" in data:
            return data
        else:
            image = data + ":latest"
            return image
    else:
        image = None
        return image


def conv_restart2data(data):
    if data and data != "none":
        return {"name": data}
    else:
        restart = None
        return restart


async def calculate_cpu_percent(d):
    try:
        cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    except KeyError as exc:
        pass
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - float(
        d["precpu_stats"]["cpu_usage"]["total_usage"]
    )
    system_delta = float(d["cpu_stats"]["system_cpu_usage"]) - float(
        d["precpu_stats"]["system_cpu_usage"]
    )
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return cpu_percent


async def calculate_cpu_percent2(d, previous_cpu, previous_system):
    cpu_percent = 0.0
    cpu_total = float(d["cpu_stats"]["cpu_usage"]["total_usage"])
    cpu_delta = cpu_total - previous_cpu
    cpu_system = float(d["cpu_stats"]["system_cpu_usage"])
    system_delta = cpu_system - previous_system
    # online_cpus = d["cpu_stats"].get(
    #     "online_cpus", len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    # )
    if system_delta > 0.0:
        # cpu_percent = (cpu_delta / system_delta) * online_cpus * 100.0
        cpu_percent = (cpu_delta / system_delta) * 100.0
    return cpu_percent, cpu_system, cpu_total


async def calculate_blkio_bytes(d):
    bytes_stats = graceful_chain_get(d, "blkio_stats", "io_service_bytes_recursive")
    if not bytes_stats:
        return 0, 0
    r = 0
    w = 0
    for s in bytes_stats:
        if s["op"] == "Read":
            r += s["value"]
        elif s["op"] == "Write":
            w += s["value"]
    return r, w


async def calculate_network_bytes(d):
    networks = graceful_chain_get(d, "networks")
    if not networks:
        return 0, 0
    r = 0
    t = 0
    for if_name, data in networks.items():
        r += data["rx_bytes"]
        t += data["tx_bytes"]
    return r, t


def graceful_chain_get(d, *args, default=None):
    t = d
    for a in args:
        try:
            t = t[a]
        except (KeyError, ValueError, TypeError, AttributeError):
            print("can't get %r from %s", a, t)
            return default
    return t


async def get_app_stats(app_name):
    async with aiodocker.Docker() as docker:
        cpu_total = 0.0
        cpu_system = 0.0
        cpu_percent = 0.0

        container: DockerContainer = await docker.containers.get(app_name)
        stats = container.stats(stream=True)
        async for line in stats:
            mem_current = line["memory_stats"]["usage"]
            mem_total = line["memory_stats"]["limit"]

            try:
                cpu_percent, cpu_system, cpu_total = await calculate_cpu_percent2(
                    line, cpu_total, cpu_system
                )
            except KeyError as e:
                print(f"error while getting new CPU stats: {e}, falling back")
                cpu_percent = await calculate_cpu_percent(line)

            full_stats = {
                "name": line["name"],
                "time": line["read"],
                "cpu_percent": cpu_percent,
                "mem_current": mem_current,
                "mem_total": line["memory_stats"]["limit"],
                "mem_percent": (mem_current / mem_total) * 100.0,
            }
            yield json.dumps(full_stats)


def get_update_ports(ports):
    if ports:
        portdir = {}
        for hport in ports:
            for d in ports[hport]:
                portdir.update({str(hport): d.get("HostPort")})
        return portdir
    else:
        return None


def _check_updates(tag):
    if tag:
        dclient = docker.from_env()
        try:
            current = dclient.images.get(tag)
        except APIError as err:
            if err.status_code == 404:
                return False
            else:
                raise HTTPException(
                    status_code=err.response.status_code, detail=err.explanation
                )
        try:
            new = dclient.images.get_registry_data(tag)
        except APIError:
            return False
        if any(
            new.attrs["Descriptor"]["digest"] in i for i in current.attrs["RepoDigests"]
        ):
            return False
        else:
            return True

    else:
        return False


def format_bytes(size):
    power = 2 ** 10
    n = 0
    power_labels = {0: "B", 1: "KB", 2: "MB", 3: "GB"}
    while size > power:
        size /= power
        n += 1
    return str(round(size)) + " " + str(power_labels[n])


def conv_cpus2data(cpus):
    if cpus:
        return cpus * 10 ** 9
    else:
        return None
