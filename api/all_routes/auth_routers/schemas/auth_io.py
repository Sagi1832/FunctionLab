from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    username: str  
    password: str = Field(..., min_length=6)


class LoginIn(BaseModel):
    username: str
    password: str = Field(..., min_length=6)


class RefreshIn(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class AuthTokensOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True
