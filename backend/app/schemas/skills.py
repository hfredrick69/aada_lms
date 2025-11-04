from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


SkillStatus = Literal["pending", "in_review", "approved", "rejected"]


class SkillCheckoffBase(BaseModel):
    user_id: UUID
    module_id: UUID
    skill_code: str = Field(..., max_length=100)
    status: SkillStatus = "pending"
    evaluator_name: Optional[str] = Field(default=None, max_length=255)
    evaluator_license: Optional[str] = Field(default=None, max_length=255)
    evidence_url: Optional[str] = None
    signed_at: Optional[datetime] = None


class SkillCheckoffCreate(SkillCheckoffBase):
    pass


class SkillCheckoffUpdate(BaseModel):
    status: Optional[SkillStatus] = None
    evaluator_name: Optional[str] = Field(default=None, max_length=255)
    evaluator_license: Optional[str] = Field(default=None, max_length=255)
    evidence_url: Optional[str] = None
    signed_at: Optional[datetime] = None


class SkillCheckoffRead(SkillCheckoffBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
