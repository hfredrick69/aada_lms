from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models.compliance.extern import Externship
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.externships import (
    ExternshipCreate,
    ExternshipRead,
    ExternshipUpdate,
)
from app.utils.encryption import decrypt_value

router = APIRouter(prefix="/externships", tags=["externships"])


def _validate_verification(data: dict, existing: Externship | None = None) -> dict:
    verified = data.get("verified")
    doc_url = data.get("verification_doc_url")
    if verified is None and existing is not None:
        verified = existing.verified
    if verified:
        doc_url = doc_url or (existing.verification_doc_url if existing else None)
        if not doc_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification documentation URL is required when marking externship as verified.",
            )
        data.setdefault("verification_doc_url", doc_url)
        data.setdefault("verified_at", datetime.now(timezone.utc))
    return data


@router.get("", response_model=List[ExternshipRead])
def list_externships(db: Session = Depends(get_db)) -> List[ExternshipRead]:
    externships = (
        db.query(Externship)
        .order_by(desc(Externship.verified), desc(Externship.verified_at), Externship.id)
        .all()
    )

    # Add decrypted student names
    result = []
    for ext in externships:
        user = db.query(User).filter(User.id == ext.user_id).first()
        student_name = None
        if user:
            first_name = decrypt_value(db, user.first_name)
            last_name = decrypt_value(db, user.last_name)
            student_name = f"{first_name} {last_name}"

        result.append(
            ExternshipRead(
                id=ext.id,
                user_id=ext.user_id,
                site_name=ext.site_name,
                site_address=ext.site_address,
                supervisor_name=ext.supervisor_name,
                supervisor_email=ext.supervisor_email,
                total_hours=ext.total_hours,
                verified=ext.verified,
                verification_doc_url=ext.verification_doc_url,
                verified_at=ext.verified_at,
                student_name=student_name
            )
        )
    return result


@router.post("", response_model=ExternshipRead, status_code=status.HTTP_201_CREATED)
def create_externship(
    payload: ExternshipCreate, db: Session = Depends(get_db)
) -> ExternshipRead:
    data = payload.model_dump()
    _validate_verification(data)
    record = Externship(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{externship_id}", response_model=ExternshipRead)
def get_externship(externship_id: UUID, db: Session = Depends(get_db)) -> ExternshipRead:
    record = db.get(Externship, externship_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Externship not found")
    return record


@router.put("/{externship_id}", response_model=ExternshipRead)
def update_externship(
    externship_id: UUID, payload: ExternshipUpdate, db: Session = Depends(get_db)
) -> ExternshipRead:
    record = db.get(Externship, externship_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Externship not found")
    data = payload.model_dump(exclude_unset=True)
    data = _validate_verification(data, existing=record)
    for key, value in data.items():
        setattr(record, key, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{externship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_externship(externship_id: UUID, db: Session = Depends(get_db)) -> None:
    record = db.get(Externship, externship_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Externship not found")
    db.delete(record)
    db.commit()
