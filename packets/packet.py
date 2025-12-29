from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class UserStatus(str, Enum):
    active = "active"
    deactivated = "deactivated"

class UserCreate(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    status: Optional[UserStatus]

class DatabaseSchema(BaseModel):
    id: int
    username: str
    password: str
    api_key: str
    status: Literal['active', 'deactivated']
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PostgresConfig(BaseModel):
    host: str
    port: int
    password: str
    user: str
    dbname: str

