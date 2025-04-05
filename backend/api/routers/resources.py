from __future__ import annotations
from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from api.actions import resources
from api.db.schemas.resources import ImageWrite, VolumeWrite, NetworkWrite
from api.auth.auth import auth_check

router = APIRouter()
### Images ###


@router.get(
    "/images/",
)
def get_images(Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.get_images()


@router.post(
    "/images/",
)
def write_image(image: ImageWrite, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.write_image(image.image)


@router.get(
    "/images/{image_id}",
)
def get_image(image_id, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.get_image(image_id)


@router.get(
    "/images/{image_id}/pull",
)
def pull_image(image_id, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.update_image(image_id)


@router.delete(
    "/images/{image_id}",
)
def delete_image(image_id, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.delete_image(image_id)


### Volumes ###
@router.get(
    "/volumes/",
)
def get_volumes(Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.get_volumes()


@router.post(
    "/volumes/",
)
def write_volume(name: VolumeWrite, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.write_volume(name.name)


@router.get(
    "/volumes/{volume_name}",
)
def get_volume(volume_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.get_volume(volume_name)


@router.delete(
    "/volumes/{volume_name}",
)
def delete_volume(volume_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.delete_volume(volume_name)


### Networks ###
@router.get(
    "/networks/",
)
def get_networks(Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.get_networks()


@router.post(
    "/networks/",
)
def write_network(form: NetworkWrite, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.write_network(form)


@router.get(
    "/networks/{network_name}",
)
def get_network(network_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.get_network(network_name)


@router.delete(
    "/networks/{network_name}",
)
def delete_network(network_name, Authorize: AuthJWT = Depends()):
    auth_check(Authorize)
    return resources.delete_network(network_name)
