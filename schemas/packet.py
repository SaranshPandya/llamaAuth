from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from enum import Enum
from dataclasses import dataclass

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
    api_key: Optional[str] = None
    status: Literal['active', 'deactivated']
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PostgresConfig(BaseModel):
    host: str
    port: int
    password: str
    user: str
    dbname: str
    sslmode: Optional[str] = None
    
    
@dataclass(frozen=True)
class Migration:
    filename: str
    body: str
    checksum: str


class RegisterUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    age: int


class AuthenticateUserInput(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

class Chat(BaseModel):
    query: str
    api_key: str
    model: str
    stream: bool = False
    base_url: Optional[str] = None 
