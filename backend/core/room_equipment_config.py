"""
Room Equipment Configuration
Defines required equipment for each room dynamically
"""

from typing import Dict, List, Optional

# Room equipment mapping - defines required equipment per room
ROOM_EQUIPMENT_MAP: Dict[str, Dict] = {
    "production-floor": {
        "required_equipment": ["mask", "gloves", "hairnet"],
        "detection_queries": "a mask. gloves. a hairnet. protective equipment.",
        "description": "Production Floor - Heavy machinery and industrial equipment area",
    },
    "assembly-line": {
        "required_equipment": ["gloves", "hairnet"],
        "detection_queries": "gloves. a hairnet. protective equipment.",
        "description": "Assembly Line - Precision assembly and quality control",
    },
    "packaging-area": {
        "required_equipment": ["gloves"],
        "detection_queries": "gloves. protective equipment.",
        "description": "Packaging Area - Food packaging and hygiene control",
    },
}

# Default fallback configuration for unknown rooms
DEFAULT_ROOM_CONFIG = {
    "required_equipment": ["mask", "gloves"],
    "detection_queries": "a mask. gloves. protective equipment.",
    "description": "General Area - Basic safety requirements",
}


class RoomEquipmentConfig:
    """Service class for managing room-specific equipment configurations"""
    
    @classmethod
    def get_room_config(cls, room_name: str) -> Dict:
        """
        Get equipment configuration for a specific room
        
        Args:
            room_name: Name of the room (e.g., "production-floor")
            
        Returns:
            Dictionary containing required_equipment, detection_queries, and description
        """
        room_key = room_name.lower().strip().replace(" ", "-")
        return ROOM_EQUIPMENT_MAP.get(room_key, DEFAULT_ROOM_CONFIG.copy())
    
    @classmethod
    def get_required_equipment(cls, room_name: str) -> List[str]:
        """Get list of required equipment for a room"""
        config = cls.get_room_config(room_name)
        return config["required_equipment"]
    
    @classmethod
    def get_detection_queries(cls, room_name: str) -> str:
        """Get detection queries string for a room"""
        config = cls.get_room_config(room_name)
        return config["detection_queries"]
    
    @classmethod
    def get_room_description(cls, room_name: str) -> str:
        """Get description for a room"""
        config = cls.get_room_config(room_name)
        return config["description"]
    
    @classmethod
    def is_compliant(cls, room_name: str, detected_equipment: Dict[str, bool]) -> bool:
        """
        Check if detected equipment meets room requirements
        
        Args:
            room_name: Name of the room
            detected_equipment: Dictionary of equipment -> detected status
            
        Returns:
            True if all required equipment is detected, False otherwise
        """
        required_equipment = cls.get_required_equipment(room_name)
        
        # Handle different glove detection formats
        # If we have separate left/right gloves, consider "gloves" present if both are present
        if "gloves" in required_equipment and "gloves" not in detected_equipment:
            left_glove = detected_equipment.get("left_glove", False)
            right_glove = detected_equipment.get("right_glove", False)
            detected_equipment = detected_equipment.copy()
            detected_equipment["gloves"] = left_glove and right_glove
        
        # Check if all required equipment is detected
        return all(detected_equipment.get(item, False) for item in required_equipment)
    
    @classmethod
    def get_missing_equipment(cls, room_name: str, detected_equipment: Dict[str, bool]) -> List[str]:
        """
        Get list of missing equipment for a room
        
        Args:
            room_name: Name of the room
            detected_equipment: Dictionary of equipment -> detected status
            
        Returns:
            List of missing equipment items
        """
        required_equipment = cls.get_required_equipment(room_name)
        
        # Handle different glove detection formats
        detected_equipment_copy = detected_equipment.copy()
        if "gloves" in required_equipment and "gloves" not in detected_equipment:
            left_glove = detected_equipment.get("left_glove", False)
            right_glove = detected_equipment.get("right_glove", False)
            detected_equipment_copy["gloves"] = left_glove and right_glove
        
        missing = []
        for item in required_equipment:
            if not detected_equipment_copy.get(item, False):
                missing.append(item)
        
        return missing
    
    @classmethod
    def get_all_rooms(cls) -> List[str]:
        """Get list of all configured room names"""
        return list(ROOM_EQUIPMENT_MAP.keys())
    
    @classmethod
    def get_all_room_configs(cls) -> Dict[str, Dict]:
        """Get all room configurations"""
        return ROOM_EQUIPMENT_MAP.copy()


def get_room_equipment_map() -> Dict[str, Dict]:
    """
    Public function to get the complete room equipment mapping
    Used by other modules that need the full configuration
    """
    return ROOM_EQUIPMENT_MAP.copy()


# Equipment label mapping for UI display
EQUIPMENT_DISPLAY_LABELS: Dict[str, str] = {
    "mask": "Face Mask",
    "gloves": "Gloves",
    "left_glove": "Left Glove",
    "right_glove": "Right Glove",
    "hairnet": "Hair Net",
    "hard_hat": "Hard Hat",
    "safety_vest": "Safety Vest",
    "safety_glasses": "Safety Glasses",
    "boots": "Safety Boots",
}


def get_equipment_display_name(equipment_key: str) -> str:
    """Get display-friendly name for equipment"""
    return EQUIPMENT_DISPLAY_LABELS.get(equipment_key, equipment_key.replace("_", " ").title())
