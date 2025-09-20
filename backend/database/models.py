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
    qr_code = Column(String(255), nullable=True, unique=True)  # Unique QR code for each user
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
            'qr_code': self.qr_code,
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
        If no required_equipment is provided, use room-specific requirements
        """
        if required_equipment is None:
            # Import here to avoid circular imports
            from core.room_equipment_config import RoomEquipmentConfig
            return RoomEquipmentConfig.is_compliant(self.room_name, self.equipment or {})
        
        if not self.equipment:
            return False
        
        # Handle different glove detection formats for legacy compatibility
        equipment_copy = self.equipment.copy()
        if "gloves" in required_equipment and "gloves" not in equipment_copy:
            left_glove = equipment_copy.get("left_glove", False)
            right_glove = equipment_copy.get("right_glove", False)
            equipment_copy["gloves"] = left_glove and right_glove
        
        return all(equipment_copy.get(item, False) for item in required_equipment)
