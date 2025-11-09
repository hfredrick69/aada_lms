"""Student management router - wrapper around users filtered by student role"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from uuid import UUID
import os

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.role import Role
from app.core.security import get_password_hash
from app.routers.auth import get_current_user
from app.utils.encryption import encrypt_value, decrypt_value
from pydantic import BaseModel, EmailStr

# Get encryption key from environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "dev_encryption_key_change_in_production_32bytes")


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


def decrypt_user_for_response(db: Session, user: User) -> StudentResponse:
    """Convert User model to StudentResponse with decrypted PII fields"""
    return StudentResponse(
        id=user.id,
        email=decrypt_value(db, user.email),
        first_name=decrypt_value(db, user.first_name),
        last_name=decrypt_value(db, user.last_name),
        status=user.status or "active"
    )


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

    # Decrypt PII fields before returning
    return [decrypt_user_for_response(db, student) for student in students]


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(data: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new student (admin/staff only)"""
    if not any(role in ["admin", "staff"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin or staff role required")

    # Check if email exists by decrypting email field in SQL
    result = db.execute(
        text("""
            SELECT id FROM users
            WHERE pgp_sym_decrypt(decode(email, 'base64'), :key) = :email
            LIMIT 1
        """),
        {"key": ENCRYPTION_KEY, "email": data.email}
    ).fetchone()

    if result:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user with encrypted PII
    user = User(
        email=encrypt_value(db, data.email),
        password_hash=get_password_hash(data.password),
        first_name=encrypt_value(db, data.first_name),
        last_name=encrypt_value(db, data.last_name)
    )

    # Assign student role
    student_role = db.query(Role).filter(Role.name == "student").first()
    if student_role:
        user.roles.append(student_role)

    db.add(user)
    db.commit()
    db.refresh(user)

    # Return decrypted response
    return decrypt_user_for_response(db, user)


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

    return decrypt_user_for_response(db, user)


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

    # Check if email needs updating
    if data.email:
        current_email = decrypt_value(db, user.email)
        if data.email != current_email:
            # Check if new email exists
            result = db.execute(
                text("""
                    SELECT id FROM users
                    WHERE pgp_sym_decrypt(decode(email, 'base64'), :key) = :email
                    AND id != :user_id
                    LIMIT 1
                """),
                {"key": ENCRYPTION_KEY, "email": data.email, "user_id": user.id}
            ).fetchone()
            if result:
                raise HTTPException(status_code=400, detail="Email already in use")
            user.email = encrypt_value(db, data.email)

    if data.first_name:
        user.first_name = encrypt_value(db, data.first_name)
    if data.last_name:
        user.last_name = encrypt_value(db, data.last_name)
    if data.status:
        user.status = data.status

    db.commit()
    db.refresh(user)
    return decrypt_user_for_response(db, user)


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
