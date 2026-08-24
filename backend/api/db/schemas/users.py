from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Union, Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: Union[int, str, UUID]
    is_active: bool
    authDisabled: Optional[bool]


class APIKEY(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key_name: str
    is_active: bool
    user: int
    created_at: datetime


class GenerateAPIKEY(BaseModel):
    key_name: str


class DisplayAPIKEY(APIKEY):
    token: str
