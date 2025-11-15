from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthUser(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    roles: List[str] = []

    class Config:
        from_attributes = True


class RegistrationRequestPayload(BaseModel):
    email: EmailStr


class RegistrationVerifyPayload(BaseModel):
    token: str


class RegistrationVerifyResponse(BaseModel):
    registration_token: str
    expires_at: datetime


class RegistrationCompletePayload(BaseModel):
    registration_token: str
    first_name: str
    last_name: str
    password: str
