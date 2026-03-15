from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from api.actions import resources
from api.db.schemas.resources import ImageWrite, VolumeWrite, NetworkWrite
from api.auth.auth import auth_check
from api.utils.auth import get_db

router = APIRouter()
### Images ###


@router.get(
    "/images/",
)
def get_images(
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.get_images(db, host_id)


@router.post(
    "/images/",
)
def write_image(
    image: ImageWrite,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.write_image(db, image.image, host_id)


@router.get(
    "/images/{image_id}",
)
def get_image(
    image_id,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.get_image(db, image_id, host_id)


@router.get(
    "/images/{image_id}/pull",
)
def pull_image(
    image_id,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.update_image(db, image_id, host_id)


@router.delete(
    "/images/{image_id}",
)
def delete_image(
    image_id,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.delete_image(db, image_id, host_id)


### Volumes ###
@router.get(
    "/volumes/",
)
def get_volumes(
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.get_volumes(db, host_id)


@router.post(
    "/volumes/",
)
def write_volume(
    name: VolumeWrite,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.write_volume(db, name.name, host_id)


@router.get(
    "/volumes/{volume_name}",
)
def get_volume(
    volume_name,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.get_volume(db, volume_name, host_id)


@router.delete(
    "/volumes/{volume_name}",
)
def delete_volume(
    volume_name,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.delete_volume(db, volume_name, host_id)


### Networks ###
@router.get(
    "/networks/",
)
def get_networks(
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.get_networks(db, host_id)


@router.post(
    "/networks/",
)
def write_network(
    form: NetworkWrite,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.write_network(db, form, host_id)


@router.get(
    "/networks/{network_name}",
)
def get_network(
    network_name,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.get_network(db, network_name, host_id)


@router.delete(
    "/networks/{network_name}",
)
def delete_network(
    network_name,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    auth_check(Authorize)
    return resources.delete_network(db, network_name, host_id)
