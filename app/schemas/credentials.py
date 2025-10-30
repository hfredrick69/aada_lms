from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CredentialBase(BaseModel):
    user_id: UUID
    program_id: UUID
    credential_type: str = Field(..., max_length=50)
    cert_serial: str = Field(..., max_length=100)
    issued_at: Optional[datetime] = None


class CredentialCreate(CredentialBase):
    pass


class CredentialUpdate(BaseModel):
    credential_type: Optional[str] = Field(default=None, max_length=50)
    issued_at: Optional[datetime] = None
    cert_serial: Optional[str] = Field(default=None, max_length=100)


class CredentialRead(CredentialBase):
    id: UUID
    issued_at: datetime

    model_config = ConfigDict(from_attributes=True)
