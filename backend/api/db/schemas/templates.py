from __future__ import annotations
from typing import List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TemplateItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: int
    title: str
    name: str
    platform: str
    description: Optional[str]
    logo: Optional[str]
    image: str
    command: Optional[List[str]]
    notes: Optional[str]
    categories: Optional[List]
    restart_policy: Optional[str]
    ports: Optional[List] = []
    volumes: Optional[List] = []
    env: Optional[List] = []
    devices: Optional[List] = []
    labels: Optional[List] = []
    sysctls: Optional[List] = []
    cap_add: Optional[List] = []
    network_mode: Optional[str]
    network: Optional[str]
    cpus: Optional[int]
    mem_limit: Optional[str]


### TEMPLATE ####


class TemplateBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    url: str

class TemplateRead(TemplateBase):
    id: int
    updated_at: datetime
    created_at: datetime


class TemplateReadAll(TemplateBase):
    items: List[TemplateItem] = []


class TemplateItems(TemplateRead):
    items: List[TemplateItem] = []


### TEMPLATES END ###


### TEMPLATE VARIABLES ###


class TemplateVariables(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    variable: str
    replacement: str


class ReadTemplateVariables(TemplateVariables):
    id: int


### Export/Import ###


class Import_Export(BaseModel):
    templates: List[TemplateItems] = []
    variables: List[ReadTemplateVariables] = []


TemplateItems.model_rebuild()
