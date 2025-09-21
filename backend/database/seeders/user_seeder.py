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
                {"name": "Alice Johnson", "role": "Production Supervisor", "qr_code": null},
                {"name": "Bob Smith", "role": "Assembly Line Worker", "qr_code": null},
                {"name": "Carol Davis", "role": "Quality Inspector", "qr_code": null},
                {"name": "David Wilson", "role": "Machine Operator", "qr_code": null},
                {"name": "Eva Martinez", "role": "Packaging Specialist", "qr_code": null},
                {"name": "Frank Brown", "role": "Maintenance Technician", "qr_code": null},
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
