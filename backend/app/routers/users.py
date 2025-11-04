"""User management router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.core.security import get_current_user, hash_password
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    status: str | None = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    status: str

    class Config:
        from_attributes = True


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all users (admin only)"""
    users = db.query(User).all()
    return users


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new user (admin only)"""
    # Check if email exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID, data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None
