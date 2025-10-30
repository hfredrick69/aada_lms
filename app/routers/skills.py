from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models.compliance.skills import SkillCheckoff
from app.db.session import get_db
from app.schemas.skills import (
    SkillCheckoffCreate,
    SkillCheckoffRead,
    SkillCheckoffUpdate,
)

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=List[SkillCheckoffRead])
def list_skills(db: Session = Depends(get_db)) -> List[SkillCheckoffRead]:
    return (
        db.query(SkillCheckoff)
        .order_by(desc(SkillCheckoff.signed_at), SkillCheckoff.id)
        .all()
    )


@router.post("", response_model=SkillCheckoffRead, status_code=status.HTTP_201_CREATED)
def create_skill_checkoff(
    payload: SkillCheckoffCreate, db: Session = Depends(get_db)
) -> SkillCheckoffRead:
    record = SkillCheckoff(**payload.model_dump())
    if record.status in {"approved", "rejected"}:
        if not record.evaluator_name or not record.evaluator_license:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evaluator name and license are required for approvals or rejections.",
            )
        record.signed_at = record.signed_at or datetime.now(timezone.utc)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _apply_skill_update(record: SkillCheckoff, data: dict) -> None:
    if "status" in data:
        new_status = data["status"]
        evaluator_name = data.get("evaluator_name", record.evaluator_name)
        evaluator_license = data.get("evaluator_license", record.evaluator_license)
        if new_status in {"approved", "rejected"}:
            if not evaluator_name or not evaluator_license:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Evaluator details are required to change status to approved or rejected.",
                )
            record.evaluator_name = evaluator_name
            record.evaluator_license = evaluator_license
            record.signed_at = data.get("signed_at", record.signed_at) or datetime.now(timezone.utc)
        else:
            if "evaluator_name" in data:
                record.evaluator_name = data["evaluator_name"]
            if "evaluator_license" in data:
                record.evaluator_license = data["evaluator_license"]
            if "signed_at" in data:
                record.signed_at = data["signed_at"]
        record.status = new_status
    else:
        if "evaluator_name" in data:
            record.evaluator_name = data["evaluator_name"]
        if "evaluator_license" in data:
            record.evaluator_license = data["evaluator_license"]
        if "signed_at" in data:
            record.signed_at = data["signed_at"]
    if "evidence_url" in data:
        record.evidence_url = data["evidence_url"]


@router.put("/{checkoff_id}", response_model=SkillCheckoffRead)
def update_skill_checkoff(
    checkoff_id: UUID,
    payload: SkillCheckoffUpdate,
    db: Session = Depends(get_db),
) -> SkillCheckoffRead:
    record = db.get(SkillCheckoff, checkoff_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill checkoff not found")
    update_data = payload.model_dump(exclude_unset=True)
    _apply_skill_update(record, update_data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{checkoff_id}", response_model=SkillCheckoffRead)
def get_skill_checkoff(
    checkoff_id: UUID, db: Session = Depends(get_db)
) -> SkillCheckoffRead:
    record = db.get(SkillCheckoff, checkoff_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill checkoff not found")
    return record


@router.delete("/{checkoff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill_checkoff(checkoff_id: UUID, db: Session = Depends(get_db)) -> None:
    record = db.get(SkillCheckoff, checkoff_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill checkoff not found")
    db.delete(record)
    db.commit()
