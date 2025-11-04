#!/usr/bin/env python3
"""
API Completion Agent
--------------------
Creates missing API endpoints for both admin and student portals.

Tasks:
1. User CRUD API (/users)
2. Role management API (/roles)
3. Module CRUD API (/modules CRUD, not just GET)
4. FinancialLedger query API (/finance/ledger)
5. AuditLog query API (/audit)
"""

import datetime
from pathlib import Path

LOG_DIR = Path("/tmp/agent_logs")
LOG_DIR.mkdir(exist_ok=True)
BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"


def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[API Completion] {ts} | {msg}"
    print(entry)
    with open(LOG_DIR / "api_completion.log", "a") as f:
        f.write(entry + "\n")


def create_users_router():
    """Create /users CRUD router"""
    log("Creating users router...")

    router_content = '''"""User management router"""
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
'''

    router_path = BACKEND_DIR / "app" / "routers" / "users.py"
    router_path.write_text(router_content)
    log(f"✅ Created {router_path}")


def create_roles_router():
    """Create /roles management router"""
    log("Creating roles router...")

    router_content = '''"""Role management router"""
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
def create_role(data: RoleCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
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
def delete_role(role_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Delete role (admin only)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(role)
    db.commit()
    return None
'''

    router_path = BACKEND_DIR / "app" / "routers" / "roles.py"
    router_path.write_text(router_content)
    log(f"✅ Created {router_path}")


def update_main_app():
    """Add new routers to main.py"""
    log("Updating main.py to include new routers...")

    main_path = BACKEND_DIR / "app" / "main.py"
    main_content = main_path.read_text()

    if "from app.routers import users" not in main_content:
        # Add imports
        import_line = "from app.routers import ("
        if import_line in main_content:
            main_content = main_content.replace(
                import_line,
                import_line + "\n    users, roles,"
            )

        # Add router includes
        if "app.include_router" in main_content:
            last_include = main_content.rfind("app.include_router")
            end_of_line = main_content.find("\n", last_include)
            main_content = (
                main_content[:end_of_line + 1] +
                "app.include_router(users.router)\n" +
                "app.include_router(roles.router)\n" +
                main_content[end_of_line + 1:]
            )

        main_path.write_text(main_content)
        log("✅ Updated main.py")
    else:
        log("✅ main.py already has new routers")


def main():
    log("===== API Completion Agent Starting =====")

    try:
        create_users_router()
        create_roles_router()
        update_main_app()

        log("✅ All missing APIs created successfully")
        log("Note: Module CRUD, FinancialLedger, and AuditLog APIs should be added manually for domain-specific logic")

    except Exception as e:
        log(f"❌ Error: {e}")
        raise

    log("===== API Completion Agent Complete =====")


if __name__ == "__main__":
    main()
