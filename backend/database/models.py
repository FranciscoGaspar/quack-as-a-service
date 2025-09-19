"""Database models for Quack as a Service"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .connection import Base

class User(Base):
    """User model for people using the system"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    personal_entries = relationship("PersonalEntry", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PersonalEntry(Base):
    """Personal entry tracking security equipment when entering rooms"""
    __tablename__ = 'personal_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    room_name = Column(String(100), nullable=False)
    image_url = Column(String(500), nullable=True)
    equipment = Column(JSONB, nullable=False, default=lambda: {})
    entered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="personal_entries")
    
    def __repr__(self):
        return f'<PersonalEntry {self.id}: User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_name': self.room_name,
            'image_url': self.image_url,
            'equipment': self.equipment,
            'entered_at': self.entered_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None
        }
    
    def set_equipment_status(self, **equipment_status):
        """
        Set equipment status with validation
        Example: set_equipment_status(mask=True, right_glove=True, left_glove=False)
        """
        if not self.equipment:
            self.equipment = {}
        
        valid_equipment = {
            'mask', 'right_glove', 'left_glove', 'hairnet', 
            'safety_glasses', 'hard_hat', 'safety_vest', 'boots'
        }
        
        for equipment_name, status in equipment_status.items():
            if equipment_name in valid_equipment:
                self.equipment[equipment_name] = bool(status)
        
        # Mark the JSONB column as modified for SQLAlchemy
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(self, 'equipment')
    
    def get_missing_equipment(self):
        """Get list of equipment that is False or missing"""
        if not self.equipment:
            return []
        
        return [item for item, status in self.equipment.items() if not status]
    
    def get_present_equipment(self):
        """Get list of equipment that is True"""
        if not self.equipment:
            return []
        
        return [item for item, status in self.equipment.items() if status]
    
    def is_compliant(self, required_equipment=None):
        """
        Check if entry is compliant with required equipment
        Default required: mask, gloves (both), hairnet
        """
        if required_equipment is None:
            required_equipment = ['mask', 'right_glove', 'left_glove', 'hairnet']
        
        if not self.equipment:
            return False
        
        return all(self.equipment.get(item, False) for item in required_equipment)
