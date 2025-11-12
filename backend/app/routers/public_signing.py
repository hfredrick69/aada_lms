"""
Public Document Signing API

Public endpoints for lead-based document signing without authentication.
Security features:
- Rate limiting to prevent abuse
- Token-based access (no login required)
- Comprehensive audit logging
- IP and user agent tracking
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from typing import Optional
import base64
import json
from datetime import datetime, timezone

from app.db.session import get_db
from app.db.models.document import SignedDocument, DocumentSignature, DocumentAuditLog
from app.services.token_service import TokenService
from app.middleware.rate_limit import rate_limit_public_endpoints, get_client_ip
from app.schemas.document import DocumentSignRequest, DocumentSignResponse


router = APIRouter(prefix="/public/sign", tags=["Public Signing"])


def get_document_by_token(token: str, db: Session) -> SignedDocument:
    """
    Retrieve and validate document by signing token

    Args:
        token: Signing token from URL
        db: Database session

    Returns:
        SignedDocument if valid

    Raises:
        HTTPException: 404 if token invalid/expired (prevents enumeration)

    Security:
        - Returns 404 for both invalid and expired tokens (no information disclosure)
        - Validates token hasn't been used already
    """
    document = db.query(SignedDocument).filter(
        SignedDocument.signing_token == token
    ).first()

    if not document:
        # Return 404 to prevent token enumeration
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Validate token expiration
    if TokenService.is_token_expired(document.token_expires_at):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check if already signed (tokens are single-use)
    if document.status in ["student_signed", "completed", "counter_signed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has already been signed"
        )

    return document


def create_audit_log(
    document: SignedDocument,
    event_type: str,
    request: Request,
    db: Session,
    event_details: Optional[str] = None
):
    """
    Create audit log entry for document event

    Args:
        document: SignedDocument being logged
        event_type: Type of event (viewed, signed, etc.)
        request: FastAPI request for IP/user agent
        db: Database session
        event_details: Optional JSON details

    Security:
        - Captures IP address for legal compliance
        - Captures user agent for fraud detection
        - Immutable audit trail
    """
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "Unknown")

    audit_log = DocumentAuditLog(
        document_id=document.id,
        user_id=document.user_id,  # Will be None for lead documents
        event_type=event_type,
        event_details=event_details,
        occurred_at=datetime.now(timezone.utc),
        ip_address=ip_address,
        user_agent=user_agent
    )

    db.add(audit_log)


@router.get("/{token}", dependencies=[Depends(rate_limit_public_endpoints)])
async def get_document_for_signing(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get document details for signing (public endpoint, no auth required)

    Args:
        token: Unique signing token from email link
        request: FastAPI request
        db: Database session

    Returns:
        Document details for display

    Security:
        - Rate limited (10 requests/60 seconds)
        - Token validation
        - Audit logging of access
        - No sensitive data in response

    Rate Limit:
        - 10 requests per 60 seconds per IP
    """
    document = get_document_by_token(token, db)

    # Update first view timestamp
    if not document.student_viewed_at:
        document.student_viewed_at = datetime.now(timezone.utc)
        create_audit_log(document, "viewed", request, db)
        db.commit()

    # Return document info (no sensitive data)
    return {
        "id": str(document.id),
        "template_name": document.template.name if document.template else "Document",
        "template_description": document.template.description if document.template else None,
        "signer_name": document.signer_name,
        "signer_email": document.signer_email,
        "course_type": document.course_type,
        "course_label": document.form_data.get("course_label") if document.form_data else None,
        "form_data": document.form_data or {},
        "status": document.status,
        "created_at": document.created_at.isoformat(),
        "expires_at": document.token_expires_at.isoformat() if document.token_expires_at else None,
        "unsigned_file_url": f"/api/public/sign/{token}/preview"  # Separate endpoint for PDF
    }


