"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, max_length=100, description="User's name")
    qr_code: Optional[str] = Field(None, max_length=255, description="Unique QR code for the user")


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's name")
    qr_code: Optional[str] = Field(None, max_length=255, description="Unique QR code for the user")


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PersonalEntryBase(BaseModel):
    """Base personal entry schema."""
    room_name: str = Field(..., min_length=1, max_length=100, description="Room name")
    equipment: Dict[str, bool] = Field(..., description="Equipment tracking (e.g., {'mask': True, 'gloves': False})")
    image_url: Optional[str] = Field(None, max_length=500, description="URL to entry image")


class PersonalEntryCreate(PersonalEntryBase):
    """Schema for creating a personal entry."""
    user_id: Optional[int] = Field(None, description="User ID (optional)")


class PersonalEntryUpdate(BaseModel):
    """Schema for updating a personal entry."""
    room_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Room name")
    equipment: Optional[Dict[str, bool]] = Field(None, description="Equipment tracking")
    image_url: Optional[str] = Field(None, max_length=500, description="URL to entry image")


class PersonalEntryBaseResponse(PersonalEntryBase):
    """Base schema for personal entry response (without computed fields)."""
    id: int
    user_id: Optional[int]
    # New approval fields
    is_approved: Optional[bool] = Field(None, description="Entry approval status (True=approved, False=denied, None=pending)")
    equipment_score: Optional[float] = Field(None, description="Equipment compliance score (0-100)")
    approval_reason: Optional[str] = Field(None, description="Reason for approval/denial decision")
    entered_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PersonalEntryResponse(PersonalEntryBaseResponse):
    """Schema for personal entry response with computed fields."""
    is_compliant: bool = Field(..., description="Whether all required equipment is present")
    missing_equipment: list[str] = Field(..., description="List of missing equipment items")
    user_name: Optional[str] = Field(None, description="Name of the user associated with this entry")


class EquipmentUpdate(BaseModel):
    """Schema for updating specific equipment items."""
    mask: Optional[bool] = None
    right_glove: Optional[bool] = None
    left_glove: Optional[bool] = None
    hairnet: Optional[bool] = None
    safety_glasses: Optional[bool] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str = Field(..., description="Error message")


class SuccessResponse(BaseModel):
    """Schema for success responses."""
    message: str = Field(..., description="Success message")


class ImageUploadRequest(BaseModel):
    """Schema for image upload request."""
    room_name: str = Field(..., min_length=1, max_length=100, description="Room name")
    user_id: int = Field(..., description="User ID (required)")


# Room Equipment Configuration Schemas
class RoomEquipmentConfigurationBase(BaseModel):
    """Base schema for room equipment configuration."""
    room_name: str = Field(..., min_length=1, max_length=100, description="Room name")
    equipment_weights: Dict[str, str] = Field(..., description="Equipment requirement levels (e.g., {'mask': 'required', 'gloves': 'recommended'})")
    entry_threshold: float = Field(70.0, ge=0, le=100, description="Minimum score required for entry approval (0-100)")
    description: Optional[str] = Field(None, max_length=500, description="Room configuration description")
    is_active: bool = Field(True, description="Whether this configuration is active")


class RoomEquipmentConfigurationCreate(RoomEquipmentConfigurationBase):
    """Schema for creating a room equipment configuration."""
    pass


class RoomEquipmentConfigurationUpdate(BaseModel):
    """Schema for updating a room equipment configuration."""
    equipment_weights: Optional[Dict[str, float]] = Field(None, description="Equipment weights")
    entry_threshold: Optional[float] = Field(None, ge=0, le=100, description="Minimum score for entry approval")
    description: Optional[str] = Field(None, max_length=500, description="Room configuration description")
    is_active: Optional[bool] = Field(None, description="Whether this configuration is active")


class RoomEquipmentConfigurationResponse(RoomEquipmentConfigurationBase):
    """Schema for room equipment configuration response."""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Enhanced schemas for approval status display
class ApprovalStatusDisplay(BaseModel):
    """Schema for displaying approval status information."""
    status: str = Field(..., description="Human-readable approval status (Approved/Denied/Pending)")
    color: str = Field(..., description="Color for status badge (green/red/yellow)")
    score: Optional[float] = Field(None, description="Equipment compliance score")
    threshold: Optional[float] = Field(None, description="Required threshold for approval")
    reason: Optional[str] = Field(None, description="Approval/denial reason")


class PersonalEntryWithApprovalStatus(PersonalEntryResponse):
    """Enhanced entry response with approval status display information."""
    approval_status: ApprovalStatusDisplay = Field(..., description="Approval status display information")
