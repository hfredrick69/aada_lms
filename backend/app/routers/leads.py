"""Lead management API router for CRM."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.db.models.crm.lead import Lead, LeadSource
from app.db.models.crm.activity import Activity
from app.db.models.user import User
from app.db.models.program import Program
from app.routers.auth import get_current_user
from app.core.rbac import RBACChecker
from app.schemas.lead import (
    LeadCreate, LeadUpdate, LeadResponse, LeadDetailResponse, LeadListResponse,
    LeadSourceCreate, LeadSourceResponse,
    ActivityCreate, ActivityUpdate, ActivityResponse, ActivityDetailResponse
)


router = APIRouter(prefix="/crm/leads", tags=["crm-leads"])


# Helper function to check if user is admissions staff
def require_admissions_staff(current_user: User = Depends(get_current_user)):
    """Require admissions staff role."""
    rbac = RBACChecker(current_user)
    if not (rbac.has_role("admissions_counselor") or
            rbac.has_role("admissions_manager") or
            rbac.is_admin() or rbac.is_staff()):
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admissions staff privileges required."
        )
    return current_user


# =============================================================================
# LEAD SOURCE ENDPOINTS
# =============================================================================

@router.get("/sources", response_model=List[LeadSourceResponse])
def list_lead_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admissions_staff)
):
    """List all lead sources."""
    sources = db.query(LeadSource).filter(LeadSource.is_active.is_(True)).all()
    return sources


@router.post("/sources", response_model=LeadSourceResponse, status_code=201)
def create_lead_source(
    source_data: LeadSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admissions_staff)
):
    """Create a new lead source."""
    # Check if source already exists
    existing = db.query(LeadSource).filter(LeadSource.name == source_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Lead source with this name already exists")

    source = LeadSource(**source_data.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


# =============================================================================
# LEAD CRUD ENDPOINTS
# =============================================================================

@router.get("", response_model=LeadListResponse)
def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    assigned_to_id: Optional[UUID] = None,
    lead_source_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admissions_staff)
):
    """List leads with optional filtering and pagination."""
    query = db.query(Lead)

    # Apply filters
    if status:
        query = query.filter(Lead.lead_status == status)
    if assigned_to_id:
        query = query.filter(Lead.assigned_to_id == assigned_to_id)
    if lead_source_id:
        query = query.filter(Lead.lead_source_id == lead_source_id)

    # Get total count
    total = query.count()

    # Apply pagination
    leads = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()

    return LeadListResponse(total=total, leads=leads)


@router.post("", response_model=LeadResponse, status_code=201)
def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admissions_staff)
):
    """Create a new lead."""
    # Validate lead_source_id exists
    source = db.query(LeadSource).filter(LeadSource.id == lead_data.lead_source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Lead source not found")

    # Validate program_interest_id if provided
    if lead_data.program_interest_id:
        program = db.query(Program).filter(Program.id == lead_data.program_interest_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")

    # Check if lead with this email already exists
    existing = db.query(Lead).filter(Lead.email == lead_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Lead with this email already exists")

    # Create lead
    lead = Lead(**lead_data.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Create activity log
    activity = Activity(
        entity_type="lead",
        entity_id=lead.id,
        activity_type="note",
        subject="Lead Created",
        description=f"Lead created by {current_user.first_name} {current_user.last_name}",
        created_by_id=current_user.id
    )
    db.add(activity)
    db.commit()

    return lead


@router.get("/{lead_id}", response_model=LeadDetailResponse)
def get_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admissions_staff)
):
    """Get a single lead by ID with full details."""
    lead = db.query(Lead).options(
        joinedload(Lead.lead_source),
        joinedload(Lead.assigned_to),
        joinedload(Lead.program_interest)
    ).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Build response with relationship data
    response = LeadDetailResponse.model_validate(lead)
    if lead.assigned_to:
        response.assigned_to_name = f"{lead.assigned_to.first_name} {lead.assigned_to.last_name}"
    if lead.program_interest:
        response.program_interest_name = lead.program_interest.name

    return response


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: UUID,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admissions_staff)
):
    """Update a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Validate foreign keys if provided
    if lead_data.lead_source_id:
        source = db.query(LeadSource).filter(LeadSource.id == lead_data.lead_source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Lead source not found")

    if lead_data.program_interest_id:
        program = db.query(Program).filter(Program.id == lead_data.program_interest_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")

    if lead_data.assigned_to_id:
        user = db.query(User).filter(User.id == lead_data.assigned_to_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Assigned user not found")

    # Update lead
    update_data = lead_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lead, key, value)

    db.commit()
    db.refresh(lead)

    # Create activity log
    activity = Activity(
        entity_type="lead",
        entity_id=lead.id,
        activity_type="note",
        subject="Lead Updated",
        description=f"Lead updated by {current_user.first_name} {current_user.last_name}",
        created_by_id=current_user.id
    )
    db.add(activity)
    db.commit()

    return lead


@router.delete("/{lead_id}", status_code=204)
def delete_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admissions_staff)
):
    """Delete a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()


# =============================================================================
# LEAD ACTIVITIES ENDPOINTS
# =============================================================================

@router.get("/{lead_id}/activities", response_model=List[ActivityDetailResponse])
def list_lead_activities(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admissions_staff)
):
    """List all activities for a lead."""
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    activities = db.query(Activity).options(
        joinedload(Activity.assigned_to),
        joinedload(Activity.created_by)
    ).filter(
        Activity.entity_type == "lead",
        Activity.entity_id == lead_id
    ).order_by(Activity.created_at.desc()).all()

    # Build response with relationship data
    result = []
    for activity in activities:
        response = ActivityDetailResponse.model_validate(activity)
        if activity.assigned_to:
            response.assigned_to_name = f"{activity.assigned_to.first_name} {activity.assigned_to.last_name}"
        if activity.created_by:
            response.created_by_name = f"{activity.created_by.first_name} {activity.created_by.last_name}"
        result.append(response)

    return result


@router.post("/{lead_id}/activities", response_model=ActivityResponse, status_code=201)
def create_lead_activity(
    lead_id: UUID,
    activity_data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admissions_staff)
):
    """Create a new activity for a lead."""
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Ensure entity_type and entity_id match the lead
    if activity_data.entity_type != "lead" or activity_data.entity_id != lead_id:
        raise HTTPException(status_code=400, detail="Activity must be for this lead")

    # Create activity
    activity = Activity(
        **activity_data.model_dump(),
        created_by_id=current_user.id
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: UUID,
    activity_data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admissions_staff)
):
    """Update an activity."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Update activity
    update_data = activity_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(activity, key, value)

    db.commit()
    db.refresh(activity)

    return activity
