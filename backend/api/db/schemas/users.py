from pydantic import BaseModel
from uuid import UUID
from typing import Union, Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    is_active: bool = True
    is_superuser: bool = False
    perm_start: bool = False
    perm_stop: bool = False
    perm_restart: bool = False
    perm_delete: bool = False


class UserUpdate(UserBase):
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    perm_start: Optional[bool] = None
    perm_stop: Optional[bool] = None
    perm_restart: Optional[bool] = None
    perm_delete: Optional[bool] = None


class User(UserBase):
    id: Union[int, str, UUID]
    is_active: bool
    is_superuser: bool
    is_2fa_enabled: bool
    perm_start: bool
    perm_stop: bool
    perm_restart: bool
    perm_delete: bool
    authDisabled: Optional[bool]

    class Config:
        orm_mode = True


class APIKEY(BaseModel):
    id: int
    key_name: str
    is_active: bool
    user: int
    created_at: datetime

    class Config:
        orm_mode = True


class GenerateAPIKEY(BaseModel):
    key_name: str


class DisplayAPIKEY(APIKEY):
    token: str
