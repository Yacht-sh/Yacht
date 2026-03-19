import docker
from fastapi import HTTPException

from api.db.crud.agents import get_agent_for_host
from api.utils.docker_hosts import get_docker_client, host_metadata, resolve_host


def _annotate_with_host(attrs, host):
    attrs.update({"YachtHost": host_metadata(host)})
    return attrs


def _docker_http_exception(exc):
    status_code = getattr(getattr(exc, "response", None), "status_code", 500)
    detail = getattr(exc, "explanation", str(exc))
    return HTTPException(status_code=status_code, detail=detail)


def _cached_agent_resource_items(db, host_id, attribute):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type != "agent":
        return None, host
    agent = get_agent_for_host(db, host.id)
    items = getattr(agent, attribute) or []
    return [_annotate_with_host(dict(item), host) for item in items], host


### IMAGES ###


def get_images(db, host_id=None):
    images, _host = _cached_agent_resource_items(db, host_id, "images")
    if images is not None:
        return images
    host, dclient = get_docker_client(db, host_id)
    containers = dclient.containers.list(all=True)
    images = dclient.images.list()
    image_list = []
    for image in images:
        attrs = image.attrs
        for container in containers:
            try:
                if container.image.id in image.id:
                    attrs.update({"inUse": True})
            except docker.errors.NotFound:
                continue
            except docker.errors.APIError as exc:
                raise _docker_http_exception(exc) from exc
        if attrs.get("inUse") is None:
            attrs.update({"inUse": False})

        image_list.append(_annotate_with_host(attrs, host))
    return image_list


def write_image(db, image_tag, host_id=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Image pulls are not implemented for agent hosts."
        )
    delim = ":"
    _, dclient = get_docker_client(db, host_id)
    repo, tag = None, image_tag
    if delim in image_tag:
        repo, tag = tag.split(delim, 1)
    else:
        repo = image_tag
        tag = "latest"
    dclient.images.pull(repo, tag)
    return get_images(db, host_id)


def get_image(db, image_id, host_id=None):
    images, _host = _cached_agent_resource_items(db, host_id, "images")
    if images is not None:
        for image in images:
            if image.get("Id") == image_id or image.get("id") == image_id:
                return image
        raise HTTPException(status_code=404, detail="Image not found.")
    host, dclient = get_docker_client(db, host_id)
    containers = dclient.containers.list(all=True)
    image = dclient.images.get(image_id)
    attrs = image.attrs
    for container in containers:
        try:
            if container.image.id in image.id:
                attrs.update({"inUse": True})
        except docker.errors.NotFound:
            continue
        except docker.errors.APIError as exc:
            raise _docker_http_exception(exc) from exc
    if attrs.get("inUse") is None:
        attrs.update({"inUse": False})
    return _annotate_with_host(attrs, host)


def update_image(db, image_id, host_id=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Image updates are not implemented for agent hosts."
        )
    _, dclient = get_docker_client(db, host_id)
    if type(image_id) == str:
        image = dclient.images.get(image_id)
        new_image = dclient.images.get_registry_data(image.tags[0])
        try:
            new_image.pull()
        except docker.errors.APIError as exc:
            raise _docker_http_exception(exc) from exc
        return get_image(db, image_id, host_id)


def delete_image(db, image_id, host_id=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Image deletes are not implemented for agent hosts."
        )
    _, dclient = get_docker_client(db, host_id)
    image = dclient.images.get(image_id)
    try:
        dclient.images.remove(image_id, force=True)
    except docker.errors.APIError as exc:
        raise _docker_http_exception(exc) from exc
    return image.attrs


### Volumes ###
def get_volumes(db, host_id=None):
    volumes, _host = _cached_agent_resource_items(db, host_id, "volumes")
    if volumes is not None:
        return volumes
    host, dclient = get_docker_client(db, host_id)
    containers = dclient.containers.list(all=True)
    volumes = dclient.volumes.list()
    volume_list = []
    for volume in volumes:
        attrs = volume.attrs
        for container in containers:
            try:
                if any(
                    d["Source"] == volume.attrs["Mountpoint"]
                    for d in container.attrs["Mounts"]
                ):
                    attrs.update({"inUse": True})
            except docker.errors.NotFound:
                continue
            except docker.errors.APIError as exc:
                raise _docker_http_exception(exc) from exc
        if attrs.get("inUse") is None:
            attrs.update({"inUse": False})
        volume_list.append(_annotate_with_host(attrs, host))
    return volume_list


def write_volume(db, volume_name, host_id=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Volume creates are not implemented for agent hosts."
        )
    _, dclient = get_docker_client(db, host_id)
    try:
        dclient.volumes.create(name=volume_name)
    except docker.errors.APIError as exc:
        raise _docker_http_exception(exc) from exc
    return get_volumes(db, host_id)


