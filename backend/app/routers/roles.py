"""Role management router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.models.role import Role
from app.core.security import get_current_user
from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None

    class Config:
        from_attributes = True


router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=List[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    """List all roles"""
    roles = db.query(Role).all()
    return roles


@router.post("/", response_model=RoleResponse, status_code=201)
def create_role(data: RoleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Create new role (admin only)"""
    existing = db.query(Role).filter(Role.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")

    role = Role(name=data.name, description=data.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=204)
def delete_role(role_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Delete role (admin only)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(role)
    db.commit()
    return None
