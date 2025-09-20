#!/usr/bin/env python3
"""
Room Equipment Configuration seeder for creating various room types with equipment requirements.
"""

import sys
import os
from typing import List, Dict, Any

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_dir)

from database.connection import create_session
from database.models import RoomEquipmentConfiguration
from database.services import RoomEquipmentConfigurationService
from .base_seeder import BaseSeeder


class RoomEquipmentConfigurationSeeder(BaseSeeder):
    """Seeder for RoomEquipmentConfiguration model"""
    
    def get_seeder_name(self) -> str:
        return "Room Equipment Configuration Seeder"
    
    def seed(self) -> bool:
        """Seed room equipment configurations with various factory room types"""
        try:
            # Check if configurations already exist
            if self.check_data_exists(RoomEquipmentConfiguration):
                self.log_skip(f"Room configurations already exist - skipping creation")
                return True
            
            self.log_info("Creating room equipment configurations...")
            
            # Comprehensive room configurations for different factory areas
            room_configurations = [
                {
                    "room_name": "production-floor",
                    "equipment_weights": {
                        "mask": "required",
                        "gloves": "required", 
                        "hairnet": "required",
                    },
                    "entry_threshold": 5.0,
                    "description": "Production Floor - High safety requirements for manufacturing operations",
                    "is_active": True
                },
                {
                    "room_name": "assembly-line",
                    "equipment_weights": {
                        "gloves": "required",
                        "hairnet": "recommended",
                    },
                    "entry_threshold": 5.0,
                    "description": "Assembly Line - Moderate safety requirements for assembly operations",
                    "is_active": True
                },
                {
                    "room_name": "packaging-area",
                    "equipment_weights": {
                        "gloves": "required",
                    },
                    "entry_threshold": 5.0,
                    "description": "Packaging Area - Basic hygiene requirements for packaging operations",
                    "is_active": True
                }
            ]
            
            created_configs = []
            
            for config_data in room_configurations:
                try:
                    config = RoomEquipmentConfigurationService.create(
                        room_name=config_data["room_name"],
                        equipment_weights=config_data["equipment_weights"],
                        entry_threshold=config_data["entry_threshold"],
                        description=config_data["description"]
                    )
                    
                    # Set active status
                    if "is_active" in config_data:
                        RoomEquipmentConfigurationService.update(
                            config.id,
                            is_active=config_data["is_active"]
                        )
                    
                    created_configs.append(config)
                    self.log_success(f"Created room config: {config.room_name}")
                    
                except Exception as e:
                    self.log_error(f"Failed to create room config {config_data['room_name']}: {e}")
            
            self.commit()
            
            self.log_info(f"Successfully created {len(created_configs)} room configurations")
            self.log_info("Room types include: production, assembly, packaging, quality control, maintenance, warehouse, chemical processing, clean room, loading dock, office, break room, and training areas")
            
            return True
            
        except Exception as e:
            self.log_error(f"Room configuration seeding failed: {e}")
            self.rollback()
            return False
    
    def get_sample_configs(self) -> List[RoomEquipmentConfiguration]:
        """Get a sample of created configurations for use by other seeders"""
        return RoomEquipmentConfigurationService.get_all()
    
    def get_config_by_room_name(self, room_name: str) -> RoomEquipmentConfiguration:
        """Get configuration by room name"""
        return RoomEquipmentConfigurationService.get_by_room_name(room_name)
    
    def get_high_safety_rooms(self) -> List[RoomEquipmentConfiguration]:
        """Get rooms with high safety requirements (many required items)"""
        all_configs = RoomEquipmentConfigurationService.get_all()
        high_safety_rooms = []
        
        for config in all_configs:
            required_count = sum(1 for level in config.equipment_weights.values() if level == "required")
            if required_count >= 4:  # 4 or more required items
                high_safety_rooms.append(config)
        
        return high_safety_rooms
    
    def get_low_safety_rooms(self) -> List[RoomEquipmentConfiguration]:
        """Get rooms with low safety requirements (few required items)"""
        all_configs = RoomEquipmentConfigurationService.get_all()
        low_safety_rooms = []
        
        for config in all_configs:
            required_count = sum(1 for level in config.equipment_weights.values() if level == "required")
            if required_count <= 2:  # 2 or fewer required items
                low_safety_rooms.append(config)
        
        return low_safety_rooms
