import docker
from fastapi import HTTPException

### IMAGES ###


def get_images():
    dclient = docker.from_env()
    containers = dclient.containers.list(all=True)
    images = dclient.images.list()
    image_list = []
    for image in images:
        attrs = image.attrs
        for container in containers:
            try:
                if container.image.id in image.id:
                    attrs.update({"inUse": True})
            except Exception as exc:
                if exc.status_code == 404:
                    pass
        if attrs.get("inUse") == None:
            attrs.update({"inUse": False})

        image_list.append(attrs)
    return image_list


def write_image(image_tag):
    delim = ":"
    dclient = docker.from_env()
    repo, tag = None, image_tag
    if delim in image_tag:
        repo, tag = tag.split(delim, 1)
    else:
        repo = image_tag
        tag = "latest"
    image = dclient.images.pull(repo, tag)
    return get_images()


def get_image(image_id):
    dclient = docker.from_env()
    containers = dclient.containers.list(all=True)
    image = dclient.images.get(image_id)
    attrs = image.attrs
    for container in containers:
        try:
            if container.image.id in image.id:
                attrs.update({"inUse": True})
        except Exception as exc:
            if exc.status_code == 404:
                pass
    if attrs.get("inUse") == None:
        attrs.update({"inUse": False})
    return attrs


def update_image(image_id):
    dclient = docker.from_env()
    if type(image_id) == str:
        image = dclient.images.get(image_id)
        new_image = dclient.images.get_registry_data(image.tags[0])
        try:
            new_image.pull()
        except Exception as exc:
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.explanation
            )
        return get_image(image_id)


def delete_image(image_id):
    dclient = docker.from_env()
    image = dclient.images.get(image_id)
    try:
        dclient.images.remove(image_id, force=True)
    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )
    return image.attrs


### Volumes ###
def get_volumes():
    dclient = docker.from_env()
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
            except Exception as exc:
                if exc.status_code == 404:
                    pass
        if attrs.get("inUse") == None:
            attrs.update({"inUse": False})
        volume_list.append(attrs)
    return volume_list


def write_volume(volume_name):
    dclient = docker.from_env()
    try:
        volume = dclient.volumes.create(name=volume_name)
    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )
    return get_volumes()


def get_volume(volume_id):
    dclient = docker.from_env()
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
        except Exception as exc:
            if exc.status_code == 404:
                pass
            else:
                raise HTTPException(
                    status_code=exc.response.status_code, detail=exc.explanation
                )
    if attrs.get("inUse") == None:
        attrs.update({"inUse": False})
    return attrs


def delete_volume(volume_id):
    dclient = docker.from_env()
    volume = dclient.volumes.get(volume_id)
    try:
        volume.remove(force=True)
    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )
    return volume.attrs


### Networks ###
def get_networks():
    dclient = docker.from_env()
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
            except Exception as exc:
                print(exc)
                if exc.status_code == 404:
                    pass
                else:
                    raise HTTPException(
                        status_code=exc.response.status_code, detail=exc.explanation
                    )
        if attrs:
            if attrs.get("inUse") is None:
                attrs.update({"inUse": False})
            if attrs.get("Labels", {}):
                if attrs.get("Labels", {}).get("com.docker.compose.project"):
                    attrs.update(
                        {"Project": attrs["Labels"]["com.docker.compose.project"]}
                    )
            network_list.append(attrs)
    return network_list


def write_network(network_form):
    dclient = docker.from_env()

    ### Check for IP addresses ###
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

    ### Check for parent device (macvlan only) ###
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
    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )

    return get_networks()


def get_network(network_id):
    dclient = docker.from_env()
    containers = dclient.containers.list(all=True)

    try:
        network = dclient.networks.get(network_id)

    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )

    attrs = network.attrs
    for container in containers:
        try:
            if any(
                d["NetworkID"] == network.attrs["Id"]
                for d in container.attrs["NetworkSettings"]["Networks"].values()
            ):
                attrs.update({"inUse": True})
                break
        except Exception as exc:
            if exc.status_code == 404:
                pass
            else:
                raise HTTPException(
                    status_code=exc.response.status_code, detail=exc.explanation
                )
    if attrs.get("inUse") == None:
        attrs.update({"inUse": False})
    return attrs


def delete_network(network_id):
    dclient = docker.from_env()
    network = dclient.networks.get(network_id)
    try:
        network.remove()

    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )

    return network.attrs


def prune_resources(resource):
    dclient = docker.from_env()
    action = getattr(dclient, resource)
    if resource == "images":
        deleted_resource = action.prune(filters={"dangling": False})
    else:
        deleted_resource = action.prune()
    return deleted_resource
