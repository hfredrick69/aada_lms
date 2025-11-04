from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.compliance.attendance import AttendanceLog
from app.db.session import get_db
from app.schemas.attendance import AttendanceCreate, AttendanceRead, AttendanceUpdate

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("", response_model=List[AttendanceRead])
def list_attendance(db: Session = Depends(get_db)) -> List[AttendanceRead]:
    return (
        db.query(AttendanceLog)
        .order_by(AttendanceLog.started_at.desc())
        .all()
    )


@router.post("", response_model=AttendanceRead, status_code=status.HTTP_201_CREATED)
def create_attendance(
    payload: AttendanceCreate, db: Session = Depends(get_db)
) -> AttendanceRead:
    record = AttendanceLog(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{attendance_id}", response_model=AttendanceRead)
def get_attendance(attendance_id: UUID, db: Session = Depends(get_db)) -> AttendanceRead:
    record = db.get(AttendanceLog, attendance_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")
    return record


@router.put("/{attendance_id}", response_model=AttendanceRead)
def update_attendance(
    attendance_id: UUID, payload: AttendanceUpdate, db: Session = Depends(get_db)
) -> AttendanceRead:
    record = db.get(AttendanceLog, attendance_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "started_at" in update_data:
        record.started_at = update_data["started_at"]
    if "ended_at" in update_data:
        if update_data["ended_at"] <= record.started_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ended_at must be after started_at",
            )
        record.ended_at = update_data["ended_at"]
    if "session_type" in update_data:
        record.session_type = update_data["session_type"]
    if "session_ref" in update_data:
        record.session_ref = update_data["session_ref"]

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(attendance_id: UUID, db: Session = Depends(get_db)) -> None:
    record = db.get(AttendanceLog, attendance_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")
    db.delete(record)
    db.commit()
