"""
Audit log and compliance reporting endpoints.

HIPAA-compliant audit log access and reporting for administrators.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models.audit_log import AuditLog
from app.db.models.user import User
from app.core.rbac import require_admin

router = APIRouter(prefix="/api/audit", tags=["audit"])


# Schemas
class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str]
    user_email: Optional[str]
    method: str
    path: str
    status_code: int
    timestamp: datetime
    ip_address: Optional[str]
    is_phi_access: bool
    duration_ms: Optional[int]

    class Config:
        from_attributes = True


class ComplianceReportResponse(BaseModel):
    report_type: str
    start_date: datetime
    end_date: datetime
    total_requests: int
    phi_access_count: int
    unique_users: int
    failed_requests: int
    avg_response_time_ms: Optional[float]
    top_endpoints: List[dict]
    top_users: List[dict]


# Endpoints
@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user_id: Optional[str] = Query(None),
    is_phi_access: Optional[bool] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with filtering.

    Requires Admin role.
    """
    query = db.query(AuditLog)

    # Apply filters
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if is_phi_access is not None:
        query = query.filter(AuditLog.is_phi_access == is_phi_access)

    # Order by most recent first
    query = query.order_by(AuditLog.timestamp.desc())

    # Paginate
    logs = query.offset(offset).limit(limit).all()

    return logs


@router.get("/phi-access", response_model=List[AuditLogResponse])
def get_phi_access_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get PHI access logs specifically.

    Requires Admin role.
    """
    query = db.query(AuditLog).filter(AuditLog.is_phi_access == True)  # noqa: E712

    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

    return logs


@router.get("/compliance-report", response_model=ComplianceReportResponse)
def get_compliance_report(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Generate HIPAA compliance report.

    Shows audit log statistics for the specified time period.
    Requires Admin role.
    """
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # Total requests
    total_requests = db.query(AuditLog).filter(
        and_(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        )
    ).count()

    # PHI access count
    phi_access_count = db.query(AuditLog).filter(
        and_(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
            AuditLog.is_phi_access == True  # noqa: E712
        )
    ).count()

    # Unique users
    unique_users = db.query(func.count(func.distinct(AuditLog.user_id))).filter(
        and_(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
            AuditLog.user_id.isnot(None)
        )
    ).scalar()

    # Failed requests (4xx and 5xx)
    failed_requests = db.query(AuditLog).filter(
        and_(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
            AuditLog.status_code >= 400
        )
    ).count()

    # Average response time
    avg_response_time = db.query(func.avg(AuditLog.duration_ms)).filter(
        and_(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
            AuditLog.duration_ms.isnot(None)
        )
    ).scalar()

    # Top endpoints
    top_endpoints_query = db.query(
        AuditLog.path,
        func.count(AuditLog.id).label('count')
    ).filter(
        and_(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        )
    ).group_by(AuditLog.path).order_by(func.count(AuditLog.id).desc()).limit(10)

    top_endpoints = [
        {"endpoint": row.path, "count": row.count}
        for row in top_endpoints_query.all()
    ]

    # Top users
    top_users_query = db.query(
        AuditLog.user_email,
        func.count(AuditLog.id).label('count')
    ).filter(
        and_(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
            AuditLog.user_email.isnot(None)
        )
    ).group_by(AuditLog.user_email).order_by(func.count(AuditLog.id).desc()).limit(10)

    top_users = [
        {"user_email": row.user_email, "count": row.count}
        for row in top_users_query.all()
    ]

    return ComplianceReportResponse(
        report_type="compliance_audit",
        start_date=start_date,
        end_date=end_date,
        total_requests=total_requests,
        phi_access_count=phi_access_count,
        unique_users=unique_users or 0,
        failed_requests=failed_requests,
        avg_response_time_ms=float(avg_response_time) if avg_response_time else None,
        top_endpoints=top_endpoints,
        top_users=top_users
    )


@router.get("/user/{user_id}/activity", response_model=List[AuditLogResponse])
def get_user_activity(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all activity for a specific user.

    Requires Admin role.
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    logs = db.query(AuditLog).filter(
        and_(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= start_date
        )
    ).order_by(AuditLog.timestamp.desc()).limit(1000).all()

    return logs
