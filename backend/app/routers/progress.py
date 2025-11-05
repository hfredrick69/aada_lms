"""Student progress tracking router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.enrollment import Enrollment, ModuleProgress
from app.db.models.program import Module
from app.db.models.xapi import XapiStatement
from app.routers.auth import get_current_user


class ProgressUpdate(BaseModel):
    enrollment_id: UUID
    module_id: UUID
    scorm_status: Optional[str] = None  # incomplete/completed/passed/failed
    score: Optional[int] = None
    progress_pct: Optional[int] = None


class ModuleProgressResponse(BaseModel):
    id: UUID
    enrollment_id: UUID
    module_id: UUID
    module_code: str
    module_title: str
    scorm_status: Optional[str]
    score: Optional[int]
    progress_pct: Optional[int]
    last_activity: Optional[datetime]

    class Config:
        from_attributes = True


class OverallProgressResponse(BaseModel):
    user_id: UUID
    enrollment_id: UUID
    program_name: str
    total_modules: int
    completed_modules: int
    completion_percentage: float
    modules: List[ModuleProgressResponse]


router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{user_id}", response_model=OverallProgressResponse)
def get_user_progress(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall progress for a user"""
    # Students can only see their own progress
    if user_id != current_user.id and not any(role in ["admin", "instructor"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized to view this progress")

    # Get active enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == user_id,
        Enrollment.status == "active"
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="No active enrollment found")

    # Get all modules in the program
    modules = db.query(Module).filter(
        Module.program_id == enrollment.program_id
    ).order_by(Module.position).all()

    if not modules:
        return OverallProgressResponse(
            user_id=user_id,
            enrollment_id=enrollment.id,
            program_name="Unknown",
            total_modules=0,
            completed_modules=0,
            completion_percentage=0.0,
            modules=[]
        )

    # Get progress for each module
    module_progress_list = []
    completed_count = 0

    for module in modules:
        # Get module progress record
        progress = db.query(ModuleProgress).filter(
            ModuleProgress.enrollment_id == enrollment.id,
            ModuleProgress.module_id == module.id
        ).first()

        # Get last activity from xAPI statements
        last_statement = db.query(XapiStatement).filter(
            XapiStatement.actor['mbox'].astext == f"mailto:{current_user.email}"
        ).order_by(XapiStatement.stored_at.desc()).first()

        # Default values if no progress record exists
        scorm_status = progress.scorm_status if progress else "incomplete"
        score = progress.score if progress else None
        progress_pct = progress.progress_pct if progress else 0

        # Count completed modules
        if scorm_status in ["completed", "passed"]:
            completed_count += 1

        module_progress_list.append(ModuleProgressResponse(
            id=progress.id if progress else module.id,
            enrollment_id=enrollment.id,
            module_id=module.id,
            module_code=module.code,
            module_title=module.title,
            scorm_status=scorm_status,
            score=score,
            progress_pct=progress_pct,
            last_activity=last_statement.stored_at if last_statement else None
        ))

    total_modules = len(modules)
    completion_percentage = (completed_count / total_modules * 100) if total_modules > 0 else 0.0

    return OverallProgressResponse(
        user_id=user_id,
        enrollment_id=enrollment.id,
        program_name=f"Program {enrollment.program_id}",  # TODO: Join with Program table
        total_modules=total_modules,
        completed_modules=completed_count,
        completion_percentage=completion_percentage,
        modules=module_progress_list
    )


@router.get("/{user_id}/module/{module_id}", response_model=ModuleProgressResponse)
def get_module_progress(
    user_id: UUID,
    module_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress for a specific module"""
    # Students can only see their own progress
    if user_id != current_user.id and not any(role in ["admin", "instructor"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized to view this progress")

    # Get active enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == user_id,
        Enrollment.status == "active"
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="No active enrollment found")

    # Get module
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get progress record
    progress = db.query(ModuleProgress).filter(
        ModuleProgress.enrollment_id == enrollment.id,
        ModuleProgress.module_id == module_id
    ).first()

    # Get last activity from xAPI
    last_statement = db.query(XapiStatement).filter(
        XapiStatement.actor['mbox'].astext == f"mailto:{current_user.email}"
    ).order_by(XapiStatement.stored_at.desc()).first()

    if not progress:
        # Create default progress if none exists
        return ModuleProgressResponse(
            id=module.id,
            enrollment_id=enrollment.id,
            module_id=module.id,
            module_code=module.code,
            module_title=module.title,
            scorm_status="incomplete",
            score=None,
            progress_pct=0,
            last_activity=last_statement.stored_at if last_statement else None
        )

    return ModuleProgressResponse(
        id=progress.id,
        enrollment_id=enrollment.id,
        module_id=module.id,
        module_code=module.code,
        module_title=module.title,
        scorm_status=progress.scorm_status,
        score=progress.score,
        progress_pct=progress.progress_pct,
        last_activity=last_statement.stored_at if last_statement else None
    )


@router.post("/", response_model=ModuleProgressResponse, status_code=201)
def update_progress(
    progress_data: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update progress for a module (students can update their own)"""
    # Get enrollment to verify ownership
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == progress_data.enrollment_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Students can only update their own progress
    is_owner = enrollment.user_id == current_user.id
    is_authorized = any(role in ["admin", "instructor"] for role in current_user.roles)
    if not is_owner and not is_authorized:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this progress"
        )

    # Get module
    module = db.query(Module).filter(Module.id == progress_data.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get or create progress record
    progress = db.query(ModuleProgress).filter(
        ModuleProgress.enrollment_id == progress_data.enrollment_id,
        ModuleProgress.module_id == progress_data.module_id
    ).first()

    if not progress:
        progress = ModuleProgress(
            enrollment_id=progress_data.enrollment_id,
            module_id=progress_data.module_id,
            scorm_status=progress_data.scorm_status or "incomplete",
            score=progress_data.score,
            progress_pct=progress_data.progress_pct or 0
        )
        db.add(progress)
    else:
        # Update existing progress
        if progress_data.scorm_status:
            progress.scorm_status = progress_data.scorm_status
        if progress_data.score is not None:
            progress.score = progress_data.score
        if progress_data.progress_pct is not None:
            progress.progress_pct = progress_data.progress_pct

    db.commit()
    db.refresh(progress)

    # Get last activity
    last_statement = db.query(XapiStatement).filter(
        XapiStatement.actor['mbox'].astext == f"mailto:{current_user.email}"
    ).order_by(XapiStatement.stored_at.desc()).first()

    return ModuleProgressResponse(
        id=progress.id,
        enrollment_id=progress.enrollment_id,
        module_id=progress.module_id,
        module_code=module.code,
        module_title=module.title,
        scorm_status=progress.scorm_status,
        score=progress.score,
        progress_pct=progress.progress_pct,
        last_activity=last_statement.stored_at if last_statement else None
    )
