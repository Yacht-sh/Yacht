from pydantic import BaseModel
from typing import Any, Optional


class Compose(BaseModel):
    name: str


class ComposeWrite(Compose):
    content: Optional[Any]


class ComposeRead(ComposeWrite):
    path: str
