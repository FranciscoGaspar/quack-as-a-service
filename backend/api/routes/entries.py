"""
Personal entry management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from database.services import UserService, PersonalEntryService
from schemas import (
    PersonalEntryCreate, PersonalEntryUpdate, PersonalEntryResponse,
    PersonalEntryBaseResponse, EquipmentUpdate, SuccessResponse
)

router = APIRouter(prefix="/entries", tags=["Personal Entries"])


def _add_computed_fields(entry) -> PersonalEntryResponse:
    """Add computed fields to entry response."""
    # First validate with base schema (no computed fields)
    base_data = PersonalEntryBaseResponse.model_validate(entry)
    
    # Then create full response with computed fields
    return PersonalEntryResponse(
        **base_data.model_dump(),
        is_compliant=entry.is_compliant(),
        missing_equipment=entry.get_missing_equipment()
    )


@router.post("", response_model=PersonalEntryResponse)
async def create_entry(entry: PersonalEntryCreate):
    """Create a new personal entry."""
    try:
        db_entry = PersonalEntryService.create(
            user_id=entry.user_id,
            room_name=entry.room_name,
            equipment=entry.equipment,
            image_url=entry.image_url
        )
        return _add_computed_fields(db_entry)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[PersonalEntryResponse])
async def get_entries(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results")
):
    """Get all personal entries."""
    try:
        entries = PersonalEntryService.get_all(limit=limit)
        return [_add_computed_fields(entry) for entry in entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}", response_model=PersonalEntryResponse)
async def get_entry(entry_id: int):
    """Get a personal entry by ID."""
    try:
        entry = PersonalEntryService.get_by_id(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return _add_computed_fields(entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{entry_id}", response_model=PersonalEntryResponse)
async def update_entry(entry_id: int, entry: PersonalEntryUpdate):
    """Update a personal entry."""
    try:
        db_entry = PersonalEntryService.get_by_id(entry_id)
        if not db_entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        updated_entry = PersonalEntryService.update(
            entry_id,
            room_name=entry.room_name,
            equipment=entry.equipment,
            image_url=entry.image_url
        )
        return _add_computed_fields(updated_entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{entry_id}/equipment", response_model=PersonalEntryResponse)
async def update_entry_equipment(entry_id: int, equipment: EquipmentUpdate):
    """Update specific equipment items for an entry."""
    try:
        db_entry = PersonalEntryService.get_by_id(entry_id)
        if not db_entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        # Convert to dict, excluding None values
        equipment_dict = equipment.dict(exclude_none=True)
        if not equipment_dict:
            raise HTTPException(status_code=400, detail="No equipment updates provided")
        
        updated_entry = PersonalEntryService.update_equipment(entry_id, **equipment_dict)
        return _add_computed_fields(updated_entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{entry_id}", response_model=SuccessResponse)
async def delete_entry(entry_id: int):
    """Delete a personal entry."""
    try:
        entry = PersonalEntryService.get_by_id(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        PersonalEntryService.delete(entry_id)
        return SuccessResponse(message=f"Entry {entry_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Additional endpoints with different URL patterns
from fastapi import APIRouter as BaseRouter

# Create separate routers for user and room-based queries
user_entries_router = BaseRouter(prefix="/users", tags=["Personal Entries"])
room_entries_router = BaseRouter(prefix="/rooms", tags=["Personal Entries"])


@user_entries_router.get("/{user_id}/entries", response_model=List[PersonalEntryResponse])
async def get_user_entries(
    user_id: int,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results")
):
    """Get all entries for a specific user."""
    try:
        # Check if user exists
        user = UserService.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        entries = PersonalEntryService.get_by_user(user_id, limit=limit)
        return [_add_computed_fields(entry) for entry in entries]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@room_entries_router.get("/{room_name}/entries", response_model=List[PersonalEntryResponse])
async def get_room_entries(
    room_name: str,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results")
):
    """Get all entries for a specific room."""
    try:
        entries = PersonalEntryService.get_by_room(room_name, limit=limit)
        return [_add_computed_fields(entry) for entry in entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
