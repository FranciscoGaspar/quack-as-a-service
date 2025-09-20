"""
Room management endpoints.
Provides information about rooms and their equipment requirements.
"""

from typing import List, Dict
from fastapi import APIRouter

from core.room_equipment_config import RoomEquipmentConfig

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=List[str])
async def get_all_rooms():
    """
    Get list of all available room names.
    
    Returns:
        List of room names that have equipment configurations
    """
    return RoomEquipmentConfig.get_all_rooms()


@router.get("/config", response_model=Dict[str, Dict])
async def get_all_room_configs():
    """
    Get complete configuration for all rooms.
    
    Returns:
        Dictionary mapping room names to their configurations
    """
    return RoomEquipmentConfig.get_all_room_configs()


@router.get("/{room_name}/config")
async def get_room_config(room_name: str):
    """
    Get configuration for a specific room.
    
    Args:
        room_name: Name of the room
        
    Returns:
        Room configuration including required equipment and detection queries
    """
    return RoomEquipmentConfig.get_room_config(room_name)


@router.get("/{room_name}/equipment", response_model=List[str])
async def get_room_equipment(room_name: str):
    """
    Get required equipment list for a specific room.
    
    Args:
        room_name: Name of the room
        
    Returns:
        List of required equipment for the room
    """
    return RoomEquipmentConfig.get_required_equipment(room_name)


@router.get("/{room_name}/description")
async def get_room_description(room_name: str):
    """
    Get description for a specific room.
    
    Args:
        room_name: Name of the room
        
    Returns:
        Room description string
    """
    return {"description": RoomEquipmentConfig.get_room_description(room_name)}
