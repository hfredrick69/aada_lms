"""Student management router - wrapper around users filtered by student role"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.role import Role
from app.core.security import get_password_hash
from app.routers.auth import get_current_user
from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class StudentUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    status: str | None = None


class StudentResponse(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    status: str

    class Config:
        from_attributes = True


router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=List[StudentResponse])
def list_students(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all students (admin/staff only)"""
    if not any(role in ["admin", "staff"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin or staff role required")

    # Get student role
    student_role = db.query(Role).filter(Role.name == "student").first()
    if not student_role:
        return []

    # Get all users with student role
    students = db.query(User).join(User.roles).filter(Role.id == student_role.id).all()
    return students


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(data: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new student (admin/staff only)"""
    if not any(role in ["admin", "staff"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin or staff role required")

    # Check if email exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name
    )

    # Assign student role
    student_role = db.query(Role).filter(Role.name == "student").first()
    if student_role:
        user.roles.append(student_role)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get student by ID (admin/staff or self)"""
    # Students can view their own profile or admin/staff can view anyone
    if student_id != current_user.id and not any(role in ["admin", "staff"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized to view this student")

    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    # Verify user has student role
    student_role = db.query(Role).filter(Role.name == "student").first()
    if student_role and student_role not in user.roles:
        raise HTTPException(status_code=404, detail="User is not a student")

    return user


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: UUID, data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update student (admin/staff only)"""
    if not any(role in ["admin", "staff"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin or staff role required")

    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    # Verify user has student role
    student_role = db.query(Role).filter(Role.name == "student").first()
    if student_role and student_role not in user.roles:
        raise HTTPException(status_code=404, detail="User is not a student")

    if data.email and data.email != user.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = data.email

    if data.first_name:
        user.first_name = data.first_name
    if data.last_name:
        user.last_name = data.last_name
    if data.status:
        user.status = data.status

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete student (admin only)"""
    if not any(role in ["admin"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin role required")

    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    # Verify user has student role
    student_role = db.query(Role).filter(Role.name == "student").first()
    if student_role and student_role not in user.roles:
        raise HTTPException(status_code=404, detail="User is not a student")

    db.delete(user)
    db.commit()
    return None
