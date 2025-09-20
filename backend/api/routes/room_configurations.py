"""
Room equipment configuration management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from database.services import RoomEquipmentConfigurationService, PersonalEntryService
from schemas import (
    RoomEquipmentConfigurationCreate,
    RoomEquipmentConfigurationUpdate, 
    RoomEquipmentConfigurationResponse,
    SuccessResponse
)

router = APIRouter(prefix="/room-configurations", tags=["Room Configurations"])


@router.post("", response_model=RoomEquipmentConfigurationResponse)
async def create_room_configuration(config: RoomEquipmentConfigurationCreate):
    """Create a new room equipment configuration."""
    try:
        db_config = RoomEquipmentConfigurationService.create(
            room_name=config.room_name,
            equipment_weights=config.equipment_weights,
            entry_threshold=config.entry_threshold,
            description=config.description
        )
        return RoomEquipmentConfigurationResponse.model_validate(db_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[RoomEquipmentConfigurationResponse])
async def get_room_configurations(
    include_inactive: bool = Query(False, description="Include inactive configurations")
):
    """Get all room equipment configurations."""
    try:
        configs = RoomEquipmentConfigurationService.get_all(include_inactive=include_inactive)
        return [RoomEquipmentConfigurationResponse.model_validate(config) for config in configs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{config_id}", response_model=RoomEquipmentConfigurationResponse)
async def get_room_configuration(config_id: int):
    """Get a room equipment configuration by ID."""
    try:
        config = RoomEquipmentConfigurationService.get_by_id(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Room configuration not found")
        return RoomEquipmentConfigurationResponse.model_validate(config)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-room/{room_name}", response_model=RoomEquipmentConfigurationResponse)
async def get_room_configuration_by_name(room_name: str):
    """Get room equipment configuration by room name."""
    try:
        config = RoomEquipmentConfigurationService.get_by_room_name(room_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Room configuration for '{room_name}' not found")
        return RoomEquipmentConfigurationResponse.model_validate(config)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{config_id}", response_model=RoomEquipmentConfigurationResponse)
async def update_room_configuration(config_id: int, config: RoomEquipmentConfigurationUpdate):
    """Update a room equipment configuration."""
    try:
        db_config = RoomEquipmentConfigurationService.get_by_id(config_id)
        if not db_config:
            raise HTTPException(status_code=404, detail="Room configuration not found")
        
        updated_config = RoomEquipmentConfigurationService.update(
            config_id,
            equipment_weights=config.equipment_weights,
            entry_threshold=config.entry_threshold,
            description=config.description,
            is_active=config.is_active
        )
        return RoomEquipmentConfigurationResponse.model_validate(updated_config)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{config_id}", response_model=SuccessResponse)
async def delete_room_configuration(config_id: int):
    """Delete a room equipment configuration."""
    try:
        config = RoomEquipmentConfigurationService.get_by_id(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Room configuration not found")
        
        RoomEquipmentConfigurationService.delete(config_id)
        return SuccessResponse(message=f"Room configuration {config_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-defaults", response_model=dict)
async def create_default_configurations():
    """Create default room equipment configurations for standard rooms."""
    try:
        created_configs = RoomEquipmentConfigurationService.create_default_configurations()
        
        return {
            "message": f"Created {len(created_configs)} default room configurations",
            "configurations": [
                RoomEquipmentConfigurationResponse.model_validate(config) 
                for config in created_configs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create default configurations: {str(e)}")


@router.post("/{config_id}/test", response_model=dict)
async def test_room_configuration(config_id: int, test_equipment: dict):
    """
    Test a room configuration with sample equipment to see approval result.
    
    Args:
        config_id: Room configuration ID to test
        test_equipment: Equipment to test (e.g., {"mask": true, "gloves": false})
    """
    try:
        config = RoomEquipmentConfigurationService.get_by_id(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Room configuration not found")
        
        score = config.calculate_equipment_score(test_equipment)
        is_approved = config.is_entry_approved(test_equipment)
        
        return {
            "room_name": config.room_name,
            "test_equipment": test_equipment,
            "equipment_score": score,
            "entry_threshold": config.entry_threshold,
            "is_approved": is_approved,
            "result": "APPROVED" if is_approved else "DENIED",
            "message": f"Score: {score:.1f}% {'≥' if is_approved else '<'} {config.entry_threshold}% threshold"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{config_id}/recalculate-entries", response_model=dict)
async def recalculate_entries_for_room(config_id: int):
    """
    Recalculate approval status for all entries in a room after configuration changes.
    """
    try:
        config = RoomEquipmentConfigurationService.get_by_id(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Room configuration not found")
        
        # Get all entries for this room
        entries = PersonalEntryService.get_by_room(config.room_name)
        
        updated_count = 0
        for entry in entries:
            try:
                PersonalEntryService.recalculate_approval_status(entry.id)
                updated_count += 1
            except Exception as e:
                print(f"⚠️  Failed to recalculate approval for entry {entry.id}: {e}")
        
        return {
            "message": f"Recalculated approval status for {updated_count} entries in room '{config.room_name}'",
            "room_name": config.room_name,
            "total_entries": len(entries),
            "updated_entries": updated_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/summary", response_model=dict)
async def get_room_configurations_analytics():
    """Get analytics summary of room configurations and their usage."""
    try:
        configs = RoomEquipmentConfigurationService.get_all(include_inactive=True)
        
        analytics = {
            "total_configurations": len(configs),
            "active_configurations": len([c for c in configs if c.is_active]),
            "inactive_configurations": len([c for c in configs if not c.is_active]),
            "rooms": []
        }
        
        for config in configs:
            # Get entries for this room
            entries = PersonalEntryService.get_by_room(config.room_name, limit=1000)
            
            # Ensure all entries have calculated approval status
            for entry in entries:
                if entry.is_approved is None:
                    try:
                        entry.calculate_and_set_approval_status()
                    except Exception as e:
                        print(f"⚠️  Could not calculate approval for entry {entry.id}: {e}")
            
            # Calculate approval statistics
            approved_entries = len([e for e in entries if e.is_approved is True])
            denied_entries = len([e for e in entries if e.is_approved is False])
            pending_entries = len([e for e in entries if e.is_approved is None])
            
            room_info = {
                "room_name": config.room_name,
                "is_active": config.is_active,
                "entry_threshold": config.entry_threshold,
                "equipment_weights": config.equipment_weights,
                "total_entries": len(entries),
                "approved_entries": approved_entries,
                "denied_entries": denied_entries,
                "pending_entries": pending_entries,
                "approval_rate": (approved_entries / len(entries) * 100) if entries else 0
            }
            
            analytics["rooms"].append(room_info)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


