#!/usr/bin/env python3
"""
User seeder for creating realistic factory worker data.
"""

import sys
import os
from typing import List, Dict, Any
import random

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_dir)

from database.connection import create_session
from database.models import User
from database.services import UserService
from .base_seeder import BaseSeeder


class UserSeeder(BaseSeeder):
    """Seeder for User model"""
    
    def get_seeder_name(self) -> str:
        return "User Seeder"
    
    def seed(self) -> bool:
        """Seed users with realistic factory worker data"""
        try:
            # Check if users already exist
            if self.check_data_exists(User):
                self.log_skip(f"Users already exist - skipping user creation")
                return True
            
            self.log_info("Creating factory worker users...")
            
            # Realistic factory worker names and roles
            factory_workers = [
                {"name": "Alice Johnson", "role": "Production Supervisor", "qr_code": "QR_ALICE_001"},
                {"name": "Bob Smith", "role": "Assembly Line Worker", "qr_code": "QR_BOB_002"},
                {"name": "Carol Davis", "role": "Quality Inspector", "qr_code": "QR_CAROL_003"},
                {"name": "David Wilson", "role": "Machine Operator", "qr_code": "QR_DAVID_004"},
                {"name": "Eva Martinez", "role": "Packaging Specialist", "qr_code": "QR_EVA_005"},
                {"name": "Frank Brown", "role": "Maintenance Technician", "qr_code": "QR_FRANK_006"},
                {"name": "Grace Lee", "role": "Safety Coordinator", "qr_code": "QR_GRACE_007"},
                {"name": "Henry Taylor", "role": "Warehouse Worker", "qr_code": "QR_HENRY_008"},
                {"name": "Iris Garcia", "role": "Production Manager", "qr_code": "QR_IRIS_009"},
                {"name": "Jack Anderson", "role": "Forklift Operator", "qr_code": "QR_JACK_010"},
                {"name": "Kate Thompson", "role": "Assembly Line Worker", "qr_code": "QR_KATE_011"},
                {"name": "Liam Rodriguez", "role": "Machine Operator", "qr_code": "QR_LIAM_012"},
                {"name": "Maya Patel", "role": "Quality Inspector", "qr_code": "QR_MAYA_013"},
                {"name": "Noah Kim", "role": "Packaging Specialist", "qr_code": "QR_NOAH_014"},
                {"name": "Olivia White", "role": "Production Supervisor", "qr_code": "QR_OLIVIA_015"},
                {"name": "Paul Johnson", "role": "Maintenance Technician", "qr_code": "QR_PAUL_016"},
                {"name": "Quinn Davis", "role": "Safety Coordinator", "qr_code": "QR_QUINN_017"},
                {"name": "Rachel Wilson", "role": "Warehouse Worker", "qr_code": "QR_RACHEL_018"},
                {"name": "Sam Garcia", "role": "Forklift Operator", "qr_code": "QR_SAM_019"},
                {"name": "Tina Brown", "role": "Assembly Line Worker", "qr_code": "QR_TINA_020"},
                {"name": "Uma Taylor", "role": "Machine Operator", "qr_code": "QR_UMA_021"},
                {"name": "Victor Lee", "role": "Quality Inspector", "qr_code": "QR_VICTOR_022"},
                {"name": "Wendy Anderson", "role": "Packaging Specialist", "qr_code": "QR_WENDY_023"},
                {"name": "Xavier Thompson", "role": "Production Manager", "qr_code": "QR_XAVIER_024"},
                {"name": "Yara Rodriguez", "role": "Maintenance Technician", "qr_code": "QR_YARA_025"},
                {"name": "Zoe Patel", "role": "Safety Coordinator", "qr_code": "QR_ZOE_026"},
                {"name": "Alex Kim", "role": "Warehouse Worker", "qr_code": "QR_ALEX_027"},
                {"name": "Blake White", "role": "Forklift Operator", "qr_code": "QR_BLAKE_028"},
                {"name": "Casey Johnson", "role": "Assembly Line Worker", "qr_code": "QR_CASEY_029"},
                {"name": "Drew Davis", "role": "Machine Operator", "qr_code": "QR_DREW_030"}
            ]
            
            created_users = []
            
            for worker_data in factory_workers:
                try:
                    user = UserService.create(
                        name=worker_data["name"],
                        qr_code=worker_data["qr_code"]
                    )
                    created_users.append(user)
                    self.log_success(f"Created user: {user.name} ({worker_data['role']})")
                    
                except Exception as e:
                    self.log_error(f"Failed to create user {worker_data['name']}: {e}")
            
            self.commit()
            
            self.log_info(f"Successfully created {len(created_users)} factory workers")
            self.log_info("Users include various roles: supervisors, operators, inspectors, technicians, etc.")
            
            return True
            
        except Exception as e:
            self.log_error(f"User seeding failed: {e}")
            self.rollback()
            return False
    
    def get_sample_users(self) -> List[User]:
        """Get a sample of created users for use by other seeders"""
        return UserService.get_all()
    
    def get_user_by_role(self, role_keyword: str) -> List[User]:
        """Get users by role keyword"""
        all_users = UserService.get_all()
        return [user for user in all_users if role_keyword.lower() in user.name.lower()]
    
    def get_random_user(self) -> User:
        """Get a random user for testing"""
        all_users = UserService.get_all()
        return random.choice(all_users) if all_users else None
