from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


ComplaintStatus = Literal["open", "in_review", "resolved", "appealed"]


class ComplaintBase(BaseModel):
    user_id: Optional[UUID] = None
    category: Optional[str] = Field(default=None, max_length=100)
    details: str
    status: ComplaintStatus = "open"
    resolution_notes: Optional[str] = None
    resolution_at: Optional[datetime] = None


class ComplaintCreate(ComplaintBase):
    submitted_at: datetime


class ComplaintUpdate(BaseModel):
    category: Optional[str] = Field(default=None, max_length=100)
    details: Optional[str] = None
    status: Optional[ComplaintStatus] = None
    resolution_notes: Optional[str] = None
    resolution_at: Optional[datetime] = None


class ComplaintRead(ComplaintBase):
    id: UUID
    submitted_at: datetime
    gnpec_appeal_info: str = ""

    model_config = ConfigDict(from_attributes=True)