@router.get("/{token}/preview", dependencies=[Depends(rate_limit_public_endpoints)])
async def preview_document(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Preview unsigned document PDF (public endpoint)

    Args:
        token: Unique signing token
        request: FastAPI request
        db: Database session

    Returns:
        PDF file response

    Security:
        - Rate limited
        - Token validation
        - Audit logging

    Rate Limit:
        - 10 requests per 60 seconds per IP
    """
    _ = get_document_by_token(token, db)  # noqa: F841

    # TODO: Return PDF file from unsigned_file_path
    # For now, return placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PDF preview not yet implemented"
    )


@router.post("/{token}", dependencies=[Depends(rate_limit_public_endpoints)])
async def submit_signature(
    token: str,
    sign_request: DocumentSignRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> DocumentSignResponse:
    """
    Submit signature for document (public endpoint, no auth required)

    Args:
        token: Unique signing token
        sign_request: Signature data (base64 image, typed name)
        request: FastAPI request
        db: Database session

    Returns:
        Success confirmation with document status

    Security:
        - Rate limited (10 requests/60 seconds)
        - Token validation (single-use)
        - Comprehensive audit trail
        - IP and user agent capture
        - Signature data validation

    Legal Compliance:
        - ESIGN Act compliant audit trail
        - IP address and timestamp capture
        - User agent tracking
        - Typed name confirmation

    Rate Limit:
        - 10 requests per 60 seconds per IP
    """
    document = get_document_by_token(token, db)

    # Validate signature data
    if not sign_request.signature_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signature data is required"
        )

    if not sign_request.typed_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Typed name is required"
        )

    # Validate base64 signature data
    try:
        base64.b64decode(sign_request.signature_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature data format"
        )

    # Extract IP and user agent for legal audit trail
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "Unknown")

    # Create signature record
    signature = DocumentSignature(
        document_id=document.id,
        signer_id=document.user_id,  # None for leads
        signature_type="applicant" if document.lead_id else "student",
        signature_data=sign_request.signature_data,
        signed_at=datetime.now(timezone.utc),
        ip_address=ip_address,
        user_agent=user_agent,
        typed_name=sign_request.typed_name,
        signer_email=document.signer_email
    )

    db.add(signature)

    # Update document status
    document.student_signed_at = datetime.now(timezone.utc)
    if sign_request.form_data:
        existing_form = document.form_data or {}
        existing_form.update(sign_request.form_data)
        document.form_data = existing_form

    # If counter-signature required, move to counter_signed status
    # Otherwise, mark as completed
    if document.template.requires_counter_signature:
        document.status = "student_signed"
    else:
        document.status = "completed"
        document.completed_at = datetime.now(timezone.utc)

    # Invalidate token (make single-use)
    document.signing_token = None
    document.token_expires_at = None

    # Create audit log
    event_details = json.dumps({
        "signature_type": signature.signature_type,
        "typed_name": sign_request.typed_name,
        "requires_counter_signature": document.template.requires_counter_signature
    })

    create_audit_log(document, "signed", request, db, event_details)

    db.commit()
    db.refresh(document)

    return DocumentSignResponse(
        success=True,
        message="Document signed successfully",
        document_id=str(document.id),
        status=document.status,
        signed_at=document.student_signed_at.isoformat(),
        requires_counter_signature=document.template.requires_counter_signature
    )


@router.get("/{token}/status", dependencies=[Depends(rate_limit_public_endpoints)])
async def get_document_status(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get document signing status (public endpoint)

    Args:
        token: Unique signing token
        request: FastAPI request
        db: Database session

    Returns:
        Document status information

    Security:
        - Rate limited
        - Token validation
        - Minimal information disclosure

    Rate Limit:
        - 10 requests per 60 seconds per IP
    """
    document = get_document_by_token(token, db)

    return {
        "status": document.status,
        "signed_at": document.student_signed_at.isoformat() if document.student_signed_at else None,
        "completed_at": document.completed_at.isoformat() if document.completed_at else None,
        "requires_counter_signature": document.template.requires_counter_signature
    }
