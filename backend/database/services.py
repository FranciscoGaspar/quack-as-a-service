"""Database service layer for Quack as a Service - Basic CRUD Operations"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import desc
from .connection import create_session
from .models import User, PersonalEntry, RoomEquipmentConfiguration

class UserService:
    """Basic CRUD operations for users"""
    
    @staticmethod
    def create(name: str, qr_code: str = None) -> User:
        """Create a new user"""
        session = create_session()
        try:
            user = User(name=name, qr_code=qr_code)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        session = create_session()
        try:
            return session.query(User).get(user_id)
        finally:
            session.close()
    
    @staticmethod
    def get_by_qr_code(qr_code: str) -> Optional[User]:
        """Get user by QR code"""
        session = create_session()
        try:
            return session.query(User).filter_by(qr_code=qr_code).first()
        finally:
            session.close()
    
    @staticmethod
    def get_all() -> List[User]:
        """Get all users"""
        session = create_session()
        try:
            return session.query(User).order_by(User.name).all()
        finally:
            session.close()
    
    @staticmethod
    def update(user_id: int, name: str = None, qr_code: str = None) -> Optional[User]:
        """Update user information"""
        session = create_session()
        try:
            user = session.query(User).get(user_id)
            if user:
                if name:
                    user.name = name
                if qr_code is not None:
                    user.qr_code = qr_code
                user.updated_at = datetime.now(timezone.utc)
                session.commit()
                session.refresh(user)
            return user
        finally:
            session.close()
    
    @staticmethod
    def delete(user_id: int) -> bool:
        """Delete a user and all their entries"""
        session = create_session()
        try:
            user = session.query(User).get(user_id)
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        finally:
            session.close()

class PersonalEntryService:
    """Basic CRUD operations for personal entries"""
    
    @staticmethod
    def create(user_id: int, room_name: str, equipment: Dict[str, bool] = None, 
               image_url: str = None, calculate_approval: bool = True) -> PersonalEntry:
        """Create a new personal entry"""
        session = create_session()
        try:
            entry = PersonalEntry(
                user_id=user_id,
                room_name=room_name,
                image_url=image_url,
                equipment=equipment or {}
            )
            session.add(entry)
            
            # Calculate approval status if requested
            if calculate_approval:
                entry.calculate_and_set_approval_status()
            
            session.commit()
            session.refresh(entry)
            return entry
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(entry_id: int) -> Optional[PersonalEntry]:
        """Get entry by ID"""
        session = create_session()
        try:
            return session.query(PersonalEntry).get(entry_id)
        finally:
            session.close()
    
    @staticmethod
    def get_all(limit: int = None) -> List[PersonalEntry]:
        """Get all entries, optionally limited"""
        session = create_session()
        try:
            query = session.query(PersonalEntry).order_by(desc(PersonalEntry.entered_at))
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()
    
    @staticmethod
    def get_by_user(user_id: int, limit: int = None) -> List[PersonalEntry]:
        """Get all entries for a specific user"""
        session = create_session()
        try:
            query = session.query(PersonalEntry).filter_by(user_id=user_id).order_by(desc(PersonalEntry.entered_at))
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()
    
    @staticmethod
    def get_by_room(room_name: str, limit: int = None) -> List[PersonalEntry]:
        """Get all entries for a specific room"""
        session = create_session()
        try:
            query = session.query(PersonalEntry).filter_by(room_name=room_name).order_by(desc(PersonalEntry.entered_at))
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()
    
    @staticmethod
    def update(entry_id: int, room_name: str = None, equipment: Dict[str, bool] = None, 
               image_url: str = None) -> Optional[PersonalEntry]:
        """Update entry information"""
        session = create_session()
        try:
            entry = session.query(PersonalEntry).get(entry_id)
            if entry:
                if room_name:
                    entry.room_name = room_name
                if equipment is not None:
                    entry.equipment = equipment
                if image_url is not None:
                    entry.image_url = image_url
                session.commit()
                session.refresh(entry)
            return entry
        finally:
            session.close()
    
    @staticmethod
    def update_equipment(entry_id: int, **equipment_status) -> Optional[PersonalEntry]:
        """Update specific equipment items"""
        session = create_session()
        try:
            entry = session.query(PersonalEntry).get(entry_id)
            if entry:
                entry.set_equipment_status(**equipment_status)
                session.commit()
                session.refresh(entry)
            return entry
        finally:
            session.close()
    
    @staticmethod
    def delete(entry_id: int) -> bool:
        """Delete an entry"""
        session = create_session()
        try:
            entry = session.query(PersonalEntry).get(entry_id)
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    @staticmethod
    def recalculate_approval_status(entry_id: int) -> Optional[PersonalEntry]:
        """Recalculate approval status for an existing entry"""
        session = create_session()
        try:
            entry = session.query(PersonalEntry).get(entry_id)
            if entry:
                entry.calculate_and_set_approval_status()
                session.commit()
                session.refresh(entry)
            return entry
        finally:
            session.close()


class RoomEquipmentConfigurationService:
    """Service for managing room equipment configurations"""
    
    @staticmethod
    def create(room_name: str, equipment_weights: Dict[str, float], 
               entry_threshold: float = 70.0, description: str = None) -> RoomEquipmentConfiguration:
        """Create a new room equipment configuration"""
        session = create_session()
        try:
            config = RoomEquipmentConfiguration(
                room_name=room_name,
                equipment_weights=equipment_weights,
                entry_threshold=entry_threshold,
                description=description
            )
            session.add(config)
            session.commit()
            session.refresh(config)
            return config
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(config_id: int) -> Optional[RoomEquipmentConfiguration]:
        """Get configuration by ID"""
        session = create_session()
        try:
            return session.query(RoomEquipmentConfiguration).get(config_id)
        finally:
            session.close()
    
    @staticmethod
    def get_by_room_name(room_name: str) -> Optional[RoomEquipmentConfiguration]:
        """Get configuration by room name"""
        session = create_session()
        try:
            return session.query(RoomEquipmentConfiguration).filter_by(
                room_name=room_name, is_active=True
            ).first()
        finally:
            session.close()
    
    @staticmethod
    def get_all(include_inactive: bool = False) -> List[RoomEquipmentConfiguration]:
        """Get all configurations"""
        session = create_session()
        try:
            query = session.query(RoomEquipmentConfiguration)
            if not include_inactive:
                query = query.filter_by(is_active=True)
            return query.order_by(RoomEquipmentConfiguration.room_name).all()
        finally:
            session.close()
    
    @staticmethod
    def update(config_id: int, equipment_weights: Dict[str, float] = None,
               entry_threshold: float = None, description: str = None,
               is_active: bool = None) -> Optional[RoomEquipmentConfiguration]:
        """Update room configuration"""
        session = create_session()
        try:
            config = session.query(RoomEquipmentConfiguration).get(config_id)
            if config:
                if equipment_weights is not None:
                    config.equipment_weights = equipment_weights
                if entry_threshold is not None:
                    config.entry_threshold = entry_threshold
                if description is not None:
                    config.description = description
                if is_active is not None:
                    config.is_active = is_active
                config.updated_at = datetime.now(timezone.utc)
                session.commit()
                session.refresh(config)
            return config
        finally:
            session.close()
    
    @staticmethod
    def delete(config_id: int) -> bool:
        """Delete a room configuration"""
        session = create_session()
        try:
            config = session.query(RoomEquipmentConfiguration).get(config_id)
            if config:
                session.delete(config)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    @staticmethod
    def create_default_configurations():
        """Create default configurations for existing rooms"""
        default_configs = [
            {
                "room_name": "production-floor",
                "equipment_weights": {"mask": "required", "gloves": "required", "hairnet": "recommended"},
                "entry_threshold": 5.0,  # Allow entry if all required items present (even without recommended)
                "description": "Production Floor - Mask & gloves REQUIRED, hairnet recommended"
            },
            {
                "room_name": "assembly-line", 
                "equipment_weights": {"gloves": "required", "hairnet": "recommended"},
                "entry_threshold": 5.0,  # Allow entry with gloves (hairnet recommended)
                "description": "Assembly Line - Gloves REQUIRED, hairnet recommended"
            },
            {
                "room_name": "packaging-area",
                "equipment_weights": {"gloves": "required"},
                "entry_threshold": 5.0,  # Need gloves only
                "description": "Packaging Area - Gloves REQUIRED"
            }
        ]
        
        created_configs = []
        for config_data in default_configs:
            # Check if config already exists
            existing = RoomEquipmentConfigurationService.get_by_room_name(config_data["room_name"])
            if not existing:
                config = RoomEquipmentConfigurationService.create(**config_data)
                created_configs.append(config)
        
        return created_configs