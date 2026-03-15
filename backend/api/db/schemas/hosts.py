from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HostCreate(BaseModel):
    name: str
    connection_type: str = "docker_api"
    docker_host: Optional[str]
    is_default: bool = False


class HostRead(BaseModel):
    id: int
    name: str
    connection_type: str
    docker_host: Optional[str]
    is_active: bool
    is_default: bool
    last_seen: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
