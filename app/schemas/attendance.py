from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AttendanceBase(BaseModel):
    user_id: UUID
    module_id: UUID
    session_type: Literal["live", "lab", "externship"]
    session_ref: Optional[str] = Field(default=None, max_length=255)
    started_at: datetime
    ended_at: datetime

    @model_validator(mode="after")
    def validate_duration(self) -> "AttendanceBase":
        if self.ended_at <= self.started_at:
            raise ValueError("ended_at must be after started_at")
        return self


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    session_type: Optional[Literal["live", "lab", "externship"]] = None
    session_ref: Optional[str] = Field(default=None, max_length=255)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_update_duration(self) -> "AttendanceUpdate":
        if self.started_at and self.ended_at and self.ended_at <= self.started_at:
            raise ValueError("ended_at must be after started_at")
        return self


class AttendanceRead(AttendanceBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
