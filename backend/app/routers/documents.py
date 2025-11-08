"""
Document E-Signature API

Provides endpoints for managing enrollment agreements and other signed documents.
Implements legally compliant e-signature workflow with full audit trail.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List
import uuid
from datetime import datetime
import json

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.crm.lead import Lead
from app.db.models.document import (
    DocumentTemplate,
    SignedDocument,
    DocumentSignature,
    DocumentAuditLog
)
from app.services.token_service import TokenService
from app.routers.auth import get_current_user
from app.schemas.document import (
    DocumentTemplateResponse,
    SignedDocumentResponse,
    SignedDocumentListResponse,
    DocumentSignatureCreate,
    DocumentSignatureResponse,
    DocumentAuditLogListResponse,
)
from app.services.pdf_service import PDFSignatureService

router = APIRouter(prefix="/documents", tags=["documents"])

# File storage paths
DOCUMENTS_BASE = Path("app/static/documents")
TEMPLATES_DIR = DOCUMENTS_BASE / "templates"
UNSIGNED_DIR = DOCUMENTS_BASE / "unsigned"
SIGNED_DIR = DOCUMENTS_BASE / "signed"

# Ensure directories exist
for directory in [TEMPLATES_DIR, UNSIGNED_DIR, SIGNED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role"""
    # TODO: Implement proper role checking
    return current_user


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
    name: str,
    version: str,
    description: str = None,
    requires_counter_signature: bool = False,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Upload a new document template (enrollment agreement, etc.)"""

    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Generate unique filename
    template_id = uuid.uuid4()
    filename = f"{template_id}_{file.filename}"
    file_path = TEMPLATES_DIR / filename

    # Save file
    with open(file_path, 'wb') as f:
        content = await file.read()
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
        sent_at=datetime.utcnow()
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


@router.get("/user/{user_id}", response_model=SignedDocumentListResponse)
def get_user_documents(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all documents for a specific user"""

    # Users can only see their own documents unless they're admin
    # TODO: Add proper role check for admin
    if str(current_user.id) != str(user_id):
        raise HTTPException(status_code=403, detail="Access denied")

    documents = db.query(SignedDocument).filter(
        SignedDocument.user_id == user_id
    ).all()

    # Enrich with template information
    enriched_docs = []
    for doc in documents:
        template = db.query(DocumentTemplate).filter(
            DocumentTemplate.id == doc.template_id
        ).first()

        enriched_docs.append({
            **doc.__dict__,
            "template_name": template.name if template else "Unknown",
            "template_version": template.version if template else "Unknown",
            "requires_counter_signature": template.requires_counter_signature if template else False
        })

    return {
        "documents": enriched_docs,
        "total": len(enriched_docs)
    }


@router.get("/lead/{lead_id}", response_model=SignedDocumentListResponse)
def get_lead_documents(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all documents for a specific lead"""

    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    documents = db.query(SignedDocument).filter(
        SignedDocument.lead_id == lead_id
    ).all()

    # Enrich with template information
    enriched_docs = []
    for doc in documents:
        template = db.query(DocumentTemplate).filter(
            DocumentTemplate.id == doc.template_id
        ).first()

        enriched_docs.append({
            **doc.__dict__,
            "template_name": template.name if template else "Unknown",
            "template_version": template.version if template else "Unknown",
            "requires_counter_signature": template.requires_counter_signature if template else False
        })

    return {
        "documents": enriched_docs,
        "total": len(enriched_docs)
    }


@router.get("/", response_model=SignedDocumentListResponse)
def get_all_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all documents (admin only)"""

    documents = db.query(SignedDocument).all()

    # Enrich with template information
    enriched_docs = []
    for doc in documents:
        template = db.query(DocumentTemplate).filter(
            DocumentTemplate.id == doc.template_id
        ).first()

        enriched_docs.append({
            **doc.__dict__,
            "template_name": template.name if template else "Unknown",
            "template_version": template.version if template else "Unknown",
            "requires_counter_signature": template.requires_counter_signature if template else False
        })

    return {
        "documents": enriched_docs,
        "total": len(enriched_docs)
    }


@router.get("/{document_id}", response_model=SignedDocumentResponse)
def get_document(
    document_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document"""

    document = db.query(SignedDocument).filter(SignedDocument.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check access: user can see their own documents or admin can see all
    # TODO: Add proper role check for admin
    if str(document.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Log document viewed event (first time only)
    if not document.student_viewed_at:
        document.student_viewed_at = datetime.utcnow()
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
        document.student_signed_at = datetime.utcnow()
        document.status = "student_signed"
    elif signature_data.signature_type == "school_official":
        document.counter_signed_at = datetime.utcnow()
        document.status = "completed"
        document.completed_at = datetime.utcnow()

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
        # Gather all signatures
        all_signatures = db.query(DocumentSignature).filter(
            DocumentSignature.document_id == document_id
        ).all()

        # Prepare signature data for PDF overlay
        # Position signatures at bottom of page (adjust x,y coordinates as needed)
        signature_list = []
        x_position = 100
        y_position = 100

        for sig in all_signatures:
            signature_list.append((
                sig.signature_data,
                sig.signature_type,
                x_position,
                y_position
            ))
            x_position += 250  # Space signatures horizontally

        # Generate signed PDF
        template_path = Path(template.file_path)
        signed_filename = f"{document.id}_signed.pdf"
        signed_path = SIGNED_DIR / signed_filename

        metadata = {
            'title': template.name,
            'author': 'AADA LMS',
            'subject': template.name,
            'document_id': str(document.id),
            'signed_date': datetime.utcnow().isoformat()
        }

        success = PDFSignatureService.overlay_signatures(
            template_pdf_path=template_path,
            output_pdf_path=signed_path,
            signatures=signature_list,
            metadata=metadata
        )

        if success:
            document.signed_file_path = str(signed_path.relative_to(Path("app")))
            document.status = "completed"
            document.completed_at = datetime.utcnow()
            db.commit()

            # Log PDF generation
            log_document_event(
                db=db,
                document_id=document_id,
                event_type="pdf_generated",
                user_id=current_user.id,
                event_details=json.dumps({"signed_file_path": document.signed_file_path}),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )

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

    # Check access
    # TODO: Add proper role check for admin
    if str(document.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Get template for unsigned version
    template = db.query(DocumentTemplate).filter(
        DocumentTemplate.id == document.template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Return signed version if exists, otherwise template
    if document.signed_file_path and Path(document.signed_file_path).exists():
        file_path = Path(document.signed_file_path)
    else:
        file_path = Path(template.file_path)

    if not file_path.exists():
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
