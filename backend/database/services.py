"""Database service layer for Quack as a Service - Basic CRUD Operations"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import desc
from .connection import create_session
from .models import User, PersonalEntry

class UserService:
    """Basic CRUD operations for users"""
    
    @staticmethod
    def create(name: str) -> User:
        """Create a new user"""
        session = create_session()
        try:
            user = User(name=name)
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
    def get_all() -> List[User]:
        """Get all users"""
        session = create_session()
        try:
            return session.query(User).order_by(User.name).all()
        finally:
            session.close()
    
    @staticmethod
    def update(user_id: int, name: str = None) -> Optional[User]:
        """Update user information"""
        session = create_session()
        try:
            user = session.query(User).get(user_id)
            if user:
                if name:
                    user.name = name
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
               image_url: str = None) -> PersonalEntry:
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