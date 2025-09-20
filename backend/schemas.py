"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, max_length=100, description="User's name")


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's name")


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
    entered_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PersonalEntryResponse(PersonalEntryBaseResponse):
    """Schema for personal entry response with computed fields."""
    is_compliant: bool = Field(..., description="Whether all required equipment is present")
    missing_equipment: list[str] = Field(..., description="List of missing equipment items")


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
