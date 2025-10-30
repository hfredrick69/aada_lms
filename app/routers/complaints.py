from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models.compliance.complaint import Complaint
from app.db.session import get_db
from app.schemas.complaints import (
    ComplaintCreate,
    ComplaintRead,
    ComplaintUpdate,
    ComplaintStatus,
)

router = APIRouter(prefix="/complaints", tags=["complaints"])

GNPEC_APPEAL_INFO = (
    "Appeals may be directed to GNPEC within 90 days of institutional resolution. "
    "Contact: gnpec@tcsg.edu, 1800 Century Place N.E., Suite 550, Atlanta, GA 30345."
)


def _serialize(record: Complaint) -> ComplaintRead:
    base_model = ComplaintRead.model_validate(record, from_attributes=True)
    return base_model.model_copy(update={"gnpec_appeal_info": GNPEC_APPEAL_INFO})


@router.get("", response_model=List[ComplaintRead])
def list_complaints(
    status_filter: Optional[ComplaintStatus] = Query(
        default=None, description="Filter by complaint status."
    ),
    db: Session = Depends(get_db),
) -> List[ComplaintRead]:
    query = db.query(Complaint)
    if status_filter:
        query = query.filter(Complaint.status == status_filter)
    records = query.order_by(desc(Complaint.submitted_at)).all()
    return [_serialize(record) for record in records]


@router.post("", response_model=ComplaintRead, status_code=status.HTTP_201_CREATED)
def create_complaint(
    payload: ComplaintCreate, db: Session = Depends(get_db)
) -> ComplaintRead:
    record = Complaint(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


def _ensure_resolution_requirements(record: Complaint, update: dict) -> None:
    new_status = update.get("status")
    notes = update.get("resolution_notes") or record.resolution_notes
    resolved_at = update.get("resolution_at") or record.resolution_at
    if new_status == "resolved":
        if not notes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resolution notes are required to resolve a complaint.",
            )
        if not resolved_at:
            update["resolution_at"] = datetime.now(timezone.utc)
    if new_status == "appealed" and record.status != "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only resolved complaints can be appealed to GNPEC.",
        )
    if new_status == "appealed":
        update.setdefault("resolution_at", datetime.now(timezone.utc))
        update.setdefault("resolution_notes", notes or "Student initiated GNPEC appeal.")


@router.put("/{complaint_id}", response_model=ComplaintRead)
def update_complaint(
    complaint_id: UUID, payload: ComplaintUpdate, db: Session = Depends(get_db)
) -> ComplaintRead:
    record = db.get(Complaint, complaint_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    update_data = payload.model_dump(exclude_unset=True)
    if "status" in update_data:
        _ensure_resolution_requirements(record, update_data)
    for key, value in update_data.items():
        setattr(record, key, value)
    if "status" in update_data and update_data["status"] == "in_review" and not record.resolution_notes:
        record.resolution_notes = "Under review by compliance team."
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.get("/{complaint_id}", response_model=ComplaintRead)
def get_complaint(complaint_id: UUID, db: Session = Depends(get_db)) -> ComplaintRead:
    record = db.get(Complaint, complaint_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    return _serialize(record)


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_complaint(complaint_id: UUID, db: Session = Depends(get_db)) -> None:
    record = db.get(Complaint, complaint_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    db.delete(record)
    db.commit()
