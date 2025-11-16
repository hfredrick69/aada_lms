"""
Document E-Signature API

Provides endpoints for managing enrollment agreements and other signed documents.
Implements legally compliant e-signature workflow with full audit trail.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import contextlib
import uuid
from datetime import datetime, timezone, timedelta
import json
import shutil
import logging

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.crm.lead import Lead, LeadSource
from app.db.models.document import (
    DocumentTemplate,
    SignedDocument,
    DocumentSignature,
    DocumentAuditLog
)
from app.services.token_service import TokenService
from app.services.email import (
    send_enrollment_agreement_email,
    send_completed_agreement_email,
    EmailDeliveryError,
)
from app.services.sms import send_enrollment_agreement_sms
from app.routers.auth import get_current_user
from app.schemas.document import (
    DocumentTemplateResponse,
    SignedDocumentResponse,
    SignedDocumentListResponse,
    DocumentSignatureCreate,
    DocumentSignatureResponse,
    DocumentAuditLogListResponse,
    EnrollmentAgreementRequest,
    CounterSignRequest,
)
from app.services.pdf_service import PDFSignatureService
from app.services.enrollment_pdf import SchemaDrivenPDFService
from app.core.file_validation import validate_pdf, validate_file
from app.utils.encryption import decrypt_value
from app.core.rbac import require_admin, require_roles
from app.core.config import settings
from app.domain.enrollment.schema import get_enrollment_agreement_schema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

# File storage paths
DOCUMENTS_BASE = Path("app/static/documents")
TEMPLATES_DIR = DOCUMENTS_BASE / "templates"
UNSIGNED_DIR = DOCUMENTS_BASE / "unsigned"
SIGNED_DIR = DOCUMENTS_BASE / "signed"

# Ensure directories exist
for directory in [TEMPLATES_DIR, UNSIGNED_DIR, SIGNED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

ENROLLMENT_COURSES = {
    "twenty_week": "20-Week Course",
    "expanded_functions": "Expanded Functions Course",
}
ENROLLMENT_RETENTION_YEARS = 5
admin_or_registrar = require_roles(["admin", "registrar"])
STAFF_ROLES = {"admin", "staff", "registrar", "instructor", "finance"}
AD_HOC_LEAD_SOURCE = "Digital Enrollment"
ACKNOWLEDGEMENT_POSITIONS = [
    ("initial_agreement_catalog", (420, 530)),
    ("initial_school_outcomes", (420, 485)),
    ("initial_employment", (420, 440)),
    ("initial_refund_policy", (420, 395)),
    ("initial_complaint_procedure", (420, 350)),
    ("initial_authorization", (420, 305)),
]


def _has_staff_access(current_user: User) -> bool:
    """Check if current user belongs to any staff role."""
    roles = getattr(current_user, "roles", []) or []
    for role in roles:
        role_name = role.name if hasattr(role, "name") else role
        if role_name in STAFF_ROLES:
            return True
    return False


def _normalize_template_path(template_path: str) -> Path:
    """Resolve a template file path relative to the documents directory."""
    candidate = Path(template_path)
    if candidate.is_absolute():
        return candidate
    return DOCUMENTS_BASE.parent / candidate


def _resolve_document_file(path_value: Optional[str]) -> Optional[Path]:
    """
    Securely resolve stored document/template paths to absolute filesystem paths.

    Security: Prevents path traversal attacks by validating paths stay within allowed directories.

    Args:
        path_value: Relative path to document file

    Returns:
        Absolute Path to file if valid and exists, None if path_value is None

    Raises:
        HTTPException: 400 for invalid paths, 403 for unauthorized access, 404 if not found
    """
    if not path_value:
        return None

    # Security: Block path traversal attempts
    if ".." in path_value or path_value.startswith("/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file path"
        )

    candidate = Path(path_value)

    # Security: Block absolute paths from user input
    if candidate.is_absolute():
        raise HTTPException(
            status_code=400,
            detail="Absolute paths not allowed"
        )

    # Define allowed base directory (app/static)
    allowed_base = DOCUMENTS_BASE.parent.resolve()

    # Resolve path relative to allowed base
    resolved = (allowed_base / candidate).resolve()

    # Security: Verify resolved path is within allowed directory
    try:
        resolved.relative_to(allowed_base)
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    # Check if file exists
    if not resolved.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return resolved


def _copy_template_to_unsigned(document_id: uuid.UUID, template_path: str) -> str:
    """Copy the template PDF into the unsigned directory for tracking."""
    source = _normalize_template_path(template_path)
    if not source.exists():
        return template_path

    filename = f"{document_id}_unsigned{source.suffix or '.pdf'}"
    destination = UNSIGNED_DIR / filename
    shutil.copyfile(source, destination)
    return str(destination.relative_to(DOCUMENTS_BASE.parent))


def _generate_signed_pdf(
    document: SignedDocument,
    template: DocumentTemplate,
    db: Session,
    current_user: Optional[User],
    request: Optional[Request]
) -> bool:
    """Generate/refresh the final signed PDF with all collected signatures."""
    template_path = _resolve_document_file(template.file_path)

    all_signatures = (
        db.query(DocumentSignature)
        .filter(DocumentSignature.document_id == document.id)
        .order_by(DocumentSignature.signed_at.asc())
        .all()
    )

    if not all_signatures:
        return False

    form_data = document.form_data if isinstance(document.form_data, dict) else {}
    signed_filename = f"{document.id}_signed.pdf"
    signed_path = SIGNED_DIR / signed_filename

    schema = None
    schema_loaded = False
    try:
        schema = get_enrollment_agreement_schema()
        schema_loaded = True
    except Exception:  # pragma: no cover - schema file missing or invalid
        schema_loaded = False

    use_schema_pdf = schema_loaded and template.name.lower().startswith("enrollment agreement")
    if use_schema_pdf:
        schema_service = SchemaDrivenPDFService(schema)
        success = schema_service.generate_pdf(
            output_pdf_path=signed_path,
            document=document,
            form_data=form_data,
            signatures=all_signatures,
        )
    else:
        if not template_path or not template_path.exists():
            return False

        # Arrange signatures in two columns to avoid overlap
        signature_list: List[Tuple[str, str, int, int]] = []
        base_x = 80
        base_y = 120
        column_width = 250
        row_height = 90
        signatures_per_row = 2

        for index, sig in enumerate(all_signatures):
            row = index // signatures_per_row
            column = index % signatures_per_row
            x_pos = base_x + column * column_width
            y_pos = base_y + row * row_height
            signature_list.append((sig.signature_data, sig.signature_type, x_pos, y_pos))

        acknowledgements = []
        ack_values = form_data.get("acknowledgements") if isinstance(form_data, dict) else None
        if isinstance(ack_values, dict):
            for key, (ack_x, ack_y) in ACKNOWLEDGEMENT_POSITIONS:
                value = ack_values.get(key)
                if isinstance(value, str) and value.strip():
                    initials = value.strip().upper()[:4]
                    acknowledgements.append((initials, ack_x, ack_y))

        metadata = {
            "title": template.name,
            "author": "AADA LMS",
            "subject": template.name,
            "document_id": str(document.id),
            "signed_date": datetime.now(timezone.utc).isoformat(),
        }

        success = PDFSignatureService.overlay_signatures(
            template_pdf_path=template_path,
            output_pdf_path=signed_path,
            signatures=signature_list,
            metadata=metadata,
            acknowledgements=acknowledgements,
        )

    if not success:
        return False

    document.signed_file_path = str(signed_path.relative_to(Path("app")))
    if document.status == "completed" and not document.completed_at:
        document.completed_at = datetime.now(timezone.utc)
    db.commit()

    log_document_event(
        db=db,
        document_id=document.id,
        event_type="pdf_generated",
        user_id=getattr(current_user, "id", None),
        event_details=json.dumps({"signed_file_path": document.signed_file_path}),
        ip_address=request.client.host if (request and request.client) else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )

    return True


def _serialize_document(doc: SignedDocument, template: Optional[DocumentTemplate]) -> dict:
    """Prepare document payload enriched with template metadata."""
    return {
        "id": doc.id,
        "template_id": doc.template_id,
        "user_id": doc.user_id,
        "lead_id": doc.lead_id,
        "signer_name": doc.signer_name,
        "signer_email": doc.signer_email,
        "signing_token": doc.signing_token,
        "token_expires_at": doc.token_expires_at,
        "status": doc.status,
        "unsigned_file_path": doc.unsigned_file_path,
        "signed_file_path": doc.signed_file_path,
        "created_at": doc.created_at,
        "sent_at": doc.sent_at,
        "student_viewed_at": doc.student_viewed_at,
        "student_signed_at": doc.student_signed_at,
        "counter_signed_at": doc.counter_signed_at,
        "completed_at": doc.completed_at,
        "course_type": doc.course_type,
        "form_data": doc.form_data,
        "retention_expires_at": doc.retention_expires_at,
        "template_name": template.name if template else "Unknown",
        "template_version": template.version if template else "Unknown",
        "requires_counter_signature": template.requires_counter_signature if template else False,
    }


def _resolve_enrollment_template(db: Session, template_id: Optional[uuid.UUID]) -> DocumentTemplate:
    """Locate the template that should be used for enrollment agreements."""
    query = db.query(DocumentTemplate).filter(DocumentTemplate.is_active.is_(True))
    template: Optional[DocumentTemplate] = None

    if template_id:
        template = query.filter(DocumentTemplate.id == template_id).first()
    else:
        template = (
            query.filter(DocumentTemplate.name == "Enrollment Agreement")
            .order_by(DocumentTemplate.updated_at.desc())
            .first()
        )

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Enrollment agreement template not found. Upload a template before sending agreements.",
        )
    return template


def _derive_signer_fields(
    db: Session,
    user: User,
    provided_name: Optional[str],
    provided_email: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    """Determine signer display name and email, falling back to decrypted PHI."""
    decrypted_first = decrypt_value(db, user.first_name) if user.first_name else None
    decrypted_last = decrypt_value(db, user.last_name) if user.last_name else None
    decrypted_email = _normalize_email(_safe_decrypt_email(db, user.email))
    provided_email = _normalize_email(provided_email)

    default_name = " ".join(
        part for part in [decrypted_first, decrypted_last] if part
    ) or None

    return provided_name or default_name, provided_email or decrypted_email


def log_document_event(
    db: Session,
    document_id: uuid.UUID,
    event_type: str,
    user_id: uuid.UUID = None,
    event_details: str = None,
    ip_address: str = None,
    user_agent: str = None
):
    """Create audit log entry"""
    audit_log = DocumentAuditLog(
        document_id=document_id,
        user_id=user_id,
        event_type=event_type,
        event_details=event_details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()


# ==================== Document Template Management ====================

@router.post("/templates", response_model=DocumentTemplateResponse)
async def create_document_template(
    name: str = Form(...),
    version: str = Form(...),
    description: str = Form(None),
    requires_counter_signature: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Upload a new document template (enrollment agreement, etc.)"""

    # Check for duplicate template (same name and version)
    existing = db.query(DocumentTemplate).filter(
        DocumentTemplate.name == name,
        DocumentTemplate.version == version
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Template '{name}' version {version} already exists"
        )

    # Read file content
    content = await file.read()

    # Comprehensive PDF validation (extension, size, magic bytes, structure)
    validate_pdf(content, file.filename, max_size_mb=10)

    # Generate unique filename
    template_id = uuid.uuid4()
    filename = f"{template_id}_{file.filename}"
    file_path = TEMPLATES_DIR / filename

    # Save file
    with open(file_path, 'wb') as f:
        f.write(content)

    # Create database record
    template = DocumentTemplate(
        id=template_id,
        name=name,
        description=description,
        version=version,
        file_path=str(file_path.relative_to(DOCUMENTS_BASE.parent)),
        requires_counter_signature=requires_counter_signature,
        is_active=True
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return template


@router.post("/enrollment/send", response_model=SignedDocumentResponse)
def send_enrollment_agreement(
    payload: EnrollmentAgreementRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_registrar),
):
    """Create a course-specific enrollment agreement for a student."""
    template = _resolve_enrollment_template(db, payload.template_id)

    recipient_user: Optional[User] = None
    recipient_lead: Optional[Lead] = None

    if payload.user_id:
        recipient_user = db.query(User).filter(User.id == payload.user_id).first()
        if not recipient_user:
            raise HTTPException(status_code=404, detail="Student not found")
    elif payload.lead_id:
        recipient_lead = db.query(Lead).filter(Lead.id == payload.lead_id).first()
        if not recipient_lead:
            raise HTTPException(status_code=404, detail="Lead not found")
    elif payload.signer_email:
        recipient_lead = _create_ad_hoc_lead(db, payload.signer_name, payload.signer_email)
    else:
        raise HTTPException(status_code=400, detail="Recipient is required")

    if payload.course_type not in ENROLLMENT_COURSES:
        raise HTTPException(status_code=400, detail="Unsupported course type")

    if recipient_user:
        signer_name, signer_email = _derive_signer_fields(
            db,
            recipient_user,
            payload.signer_name,
            payload.signer_email,
        )
    elif recipient_lead:
        default_name = " ".join(
            part
            for part in [
                getattr(recipient_lead, "first_name", None),
                getattr(recipient_lead, "last_name", None),
            ]
            if part
        ).strip()
        signer_name = payload.signer_name or default_name or recipient_lead.email
        signer_email = payload.signer_email or recipient_lead.email

        if not signer_email:
            raise HTTPException(status_code=400, detail="Lead email is required to send agreements.")
    else:
        signer_email = payload.signer_email
        if not signer_email:
            raise HTTPException(status_code=400, detail="Signer email is required to send agreements.")
        signer_name = payload.signer_name or signer_email

    signing_token = TokenService.generate_signing_token(48)
    token_expires_at = datetime.now(timezone.utc) + timedelta(days=14)
    retention_expires_at = datetime.now(timezone.utc) + timedelta(
        days=ENROLLMENT_RETENTION_YEARS * 365
    )

    form_payload = dict(payload.form_data or {})
    form_payload.setdefault("course_label", ENROLLMENT_COURSES[payload.course_type])

    student_defaults: Dict[str, Optional[str]] = {}

    if recipient_user:
        decrypted_first = decrypt_value(db, recipient_user.first_name) if recipient_user.first_name else None
        decrypted_last = decrypt_value(db, recipient_user.last_name) if recipient_user.last_name else None
        decrypted_email = _normalize_email(_safe_decrypt_email(db, recipient_user.email))
        student_defaults.update(
            {
                "first_name": decrypted_first,
                "last_name": decrypted_last,
                "email": decrypted_email,
            }
        )
    elif recipient_lead:
        student_defaults.update(
            {
                "first_name": getattr(recipient_lead, "first_name", None),
                "last_name": getattr(recipient_lead, "last_name", None),
                "email": getattr(recipient_lead, "email", None),
                "phone": getattr(recipient_lead, "phone", None),
                "street_address": getattr(recipient_lead, "address_line1", None),
                "city": getattr(recipient_lead, "city", None),
                "state": getattr(recipient_lead, "state", None),
                "postal_code": getattr(recipient_lead, "zip_code", None),
            }
        )

    if signer_name and not student_defaults.get("first_name"):
        parts = signer_name.split(" ", 1)
        student_defaults["first_name"] = parts[0]
        if len(parts) > 1:
            student_defaults.setdefault("last_name", parts[1])
    if signer_email:
        student_defaults.setdefault("email", signer_email)

    _apply_student_defaults(form_payload, student_defaults)

    document = SignedDocument(
        template_id=template.id,
        user_id=recipient_user.id if recipient_user else None,
        lead_id=recipient_lead.id if recipient_lead else None,
        signer_name=signer_name,
        signer_email=signer_email,
        signing_token=signing_token,
        token_expires_at=token_expires_at,
        status="pending",
        unsigned_file_path=template.file_path,
        course_type=payload.course_type,
        form_data=form_payload,
        retention_expires_at=retention_expires_at,
        sent_at=datetime.now(timezone.utc),
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Copy template into unsigned directory for auditing
    document.unsigned_file_path = _copy_template_to_unsigned(document.id, template.file_path)
    db.commit()
    db.refresh(document)

    log_document_event(
        db=db,
        document_id=document.id,
        event_type="enrollment_sent",
        user_id=current_user.id,
        event_details=json.dumps(
            {
                "course_type": payload.course_type,
                "course_label": ENROLLMENT_COURSES[payload.course_type],
                "recipient_type": "student" if recipient_user else ("lead" if recipient_lead else "ad_hoc"),
            }
        ),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    signing_url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/sign/{signing_token}"
    course_label = form_payload.get("course_label", ENROLLMENT_COURSES[payload.course_type])
    try:
        send_enrollment_agreement_email(
            to_email=signer_email,
            signer_name=signer_name or "",
            course_label=course_label,
            signing_url=signing_url,
            token_expires_at=token_expires_at,
        )
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to send enrollment email: {exc}") from exc

    # Also send SMS if phone number is available (non-blocking)
    signer_phone = student_defaults.get("phone") or form_payload.get("phone")
    if signer_phone:
        try:
            send_enrollment_agreement_sms(
                to_phone=signer_phone,
                signer_name=signer_name or "",
                course_label=course_label,
                signing_url=signing_url,
            )
        except Exception as sms_exc:
            # Log SMS failure but don't fail the request - email was sent successfully
            logger.warning(f"SMS notification failed for enrollment agreement {document.id}: {sms_exc}")

    return document


@router.get("/templates", response_model=List[DocumentTemplateResponse])
def list_document_templates(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all document templates"""
    query = db.query(DocumentTemplate)

    if active_only:
        query = query.filter(DocumentTemplate.is_active.is_(True))

    return query.all()


@router.get("/templates/{template_id}", response_model=DocumentTemplateResponse)
def get_document_template(
    template_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get a specific document template"""
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.patch("/templates/{template_id}/toggle-active")
def toggle_template_active(
    template_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Toggle template active status (soft delete/restore)"""
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.is_active = not template.is_active
    db.commit()
    db.refresh(template)

    return {
        "id": template.id,
        "name": template.name,
        "version": template.version,
        "is_active": template.is_active
    }


@router.delete("/templates/{template_id}")
def delete_template(
    template_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Permanently delete a template (hard delete)"""
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check if template has been used in any documents
    document_count = db.query(SignedDocument).filter(
        SignedDocument.template_id == template_id
    ).count()

    if document_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete template: {document_count} document(s) use this template. Mark as inactive instead."
        )

    # Delete file
    if template.file_path:
        file_path = Path(template.file_path)
        if file_path.exists():
            file_path.unlink()

    db.delete(template)
    db.commit()

    return {"message": "Template deleted successfully"}


# ==================== Student Document Uploads ====================

@router.post("/upload")
async def upload_student_document(
    document_type: str = Form(...),  # e.g., "identification", "transcript", "certification"
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload student documents (ID, transcripts, certifications, etc.)

    Supports: PDF, PNG, JPG/JPEG
    Max size: 10MB
    Security: Full validation (extension, magic bytes, structure)
    """
    # Read file content
    content = await file.read()

    # Validate file type and structure
    file_type = validate_file(
        content,
        file.filename,
        allowed_types={'.pdf', '.png', '.jpg', '.jpeg'},
        max_size_mb=10
    )

    # Create student documents directory if needed
    STUDENT_DOCS_DIR = DOCUMENTS_BASE / "student_uploads" / str(current_user.id)
    STUDENT_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    doc_id = uuid.uuid4()
    ext = Path(file.filename).suffix.lower()
    filename = f"{doc_id}_{document_type}{ext}"
    file_path = STUDENT_DOCS_DIR / filename

    # Save file
    with open(file_path, 'wb') as f:
        f.write(content)

    # TODO: Store metadata in database (create StudentDocument model)
    # For now, return success with file info

    return {
        "id": str(doc_id),
        "document_type": document_type,
        "filename": file.filename,
        "file_type": file_type,
        "file_path": str(file_path.relative_to(Path("app/static"))),
        "size_bytes": len(content),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "uploaded_by": current_user.id
    }


# ==================== Document Instance Management ====================

@router.post("/send", response_model=SignedDocumentResponse)
def send_document(
    template_id: uuid.UUID,
    user_id: uuid.UUID = None,
    lead_id: uuid.UUID = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Send a document to a user or lead for signing

    Security:
        - For leads: generates secure token for public signing
        - For users: uses authenticated signing flow
        - XOR validation: must provide either user_id OR lead_id (not both)
    """

    # Validate XOR: either user_id or lead_id, not both
    if not user_id and not lead_id:
        raise HTTPException(status_code=400, detail="Either user_id or lead_id must be provided")

    if user_id and lead_id:
        raise HTTPException(status_code=400, detail="Cannot provide both user_id and lead_id")

    # Validate template exists
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Initialize document fields
    signer_name = None
    signer_email = None
    signing_token = None
    token_expires_at = None
    event_details = {"template_id": str(template_id)}

    # Handle user-based document
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        event_details["recipient_user_id"] = str(user_id)

    # Handle lead-based document (token-based signing)
    else:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Generate secure signing token
        signing_token = TokenService.generate_signing_token()
        token_expires_at = TokenService.calculate_token_expiration(days=30)

        # Store signer info from lead
        signer_name = f"{lead.first_name} {lead.last_name}"
        signer_email = lead.email

        event_details["recipient_lead_id"] = str(lead_id)
        event_details["signing_token_expires_at"] = token_expires_at.isoformat()

    # Create signed document instance
    document = SignedDocument(
        template_id=template_id,
        user_id=user_id,
        lead_id=lead_id,
        signer_name=signer_name,
        signer_email=signer_email,
        signing_token=signing_token,
        token_expires_at=token_expires_at,
        status="pending",
        sent_at=datetime.now(timezone.utc)
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Log event
    log_document_event(
        db=db,
        document_id=document.id,
        event_type="document_sent",
        user_id=current_user.id,
        event_details=json.dumps(event_details),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    db.commit()
    db.refresh(document)

    return document


@router.post("/{document_id}/counter-sign", response_model=SignedDocumentResponse)
def counter_sign_document(
    document_id: uuid.UUID,
    payload: CounterSignRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_registrar),
):
    """Apply the AADA counter-signature to a signed document."""
    document = db.query(SignedDocument).filter(SignedDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status not in {"student_signed", "pending"}:
        raise HTTPException(
            status_code=400,
            detail="Document cannot be counter-signed in its current state",
        )

    signature = DocumentSignature(
        document_id=document.id,
        signer_id=current_user.id,
        signature_type="school_official",
        signature_data=payload.signature_data,
        signed_at=datetime.now(timezone.utc),
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent") or "unknown",
        typed_name=payload.typed_name,
        signer_email=_normalize_email(_safe_decrypt_email(db, current_user.email)),
    )
    db.add(signature)

    document.counter_signed_at = signature.signed_at
    document.completed_at = signature.signed_at
    document.status = "completed"
    document.signing_token = None
    document.token_expires_at = None

    db.commit()
    db.refresh(document)

    log_document_event(
        db=db,
        document_id=document.id,
        event_type="document_counter_signed",
        user_id=current_user.id,
        event_details=json.dumps({"typed_name": payload.typed_name}),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == document.template_id).first()
    generated_pdf = False
    if template:
        generated_pdf = _generate_signed_pdf(document, template, db, current_user, request)
        if generated_pdf:
            db.refresh(document)

    if not generated_pdf and not document.signed_file_path:
        # Fallback to the unsigned file so downloads still succeed.
        document.signed_file_path = document.unsigned_file_path
        db.commit()
        db.refresh(document)

    # Send the completed agreement PDF to the original signer
    if document.signed_file_path and document.signer_email:
        try:
            pdf_path = Path(document.signed_file_path)
            if pdf_path.exists():
                pdf_content = pdf_path.read_bytes()
                course_label = template.title if template else "Dental Assisting"

                # Get signer name from the first signature (student/lead signature)
                first_sig = (
                    db.query(DocumentSignature)
                    .filter(
                        DocumentSignature.document_id == document.id,
                        DocumentSignature.signature_type != "school_official"
                    )
                    .order_by(DocumentSignature.signed_at.asc())
                    .first()
                )
                signer_name = first_sig.typed_name if first_sig else "Student"

                send_completed_agreement_email(
                    to_email=document.signer_email,
                    signer_name=signer_name,
                    course_label=course_label,
                    pdf_content=pdf_content,
                    pdf_filename=f"AADA_Enrollment_Agreement_{document.id}.pdf"
                )
                logger.info(
                    f"Sent completed agreement email to {document.signer_email} "
                    f"for document {document.id}"
                )
        except EmailDeliveryError as e:
            logger.error(f"Failed to send completed agreement email: {e}")
            # Don't fail the counter-signature, just log the error
        except Exception as e:
            logger.error(f"Unexpected error sending completed agreement email: {e}")

    return document


@router.get("/user/{user_id}", response_model=SignedDocumentListResponse)
def get_user_documents(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all documents for a specific user"""

    if str(current_user.id) != str(user_id) and not _has_staff_access(current_user):
        raise HTTPException(status_code=403, detail="Access denied")

    documents = (
        db.query(SignedDocument)
        .filter(SignedDocument.user_id == user_id)
        .order_by(SignedDocument.created_at.desc())
        .all()
    )

    enriched_docs = [
        _serialize_document(
            doc,
            db.query(DocumentTemplate).filter(DocumentTemplate.id == doc.template_id).first(),
        )
        for doc in documents
    ]

    return {"documents": enriched_docs, "total": len(enriched_docs)}


@router.get("/lead/{lead_id}", response_model=SignedDocumentListResponse)
def get_lead_documents(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all documents for a specific lead"""

    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    documents = (
        db.query(SignedDocument)
        .filter(SignedDocument.lead_id == lead_id)
        .order_by(SignedDocument.created_at.desc())
        .all()
    )

    enriched_docs = [
        _serialize_document(
            doc,
            db.query(DocumentTemplate).filter(DocumentTemplate.id == doc.template_id).first(),
        )
        for doc in documents
    ]

    return {"documents": enriched_docs, "total": len(enriched_docs)}


@router.get("/", response_model=SignedDocumentListResponse)
def get_all_documents(
    course_type: Optional[str] = Query(None, description="Filter by course type slug"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by document status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_registrar),
):
    """Get all documents (admin/registrar access)."""

    query = db.query(SignedDocument)
    if course_type:
        query = query.filter(SignedDocument.course_type == course_type)
    if status_filter:
        query = query.filter(SignedDocument.status == status_filter)

    documents = query.order_by(SignedDocument.created_at.desc()).all()
    enriched_docs = [
        _serialize_document(
            doc,
            db.query(DocumentTemplate).filter(DocumentTemplate.id == doc.template_id).first(),
        )
        for doc in documents
    ]

    return {"documents": enriched_docs, "total": len(enriched_docs)}


@router.get("/{document_id}", response_model=SignedDocumentResponse)
def get_document(
    document_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific document"""

    document = db.query(SignedDocument).filter(SignedDocument.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check access: user can see their own documents or admin can see all
    if str(document.user_id) != str(current_user.id) and not _has_staff_access(current_user):
        raise HTTPException(status_code=403, detail="Access denied")

    # Log document viewed event (first time only)
    if not document.student_viewed_at:
        document.student_viewed_at = datetime.now(timezone.utc)
        db.commit()

        log_document_event(
            db=db,
            document_id=document.id,
            event_type="document_viewed",
            user_id=current_user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

    return document


# ==================== Signature Management ====================

@router.post("/{document_id}/sign", response_model=DocumentSignatureResponse)
async def sign_document(
    document_id: uuid.UUID,
    signature_data: DocumentSignatureCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sign a document"""

    document = db.query(SignedDocument).filter(SignedDocument.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate access based on signature type
    if signature_data.signature_type == "student":
        if str(document.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Only the assigned student can sign")

        if document.status not in ["pending", "viewed"]:
            raise HTTPException(status_code=400, detail="Document already signed")

    elif signature_data.signature_type == "school_official":
        # TODO: Add proper admin role check
        if document.status != "student_signed":
            raise HTTPException(status_code=400, detail="Student must sign first")

    else:
        raise HTTPException(status_code=400, detail="Invalid signature type")

    # Create signature record
    signature = DocumentSignature(
        document_id=document_id,
        signer_id=current_user.id,
        signature_type=signature_data.signature_type,
        signature_data=signature_data.signature_data,
        typed_name=signature_data.typed_name,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown")
    )

    db.add(signature)

    # Update document status
    if signature_data.signature_type == "student":
        document.student_signed_at = datetime.now(timezone.utc)
        document.status = "student_signed"
    elif signature_data.signature_type == "school_official":
        document.counter_signed_at = datetime.now(timezone.utc)
        document.status = "completed"
        document.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(signature)

    # Log signature event
    log_document_event(
        db=db,
        document_id=document_id,
        event_type=f"signature_{signature_data.signature_type}",
        user_id=current_user.id,
        event_details=json.dumps({"typed_name": signature_data.typed_name}),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    # Generate signed PDF if document is completed
    template = db.query(DocumentTemplate).filter(
        DocumentTemplate.id == document.template_id
    ).first()

    is_completed = False
    if template and not template.requires_counter_signature and document.status == "student_signed":
        is_completed = True
    elif template and template.requires_counter_signature and document.status == "completed":
        is_completed = True

    if is_completed and template:
        if document.status != "completed":
            document.status = "completed"
            document.completed_at = document.completed_at or datetime.now(timezone.utc)
            db.commit()
        _generate_signed_pdf(document, template, db, current_user, request)

    return signature


# ==================== Document Download ====================

@router.get("/{document_id}/download")
async def download_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a document (template or signed version)"""

    document = db.query(SignedDocument).filter(SignedDocument.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Allow the student who owns the document or any staff role to download
    if str(document.user_id) != str(current_user.id) and not _has_staff_access(current_user):
        raise HTTPException(status_code=403, detail="Access denied")

    # Get template for unsigned version
    template = db.query(DocumentTemplate).filter(
        DocumentTemplate.id == document.template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    signed_path = _resolve_document_file(document.signed_file_path)
    template_path = _resolve_document_file(template.file_path)

    # Return signed version if exists, otherwise template
    file_path = signed_path if signed_path and signed_path.exists() else template_path

    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file not found")

    return FileResponse(
        path=file_path,
        filename=f"{template.name}_v{template.version}.pdf",
        media_type="application/pdf"
    )


# ==================== Audit Trail ====================

@router.get("/{document_id}/audit-trail", response_model=DocumentAuditLogListResponse)
def get_document_audit_trail(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get complete audit trail for a document"""

    logs = db.query(DocumentAuditLog).filter(
        DocumentAuditLog.document_id == document_id
    ).order_by(DocumentAuditLog.occurred_at).all()

    return {
        "logs": logs,
        "total": len(logs)
    }


def _get_or_create_ad_hoc_lead_source(db: Session) -> LeadSource:
    """Ensure there is a lead source to attribute auto-created prospects."""
    source = (
        db.query(LeadSource)
        .filter(LeadSource.name == AD_HOC_LEAD_SOURCE)
        .first()
    )
    if source:
        return source

    source = LeadSource(
        name=AD_HOC_LEAD_SOURCE,
        description="Auto-created for enrollment agreements sent to ad-hoc contacts.",
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def _create_ad_hoc_lead(db: Session, signer_name: Optional[str], signer_email: str) -> Lead:
    """Create a lightweight lead so ad-hoc agreements comply with FK constraints."""
    display_name = signer_name or signer_email
    parts = display_name.strip().split(" ", 1)
    first_name = parts[0] if parts and parts[0] else signer_email.split("@")[0]
    last_name = parts[1] if len(parts) > 1 else "Prospect"
    source = _get_or_create_ad_hoc_lead_source(db)

    lead = Lead(
        first_name=first_name[:100],
        last_name=last_name[:100],
        email=signer_email,
        lead_source_id=source.id,
        lead_status="new",
        notes="Generated automatically for enrollment agreement delivery.",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def _merge_form_data(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge nested form payloads."""
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _merge_form_data(base.get(key, {}), value)
        else:
            base[key] = value
    return base


def _safe_decrypt_email(db: Session, encrypted_value: Optional[str]) -> Optional[str]:
    """Best-effort decrypt helper that falls back to the original value."""
    if not encrypted_value:
        return None
    try:
        return decrypt_value(db, encrypted_value)
    except Exception:
        with contextlib.suppress(Exception):
            db.rollback()
        return encrypted_value


def _normalize_email(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    return value if "@" in value else None


def _apply_student_defaults(form_payload: Dict[str, Any], defaults: Dict[str, Optional[str]]) -> None:
    """Merge default student data without overwriting what was already provided."""
    if not defaults:
        return
    student_section = form_payload.get("student") or {}
    updated = False
    for key, value in defaults.items():
        if value and not student_section.get(key):
            student_section[key] = value
            updated = True
    if updated:
        form_payload["student"] = student_section
