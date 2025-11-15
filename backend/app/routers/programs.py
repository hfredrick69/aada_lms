from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.db.session import get_db
from app.db.models.program import Program, Module
from app.routers.auth import get_current_user
from app.db.models.user import User


router = APIRouter(prefix="/programs", tags=["programs"])


# Pydantic schemas for validation
class ProgramCreate(BaseModel):
    code: str
    name: str
    credential_level: str
    total_clock_hours: int


class ProgramUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    credential_level: Optional[str] = None
    total_clock_hours: Optional[int] = None


class ModuleCreate(BaseModel):
    code: str
    title: str
    delivery_type: str
    clock_hours: int
    requires_in_person: bool = False
    position: int


class ModuleUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None
    delivery_type: Optional[str] = None
    clock_hours: Optional[int] = None
    requires_in_person: Optional[bool] = None
    position: Optional[int] = None


# Helper function to check admin/instructor/staff role
def require_admin_or_instructor(current_user: User):
    if not any(role in ["admin", "instructor", "staff"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin, Instructor, or Staff role required")


# ============ PROGRAM ENDPOINTS ============

@router.get("")
def list_programs(db: Session = Depends(get_db)):
    """List all programs"""
    return db.query(Program).all()


@router.get("/{program_id}")
def get_program(program_id: UUID, db: Session = Depends(get_db)):
    """Get a specific program"""
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program


@router.post("", status_code=201)
def create_program(
    program_data: ProgramCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new program (admin/instructor only)"""
    require_admin_or_instructor(current_user)

    # Check for duplicate code
    existing = db.query(Program).filter(Program.code == program_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Program code already exists")

    program = Program(**program_data.model_dump())
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.put("/{program_id}")
def update_program(
    program_id: UUID,
    program_data: ProgramUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing program (admin/instructor only)"""
    require_admin_or_instructor(current_user)

    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    # Check for duplicate code if updating code
    if program_data.code and program_data.code != program.code:
        existing = db.query(Program).filter(Program.code == program_data.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="Program code already exists")

    # Update fields
    for field, value in program_data.model_dump(exclude_unset=True).items():
        setattr(program, field, value)

    db.commit()
    db.refresh(program)
    return program


@router.delete("/{program_id}")
def delete_program(
    program_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a program (admin only)"""
    if not any(role in ["admin"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin role required")

    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    db.delete(program)
    db.commit()
    return {"message": "Program deleted successfully"}


# ============ MODULE ENDPOINTS ============

@router.get("/{program_id}/modules")
def list_modules(program_id: UUID, db: Session = Depends(get_db)):
    """List all modules for a program"""
    # Verify program exists
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    return db.query(Module).filter(Module.program_id == program_id).order_by(Module.position).all()


@router.get("/{program_id}/modules/{module_id}")
def get_module(program_id: UUID, module_id: UUID, db: Session = Depends(get_db)):
    """Get a specific module"""
    module = db.query(Module).filter(
        Module.id == module_id,
        Module.program_id == program_id
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


@router.post("/{program_id}/modules", status_code=201)
def create_module(
    program_id: UUID,
    module_data: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new module in a program (admin/instructor only)"""
    require_admin_or_instructor(current_user)

    # Verify program exists
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    # Check for duplicate code within program
    existing = db.query(Module).filter(
        Module.program_id == program_id,
        Module.code == module_data.code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Module code already exists in this program")

    module = Module(program_id=program_id, **module_data.model_dump())
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


@router.put("/{program_id}/modules/{module_id}")
def update_module(
    program_id: UUID,
    module_id: UUID,
    module_data: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing module (admin/instructor only)"""
    require_admin_or_instructor(current_user)

    module = db.query(Module).filter(
        Module.id == module_id,
        Module.program_id == program_id
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Check for duplicate code if updating code
    if module_data.code and module_data.code != module.code:
        existing = db.query(Module).filter(
            Module.program_id == program_id,
            Module.code == module_data.code
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Module code already exists in this program")

    # Update fields
    for field, value in module_data.model_dump(exclude_unset=True).items():
        setattr(module, field, value)

    db.commit()
    db.refresh(module)
    return module


@router.delete("/{program_id}/modules/{module_id}")
def delete_module(
    program_id: UUID,
    module_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a module (admin only)"""
    if not any(role in ["admin"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin role required")

    module = db.query(Module).filter(
        Module.id == module_id,
        Module.program_id == program_id
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    db.delete(module)
    db.commit()
    return {"message": "Module deleted successfully"}
