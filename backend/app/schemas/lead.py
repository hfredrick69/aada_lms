"""Pydantic schemas for CRM Lead management."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# LeadSource Schemas
class LeadSourceBase(BaseModel):
    """Base schema for LeadSource."""
    name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class LeadSourceCreate(LeadSourceBase):
    """Schema for creating a LeadSource."""
    pass


class LeadSourceUpdate(BaseModel):
    """Schema for updating a LeadSource."""
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class LeadSourceResponse(LeadSourceBase):
    """Schema for LeadSource response."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Lead Schemas
class LeadBase(BaseModel):
    """Base schema for Lead."""
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    lead_source_id: UUID
    program_interest_id: Optional[UUID] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a Lead."""
    pass


class LeadUpdate(BaseModel):
    """Schema for updating a Lead."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    lead_source_id: Optional[UUID] = None
    lead_status: Optional[str] = Field(None, max_length=50)
    lead_score: Optional[int] = None
    assigned_to_id: Optional[UUID] = None
    program_interest_id: Optional[UUID] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    """Schema for Lead response."""
    id: UUID
    lead_status: str
    lead_score: int
    assigned_to_id: Optional[UUID]
    converted_to_application_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadDetailResponse(LeadResponse):
    """Schema for detailed Lead response with relationships."""
    lead_source: Optional[LeadSourceResponse] = None
    assigned_to_name: Optional[str] = None
    program_interest_name: Optional[str] = None

    class Config:
        from_attributes = True


# Custom Field Schemas
class LeadCustomFieldBase(BaseModel):
    """Base schema for LeadCustomField."""
    field_name: str = Field(..., max_length=100)
    field_value: Optional[str] = None


class LeadCustomFieldCreate(LeadCustomFieldBase):
    """Schema for creating a LeadCustomField."""
    lead_id: UUID


class LeadCustomFieldUpdate(BaseModel):
    """Schema for updating a LeadCustomField."""
    field_value: Optional[str] = None


class LeadCustomFieldResponse(LeadCustomFieldBase):
    """Schema for LeadCustomField response."""
    id: UUID
    lead_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# List Response Schemas
class LeadListResponse(BaseModel):
    """Schema for paginated lead list."""
    total: int
    leads: List[LeadResponse]


# Activity Schemas (for lead activities)
class ActivityBase(BaseModel):
    """Base schema for Activity."""
    entity_type: str = Field(..., max_length=50)  # lead, application, user
    entity_id: UUID
    activity_type: str = Field(..., max_length=50)  # call, email, sms, meeting, note, task
    subject: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[UUID] = None


class ActivityCreate(ActivityBase):
    """Schema for creating an Activity."""
    pass


class ActivityUpdate(BaseModel):
    """Schema for updating an Activity."""
    activity_type: Optional[str] = Field(None, max_length=50)
    subject: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_to_id: Optional[UUID] = None


class ActivityResponse(ActivityBase):
    """Schema for Activity response."""
    id: UUID
    completed_at: Optional[datetime]
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityDetailResponse(ActivityResponse):
    """Schema for detailed Activity response with relationships."""
    assigned_to_name: Optional[str] = None
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True
