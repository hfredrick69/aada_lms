"""SCORM tracking router - Save and retrieve SCORM 1.2/2004 data"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal

from app.db.session import get_db
from app.db.models.scorm import ScormRecord
from app.db.models.user import User
from app.routers.auth import get_current_user


class ScormDataCreate(BaseModel):
    user_id: UUID
    module_id: UUID
    lesson_status: Optional[str] = "incomplete"  # incomplete/completed/passed/failed
    score_scaled: Optional[Decimal] = None  # 0.0 to 1.0
    score_raw: Optional[Decimal] = None
    session_time: Optional[str] = None
    interactions: Optional[dict] = None


class ScormDataUpdate(BaseModel):
    lesson_status: Optional[str] = None
    score_scaled: Optional[Decimal] = None
    score_raw: Optional[Decimal] = None
    session_time: Optional[str] = None
    interactions: Optional[dict] = None


class ScormDataResponse(BaseModel):
    id: UUID
    user_id: UUID
    module_id: UUID
    lesson_status: Optional[str]
    score_scaled: Optional[Decimal]
    score_raw: Optional[Decimal]
    session_time: Optional[str]
    interactions: Optional[dict]

    class Config:
        from_attributes = True


router = APIRouter(prefix="/scorm", tags=["scorm"])


@router.post("/records", response_model=ScormDataResponse, status_code=201)
def upsert_scorm_record(
    data: ScormDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update SCORM record (students can update their own, admins can update any)"""
    # Students can only update their own records
    if data.user_id != current_user.id and not any(
        role in ["admin", "instructor"] for role in current_user.roles
    ):
        raise HTTPException(status_code=403, detail="Not authorized to update this record")

    # Check if record exists
    existing = db.query(ScormRecord).filter(
        ScormRecord.user_id == data.user_id,
        ScormRecord.module_id == data.module_id
    ).first()

    if existing:
        # Update existing record
        if data.lesson_status is not None:
            existing.lesson_status = data.lesson_status
        if data.score_scaled is not None:
            existing.score_scaled = data.score_scaled
        if data.score_raw is not None:
            existing.score_raw = data.score_raw
        if data.session_time is not None:
            existing.session_time = data.session_time
        if data.interactions is not None:
            existing.interactions = data.interactions

        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new record
        record = ScormRecord(
            user_id=data.user_id,
            module_id=data.module_id,
            lesson_status=data.lesson_status,
            score_scaled=data.score_scaled,
            score_raw=data.score_raw,
            session_time=data.session_time,
            interactions=data.interactions
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


@router.get("/records/{user_id}/{module_id}", response_model=ScormDataResponse)
def get_scorm_record(
    user_id: UUID,
    module_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get SCORM data for a specific user and module (for resume functionality)"""
    # Students can only view their own records
    if user_id != current_user.id and not any(
        role in ["admin", "instructor"] for role in current_user.roles
    ):
        raise HTTPException(status_code=403, detail="Not authorized to view this record")

    record = db.query(ScormRecord).filter(
        ScormRecord.user_id == user_id,
        ScormRecord.module_id == module_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="SCORM record not found")

    return record


@router.get("/records/{user_id}", response_model=List[ScormDataResponse])
def list_user_scorm_records(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all SCORM records for a user"""
    # Students can only view their own records
    if user_id != current_user.id and not any(
        role in ["admin", "instructor"] for role in current_user.roles
    ):
        raise HTTPException(status_code=403, detail="Not authorized to view these records")

    records = db.query(ScormRecord).filter(ScormRecord.user_id == user_id).all()
    return records


@router.delete("/records/{user_id}/{module_id}", status_code=204)
def delete_scorm_record(
    user_id: UUID,
    module_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete SCORM record (admin/instructor only)"""
    if not any(role in ["admin", "instructor"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin or Instructor role required")

    record = db.query(ScormRecord).filter(
        ScormRecord.user_id == user_id,
        ScormRecord.module_id == module_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="SCORM record not found")

    db.delete(record)
    db.commit()
    return None
