from pydantic import BaseModel
from uuid import UUID
from typing import Union, Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: Union[int, str, UUID]
    is_active: bool
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
