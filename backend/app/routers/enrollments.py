"""Enrollment management router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import date

from app.db.session import get_db
from app.db.models.enrollment import Enrollment
from app.db.models.user import User
from app.routers.auth import get_current_user


class EnrollmentCreate(BaseModel):
    user_id: UUID
    program_id: UUID
    start_date: date
    expected_end_date: Optional[date] = None
    status: Optional[str] = "active"


class EnrollmentUpdate(BaseModel):
    start_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    status: Optional[str] = None


class EnrollmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    program_id: UUID
    start_date: date
    expected_end_date: Optional[date]
    status: str

    class Config:
        from_attributes = True


router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("", response_model=List[EnrollmentResponse])
def list_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List enrollments (students see their own, admin/instructor see all)"""
    # Students can only see their own enrollments
    if not any(role in ["admin", "instructor", "staff"] for role in current_user.roles):
        enrollments = db.query(Enrollment).filter(
            Enrollment.user_id == current_user.id
        ).all()
    else:
        # Admin/instructor can see all
        enrollments = db.query(Enrollment).all()

    return enrollments


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def get_enrollment(
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific enrollment by ID"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Students can only view their own enrollments
    if enrollment.user_id != current_user.id and not any(
        role in ["admin", "instructor", "staff"] for role in current_user.roles
    ):
        raise HTTPException(status_code=403, detail="Not authorized to view this enrollment")

    return enrollment


@router.post("", response_model=EnrollmentResponse, status_code=201)
def create_enrollment(
    enrollment_data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new enrollment (admin/staff only)"""
    if not any(role in ["admin", "staff"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin or Staff role required to create enrollments")

    # Create new enrollment
    enrollment = Enrollment(
        user_id=enrollment_data.user_id,
        program_id=enrollment_data.program_id,
        start_date=enrollment_data.start_date,
        expected_end_date=enrollment_data.expected_end_date,
        status=enrollment_data.status
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
def update_enrollment(
    enrollment_id: UUID,
    enrollment_data: EnrollmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update enrollment (admin/staff only)"""
    if not any(role in ["admin", "staff"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin or Staff role required to update enrollments")

    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Update fields if provided
    if enrollment_data.start_date is not None:
        enrollment.start_date = enrollment_data.start_date
    if enrollment_data.expected_end_date is not None:
        enrollment.expected_end_date = enrollment_data.expected_end_date
    if enrollment_data.status is not None:
        enrollment.status = enrollment_data.status

    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.delete("/{enrollment_id}", status_code=204)
def delete_enrollment(
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete enrollment (admin only)"""
    if not any(role in ["admin"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin role required to delete enrollments")

    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    db.delete(enrollment)
    db.commit()
    return None
