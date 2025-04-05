from pydantic import BaseModel
from typing import Optional


class ImageWrite(BaseModel):
    image: str


class VolumeWrite(BaseModel):
    name: str


class NetworkWrite(BaseModel):
    attachable: bool
    internal: bool
    ipv4gateway: str
    ipv4range: Optional[str]
    ipv4subnet: str
    ipv6_enabled: bool
    ipv6gateway: Optional[str]
    ipv6range: Optional[str]
    ipv6subnet: Optional[str]
    name: str
    networkDriver: str
    network_devices: str
