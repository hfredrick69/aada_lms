from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ModuleResult(BaseModel):
    module_id: UUID
    module_code: str
    module_title: str
    score: Optional[int] = None
    progress_pct: Optional[int] = None
    scorm_status: Optional[str] = None


class TranscriptGenerate(BaseModel):
    user_id: UUID
    program_id: UUID


class TranscriptRead(BaseModel):
    id: UUID
    user_id: UUID
    program_id: UUID
    gpa: Optional[float] = None
    generated_at: datetime
    pdf_url: Optional[str] = None
    modules: List[ModuleResult] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_with_modules(cls, transcript, modules: List[ModuleResult]) -> "TranscriptRead":
        gpa_value: Optional[Decimal] = getattr(transcript, "gpa", None)
        gpa_float = float(gpa_value) if gpa_value is not None else None
        return cls(
            id=transcript.id,
            user_id=transcript.user_id,
            program_id=transcript.program_id,
            gpa=gpa_float,
            generated_at=transcript.generated_at,
            pdf_url=transcript.pdf_url,
            modules=modules,
        )
