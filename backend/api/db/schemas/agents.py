from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AgentRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    hostname: Optional[str] = Field(None, max_length=255)
    version: Optional[str] = Field(None, max_length=64)
    docker_version: Optional[str] = Field(None, max_length=64)
    capabilities: dict[str, bool] = Field(default_factory=dict)


class AgentHeartbeat(BaseModel):
    version: Optional[str] = Field(None, max_length=64)
    docker_version: Optional[str] = Field(None, max_length=64)
    capabilities: Optional[dict[str, bool]] = None
    containers_running: Optional[int] = None
    containers_total: Optional[int] = None


class AgentRegisterResponse(BaseModel):
    host_id: int
    agent_id: str
    agent_token: str
    heartbeat_interval: int


class AgentHeartbeatResponse(BaseModel):
    host_id: int
    heartbeat_interval: int
    server_time: datetime


class AgentRead(BaseModel):
    id: int
    host_id: int
    host_name: str
    hostname: Optional[str]
    version: Optional[str]
    docker_version: Optional[str]
    capabilities: dict[str, bool]
    last_heartbeat: Optional[datetime]
    created_at: datetime
    updated_at: datetime

