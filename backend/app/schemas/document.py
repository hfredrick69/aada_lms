"""
Document and E-Signature Schemas
"""

from typing import Optional, List, Dict, Any, Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import html


# ==================== Document Template Schemas ====================

class DocumentTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    version: str = Field(..., min_length=1, max_length=50)
    requires_counter_signature: bool = False


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DocumentTemplateResponse(DocumentTemplateBase):
    id: UUID
    file_path: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== Signed Document Schemas ====================

class SignedDocumentCreate(BaseModel):
    """Create a signed document for either a user or a lead"""
    template_id: UUID
    user_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    signer_name: Optional[str] = Field(None, max_length=255)
    signer_email: Optional[str] = Field(None, max_length=255)
    course_type: Optional[str] = Field(None, max_length=50)
    form_data: Optional[Dict[str, Any]] = None

    class Config:
        # Must have either user_id or lead_id, not both
        # This will be validated at the business logic layer
        pass


class SignedDocumentResponse(BaseModel):
    id: UUID
    template_id: UUID
    user_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    signer_name: Optional[str] = None
    signer_email: Optional[str] = None
    signing_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    status: str
    unsigned_file_path: Optional[str] = None
    signed_file_path: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    student_viewed_at: Optional[datetime] = None
    student_signed_at: Optional[datetime] = None
    counter_signed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    course_type: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None
    retention_expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SignedDocumentWithTemplate(SignedDocumentResponse):
    """Document with embedded template information"""
    template_name: str
    template_version: str
    requires_counter_signature: bool


class SignedDocumentListResponse(BaseModel):
    documents: List[SignedDocumentWithTemplate]
    total: int


class EnrollmentAgreementRequest(BaseModel):
    user_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    course_type: Literal["twenty_week", "expanded_functions"]
    template_id: Optional[UUID] = None
    signer_name: Optional[str] = Field(None, max_length=255)
    signer_email: Optional[str] = Field(None, max_length=255)
    form_data: Optional[Dict[str, Any]] = None


class CounterSignRequest(BaseModel):
    signature_data: str = Field(..., min_length=1)
    typed_name: str = Field(..., max_length=255)


class AdvisorDirectoryEntry(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)
    title: Optional[str] = None


# ==================== Document Signature Schemas ====================

class DocumentSignatureCreate(BaseModel):
    signature_type: str = Field(..., pattern="^(applicant|student|school_official)$")
    signature_data: str = Field(..., min_length=1)  # Base64 encoded signature image
    typed_name: str = Field(..., max_length=255)  # Required for all signatures


class DocumentSignatureResponse(BaseModel):
    id: UUID
    document_id: UUID
    signer_id: UUID
    signature_type: str
    signed_at: datetime
    ip_address: str
    user_agent: str
    typed_name: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== Document Audit Log Schemas ====================

class DocumentAuditLogResponse(BaseModel):
    id: UUID
    document_id: UUID
    user_id: Optional[UUID] = None
    event_type: str
    event_details: Optional[str] = None
    occurred_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentAuditLogListResponse(BaseModel):
    logs: List[DocumentAuditLogResponse]
    total: int


# ==================== Document View/Download Schemas ====================

class DocumentViewRequest(BaseModel):
    """Request to mark a document as viewed"""
    pass


class DocumentDownloadResponse(BaseModel):
    """Response containing document download information"""
    document_id: UUID
    filename: str
    content_type: str = "application/pdf"
    download_url: str  # Pre-signed URL or direct path


# ==================== Public Signing Schemas ====================

class DocumentSignRequest(BaseModel):
    """Request to sign a document via public endpoint"""
    signature_data: str = Field(..., min_length=1)  # Base64 encoded signature image
    typed_name: str = Field(..., min_length=1, max_length=255)
    form_data: Optional[Dict[str, Any]] = Field(None, max_length=100)

    @field_validator('form_data')
    @classmethod
    def validate_and_sanitize_form_data(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate and sanitize form data to prevent XSS and limit abuse

        Security measures:
        - All values must be strings
        - Maximum 100 fields
        - Maximum 1000 characters per field
        - HTML escape all values to prevent XSS
        """
        if not v:
            return v

        if len(v) > 100:
            raise ValueError("form_data cannot contain more than 100 fields")

        sanitized = {}
        for key, value in v.items():
            # Ensure all values are strings
            if not isinstance(value, str):
                raise ValueError(f"Form field '{key}' must be a string, got {type(value).__name__}")

            # Limit field length
            if len(value) > 1000:
                raise ValueError(f"Form field '{key}' exceeds maximum length of 1000 characters")

            # HTML escape to prevent XSS attacks
            sanitized[key] = html.escape(value)

        return sanitized


class DocumentSignResponse(BaseModel):
    """Response after signing a document via public endpoint"""
    success: bool
    message: str
    document_id: str
    status: str
    signed_at: str
    requires_counter_signature: bool
