from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExternshipBase(BaseModel):
    user_id: UUID
    site_name: str = Field(..., max_length=255)
    site_address: Optional[str] = None
    supervisor_name: Optional[str] = Field(default=None, max_length=255)
    supervisor_email: Optional[str] = Field(default=None, max_length=255)
    total_hours: int = Field(default=0, ge=0)
    verification_doc_url: Optional[str] = None
    verified: bool = False
    verified_at: Optional[datetime] = None


class ExternshipCreate(ExternshipBase):
    pass


class ExternshipUpdate(BaseModel):
    site_name: Optional[str] = Field(default=None, max_length=255)
    site_address: Optional[str] = None
    supervisor_name: Optional[str] = Field(default=None, max_length=255)
    supervisor_email: Optional[str] = Field(default=None, max_length=255)
    total_hours: Optional[int] = Field(default=None, ge=0)
    verification_doc_url: Optional[str] = None
    verified: Optional[bool] = None
    verified_at: Optional[datetime] = None


class ExternshipRead(ExternshipBase):
    id: UUID
    student_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
