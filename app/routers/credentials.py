from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.compliance.credential import Credential
from app.db.models.enrollment import Enrollment, ModuleProgress
from app.db.models.program import Module
from app.db.session import get_db
from app.schemas.credentials import (
    CredentialCreate,
    CredentialRead,
    CredentialUpdate,
)

router = APIRouter(prefix="/credentials", tags=["credentials"])


def _find_enrollment(db: Session, user_id: UUID, program_id: UUID) -> Enrollment:
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user_id, Enrollment.program_id == program_id)
        .order_by(Enrollment.start_date.desc())
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No enrollment found for user and program.",
        )
    return enrollment


def _is_program_completed(db: Session, enrollment: Enrollment) -> bool:
    progress_records = (
        db.query(ModuleProgress, Module)
        .join(Module, Module.id == ModuleProgress.module_id)
        .filter(Module.program_id == enrollment.program_id, ModuleProgress.enrollment_id == enrollment.id)
        .all()
    )
    if not progress_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No module progress records found; program cannot be marked complete.",
        )
    completed_modules = 0
    for progress, _module in progress_records:
        if (progress.progress_pct or 0) >= 100 or (progress.scorm_status or "").lower() in {"passed", "completed"}:
            completed_modules += 1
    return completed_modules == len(progress_records)


def _ensure_credential_unique(db: Session, user_id: UUID, program_id: UUID) -> None:
    exists = (
        db.query(Credential)
        .filter(Credential.user_id == user_id, Credential.program_id == program_id)
        .first()
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Credential already issued for this user and program.",
        )


@router.get("", response_model=List[CredentialRead])
def list_credentials(db: Session = Depends(get_db)) -> List[CredentialRead]:
    return db.query(Credential).order_by(Credential.issued_at.desc()).all()


@router.post("", response_model=CredentialRead, status_code=status.HTTP_201_CREATED)
def create_credential(
    payload: CredentialCreate, db: Session = Depends(get_db)
) -> CredentialRead:
    enrollment = _find_enrollment(db, payload.user_id, payload.program_id)
    if not _is_program_completed(db, enrollment):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program completion requirements not met; cannot issue credential.",
        )
    _ensure_credential_unique(db, payload.user_id, payload.program_id)
    issued_at = payload.issued_at or datetime.now(timezone.utc)
    record = Credential(**payload.model_dump())
    record.issued_at = issued_at
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{credential_id}", response_model=CredentialRead)
def get_credential(credential_id: UUID, db: Session = Depends(get_db)) -> CredentialRead:
    record = db.get(Credential, credential_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    return record


@router.put("/{credential_id}", response_model=CredentialRead)
def update_credential(
    credential_id: UUID, payload: CredentialUpdate, db: Session = Depends(get_db)
) -> CredentialRead:
    record = db.get(Credential, credential_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    if "issued_at" in update_data and record.issued_at.tzinfo is None:
        record.issued_at = record.issued_at.replace(tzinfo=timezone.utc)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_credential(credential_id: UUID, db: Session = Depends(get_db)) -> None:
    record = db.get(Credential, credential_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    db.delete(record)
    db.commit()
