from typing import List, Optional, Union
from pydantic import BaseModel


class PortsSchema(BaseModel):
    label: Optional[str]
    cport: str
    hport: Optional[str]
    proto: str


class VolumesSchema(BaseModel):
    container: str
    bind: str


class EnvSchema(BaseModel):
    label: str
    default: Optional[str]
    name: Optional[str]
    description: Optional[str]


class SysctlsSchema(BaseModel):
    name: str
    value: str


class DevicesSchema(BaseModel):
    container: str
    host: str


class LabelSchema(BaseModel):
    label: str
    value: str


class DeployForm(BaseModel):
    name: str
    image: str
    restart_policy: str
    notes: Optional[str]
    command: Optional[List[str]]
    ports: Optional[List[PortsSchema]]
    volumes: Optional[List[VolumesSchema]]
    env: Optional[List[EnvSchema]]
    devices: Optional[List[DevicesSchema]]
    labels: Optional[List[LabelSchema]]
    sysctls: Optional[List[SysctlsSchema]]
    cap_add: Optional[List[str]]
    network_mode: Optional[str]
    network: Optional[str]
    cpus: Optional[int]
    mem_limit: Optional[str]
    edit: Optional[bool]
    id: Optional[str]


# LOGS #


class DeployLogs(BaseModel):
    logs: str


class AppLogs(BaseModel):
    logs: str


# Processes #


class Processes(BaseModel):
    Processes: List[List[str]]
    Titles: List[str]