def get_volume(db, volume_id, host_id=None):
    volumes, _host = _cached_agent_resource_items(db, host_id, "volumes")
    if volumes is not None:
        for volume in volumes:
            if volume.get("Name") == volume_id or volume.get("name") == volume_id:
                return volume
        raise HTTPException(status_code=404, detail="Volume not found.")
    host, dclient = get_docker_client(db, host_id)
    containers = dclient.containers.list(all=True)
    volume = dclient.volumes.get(volume_id)
    attrs = volume.attrs
    for container in containers:
        try:
            if any(
                d["Source"] == volume.attrs["Mountpoint"]
                for d in container.attrs["Mounts"]
            ):
                attrs.update({"inUse": True})
        except docker.errors.NotFound:
            continue
        except docker.errors.APIError as exc:
            raise _docker_http_exception(exc) from exc
    if attrs.get("inUse") is None:
        attrs.update({"inUse": False})
    return _annotate_with_host(attrs, host)


def delete_volume(db, volume_id, host_id=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Volume deletes are not implemented for agent hosts."
        )
    _, dclient = get_docker_client(db, host_id)
    volume = dclient.volumes.get(volume_id)
    try:
        volume.remove(force=True)
    except docker.errors.APIError as exc:
        raise _docker_http_exception(exc) from exc
    return volume.attrs


### Networks ###
def get_networks(db, host_id=None):
    networks, _host = _cached_agent_resource_items(db, host_id, "networks")
    if networks is not None:
        return networks
    host, dclient = get_docker_client(db, host_id)
    containers = dclient.containers.list(all=True)
    networks = dclient.networks.list()
    network_list = []
    for network in networks:
        attrs = network.attrs
        for container in containers:
            try:
                if any(
                    d["NetworkID"] == network.attrs["Id"]
                    for d in container.attrs["NetworkSettings"]["Networks"].values()
                ):
                    attrs.update({"inUse": True})
                    break
            except docker.errors.NotFound:
                continue
            except docker.errors.APIError as exc:
                raise _docker_http_exception(exc) from exc
        if attrs:
            if attrs.get("inUse") is None:
                attrs.update({"inUse": False})
            if attrs.get("Labels", {}) and attrs.get("Labels", {}).get(
                "com.docker.compose.project"
            ):
                attrs.update({"Project": attrs["Labels"]["com.docker.compose.project"]})
            network_list.append(_annotate_with_host(attrs, host))
    return network_list


def write_network(db, network_form, host_id=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Network creates are not implemented for agent hosts."
        )
    _, dclient = get_docker_client(db, host_id)

    if network_form.ipv4subnet:
        ipv4_pool = docker.types.IPAMPool(
            subnet=network_form.ipv4subnet,
            gateway=network_form.ipv4gateway,
            iprange=network_form.ipv4range,
        )
    if network_form.ipv6_enabled and network_form.ipv6subnet:
        ipv6_pool = docker.types.IPAMPool(
            subnet=network_form.ipv6subnet,
            gateway=network_form.ipv6gateway,
            iprange=network_form.ipv6range,
        )
    if "ipv6_pool" in locals() and "ipv4_pool" in locals():
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipv4_pool, ipv6_pool])
    elif "ipv4_pool" in locals():
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipv4_pool])
    else:
        ipam_config = None

    if network_form.network_devices:
        network_options = {"parent": network_form.network_devices}
    else:
        network_options = None
    try:
        dclient.networks.create(
            network_form.name,
            driver=network_form.networkDriver,
            ipam=ipam_config,
            options=network_options,
            internal=network_form.internal,
            enable_ipv6=network_form.ipv6_enabled,
            attachable=network_form.attachable,
        )
    except docker.errors.APIError as exc:
        raise _docker_http_exception(exc) from exc

    return get_networks(db, host_id)


def get_network(db, network_id, host_id=None):
    networks, _host = _cached_agent_resource_items(db, host_id, "networks")
    if networks is not None:
        for network in networks:
            if network.get("Id") == network_id or network.get("Name") == network_id:
                return network
        raise HTTPException(status_code=404, detail="Network not found.")
    host, dclient = get_docker_client(db, host_id)
    containers = dclient.containers.list(all=True)

    try:
        network = dclient.networks.get(network_id)
    except docker.errors.APIError as exc:
        raise _docker_http_exception(exc) from exc

    attrs = network.attrs
    for container in containers:
        try:
            if any(
                d["NetworkID"] == network.attrs["Id"]
                for d in container.attrs["NetworkSettings"]["Networks"].values()
            ):
                attrs.update({"inUse": True})
                break
        except docker.errors.NotFound:
            continue
        except docker.errors.APIError as exc:
            raise _docker_http_exception(exc) from exc
    if attrs.get("inUse") is None:
        attrs.update({"inUse": False})
    return _annotate_with_host(attrs, host)


def delete_network(db, network_id, host_id=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Network deletes are not implemented for agent hosts."
        )
    _, dclient = get_docker_client(db, host_id)
    network = dclient.networks.get(network_id)
    try:
        network.remove()
    except docker.errors.APIError as exc:
        raise _docker_http_exception(exc) from exc

    return network.attrs


def prune_resources(db, resource, host_id=None):
    host = resolve_host(db, host_id, update_last_seen=False)
    if host.connection_type == "agent":
        raise HTTPException(
            status_code=501, detail="Prune is not implemented for agent hosts."
        )
    _, dclient = get_docker_client(db, host_id)
    action = getattr(dclient, resource)
    if resource == "images":
        deleted_resource = action.prune(filters={"dangling": False})
    else:
        deleted_resource = action.prune()
    return deleted_resource
