#!/usr/bin/env python3
"""
Personal Entry seeder for creating realistic factory entry records with equipment detection data.
"""

import sys
import os
from typing import List, Dict, Any
import random
from datetime import datetime, timezone, timedelta

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_dir)

from database.connection import create_session
from database.models import PersonalEntry
from database.services import PersonalEntryService, UserService, RoomEquipmentConfigurationService
from .base_seeder import BaseSeeder, random_date_in_range, random_equipment_detection


class PersonalEntrySeeder(BaseSeeder):
    """Seeder for PersonalEntry model"""
    
    def get_seeder_name(self) -> str:
        return "Personal Entry Seeder"
    
    def seed(self) -> bool:
        """Seed personal entries with realistic factory entry data"""
        try:
            # Check if entries already exist
            if self.check_data_exists(PersonalEntry):
                self.log_skip(f"Personal entries already exist - skipping creation")
                return True
            
            # Get dependencies
            users = UserService.get_all()
            room_configs = RoomEquipmentConfigurationService.get_all()
            
            if not users:
                self.log_error("No users found - run UserSeeder first")
                return False
            
            if not room_configs:
                self.log_error("No room configurations found - run RoomEquipmentConfigurationSeeder first")
                return False
            
            self.log_info("Creating personal entries with equipment detection data...")
            
            # Generate realistic entry scenarios
            entry_scenarios = self._generate_entry_scenarios(users, room_configs)
            
            created_entries = []
            
            for scenario in entry_scenarios:
                try:
                    entry = PersonalEntryService.create(
                        user_id=scenario["user_id"],
                        room_name=scenario["room_name"],
                        equipment=scenario["equipment"],
                        image_url=scenario["image_url"],
                        calculate_approval=True  # Calculate approval status based on room config
                    )
                    
                    # Update entry timestamp to be more realistic
                    entry.entered_at = scenario["entered_at"]
                    entry.created_at = scenario["created_at"]
                    
                    created_entries.append(entry)
                    self.log_success(f"Created entry: {scenario['user_name']} -> {scenario['room_name']} (Score: {entry.equipment_score:.1f}%)")
                    
                except Exception as e:
                    self.log_error(f"Failed to create entry for {scenario['user_name']}: {e}")
            
            self.commit()
            
            self.log_info(f"Successfully created {len(created_entries)} personal entries")
            self.log_info("Entries include various equipment compliance scenarios: compliant, non-compliant, and mixed compliance")
            
            return True
            
        except Exception as e:
            self.log_error(f"Personal entry seeding failed: {e}")
            self.rollback()
            return False
    
    def _generate_entry_scenarios(self, users: List, room_configs: List) -> List[Dict[str, Any]]:
        """Generate realistic entry scenarios"""
        scenarios = []
        
        # Room names from configurations
        room_names = [config.room_name for config in room_configs]
        
        # Generate entries for the last 30 days
        for i in range(50):  # Generate 50 entries
            user = random.choice(users)
            room_name = random.choice(room_names)
            
            # Get room configuration to generate realistic equipment
            room_config = next((config for config in room_configs if config.room_name == room_name), None)
            
            if room_config:
                # Generate equipment based on room requirements
                equipment = self._generate_realistic_equipment(room_config)
            else:
                # Fallback to random equipment
                equipment = random_equipment_detection()
            
            # Generate realistic timestamps (more entries during work hours)
            entered_at = self._generate_realistic_timestamp()
            
            # Generate image URL (placeholder)
            image_url = f"https://example.com/entry_images/entry_{i+1:04d}.jpg"
            
            scenario = {
                "user_id": user.id,
                "user_name": user.name,
                "room_name": room_name,
                "equipment": equipment,
                "image_url": image_url,
                "entered_at": entered_at,
                "created_at": entered_at
            }
            
            scenarios.append(scenario)
        
        return scenarios
    
    def _generate_realistic_equipment(self, room_config) -> Dict[str, bool]:
        """Generate realistic equipment detection based on room requirements"""
        equipment = {}
        
        # Get required and recommended equipment from room config
        required_items = [item for item, level in room_config.equipment_weights.items() if level == "required"]
        recommended_items = [item for item, level in room_config.equipment_weights.items() if level == "recommended"]
        
        # Generate compliance scenarios
        compliance_scenario = random.choice([
            "fully_compliant",      # 40% chance
            "mostly_compliant",    # 30% chance  
            "partially_compliant", # 20% chance
            "non_compliant"        # 10% chance
        ])
        
        if compliance_scenario == "fully_compliant":
            # All required and most recommended items present
            for item in required_items:
                equipment[item] = True
            for item in recommended_items:
                equipment[item] = random.random() < 0.8  # 80% chance
            
        elif compliance_scenario == "mostly_compliant":
            # All required items present, some recommended missing
            for item in required_items:
                equipment[item] = True
            for item in recommended_items:
                equipment[item] = random.random() < 0.6  # 60% chance
                
        elif compliance_scenario == "partially_compliant":
            # Some required items missing
            for item in required_items:
                equipment[item] = random.random() < 0.7  # 70% chance
            for item in recommended_items:
                equipment[item] = random.random() < 0.4  # 40% chance
                
        else:  # non_compliant
            # Many required items missing
            for item in required_items:
                equipment[item] = random.random() < 0.3  # 30% chance
            for item in recommended_items:
                equipment[item] = random.random() < 0.2  # 20% chance
        
        # Only use equipment defined in the room configurations - no additional equipment
        
        return equipment
    
    def _generate_realistic_timestamp(self) -> datetime:
        """Generate realistic timestamps (more entries during work hours)"""
        # Generate date within last 30 days
        base_date = random_date_in_range(30)
        
        # Adjust for work hours (more entries during 6 AM - 6 PM)
        hour = base_date.hour
        
        # Weight entries more heavily during work hours
        if 6 <= hour <= 18:  # Work hours
            # Keep the original time
            return base_date
        else:  # Non-work hours
            # Adjust to work hours with some probability
            if random.random() < 0.3:  # 30% chance to adjust to work hours
                work_hour = random.randint(6, 18)
                return base_date.replace(hour=work_hour, minute=random.randint(0, 59))
            else:
                return base_date
    
    def get_sample_entries(self) -> List[PersonalEntry]:
        """Get a sample of created entries for use by other seeders"""
        return PersonalEntryService.get_all(limit=50)
    
    def get_entries_by_room(self, room_name: str) -> List[PersonalEntry]:
        """Get entries by room name"""
        return PersonalEntryService.get_by_room(room_name)
    
    def get_approved_entries(self) -> List[PersonalEntry]:
        """Get approved entries"""
        all_entries = PersonalEntryService.get_all()
        return [entry for entry in all_entries if entry.is_approved is True]
    
    def get_denied_entries(self) -> List[PersonalEntry]:
        """Get denied entries"""
        all_entries = PersonalEntryService.get_all()
        return [entry for entry in all_entries if entry.is_approved is False]
    
    def get_pending_entries(self) -> List[PersonalEntry]:
        """Get pending entries"""
        all_entries = PersonalEntryService.get_all()
        return [entry for entry in all_entries if entry.is_approved is None]
    
    def get_high_score_entries(self, min_score: float = 80.0) -> List[PersonalEntry]:
        """Get entries with high equipment scores"""
        all_entries = PersonalEntryService.get_all()
        return [entry for entry in all_entries if entry.equipment_score and entry.equipment_score >= min_score]
    
    def get_low_score_entries(self, max_score: float = 50.0) -> List[PersonalEntry]:
        """Get entries with low equipment scores"""
        all_entries = PersonalEntryService.get_all()
        return [entry for entry in all_entries if entry.equipment_score and entry.equipment_score <= max_score]
