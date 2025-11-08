"""
Document and E-Signature Schemas
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


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
    template_id: UUID
    user_id: UUID


class SignedDocumentResponse(BaseModel):
    id: UUID
    template_id: UUID
    user_id: UUID
    status: str
    unsigned_file_path: Optional[str] = None
    signed_file_path: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    student_viewed_at: Optional[datetime] = None
    student_signed_at: Optional[datetime] = None
    counter_signed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

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


# ==================== Document Signature Schemas ====================

class DocumentSignatureCreate(BaseModel):
    signature_type: str = Field(..., pattern="^(student|school_official)$")
    signature_data: str = Field(..., min_length=1)  # Base64 encoded signature image
    typed_name: Optional[str] = Field(None, max_length=255)


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
