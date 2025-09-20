"""Database models for Quack as a Service"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
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


class RoomEquipmentConfiguration(Base):
    """Room equipment configuration with weights and thresholds"""
    __tablename__ = 'room_equipment_configurations'
    
    id = Column(Integer, primary_key=True)
    room_name = Column(String(100), nullable=False, unique=True)
    equipment_weights = Column(JSONB, nullable=False, default=lambda: {})  # {"mask": "required", "gloves": "recommended", "hairnet": "required"}
    entry_threshold = Column(Float, nullable=False, default=70.0)  # Minimum score required for entry
    is_active = Column(Boolean, nullable=False, default=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<RoomEquipmentConfig {self.room_name}: threshold={self.entry_threshold}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_name': self.room_name,
            'equipment_weights': self.equipment_weights,
            'entry_threshold': self.entry_threshold,
            'is_active': self.is_active,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def calculate_equipment_score(self, detected_equipment: dict) -> float:
        """
        Calculate equipment compliance score based on requirement levels
        
        Args:
            detected_equipment: Dict of equipment -> detected status (e.g., {"mask": True, "gloves": False})
            
        Returns:
            Float score (0-10): 10 = all required present, 5-9 = missing recommended, 0-4 = missing required
        """
        if not self.equipment_weights or not detected_equipment:
            return 0.0
        
        required_items = [eq for eq, level in self.equipment_weights.items() if level == "required"]
        recommended_items = [eq for eq, level in self.equipment_weights.items() if level == "recommended"]
        
        # Check required items (critical for entry)
        required_present = sum(1 for eq in required_items if detected_equipment.get(eq, False))
        required_missing = len(required_items) - required_present
        
        # Check recommended items (nice to have)
        recommended_present = sum(1 for eq in recommended_items if detected_equipment.get(eq, False))
        
        # Scoring logic:
        if required_missing > 0:
            # Missing required items = low score (0-4)
            return max(0, 4 - required_missing * 2)
        else:
            # All required present, score based on recommended (5-10)
            if len(recommended_items) == 0:
                return 10.0  # No recommended items, perfect score
            else:
                recommended_ratio = recommended_present / len(recommended_items)
                return 5.0 + (recommended_ratio * 5.0)  # 5-10 based on recommended compliance
    
    def is_entry_approved(self, detected_equipment: dict) -> bool:
        """
        Determine if entry should be approved based on equipment score and threshold
        
        Args:
            detected_equipment: Dict of equipment -> detected status
            
        Returns:
            Boolean indicating if entry is approved
        """
        score = self.calculate_equipment_score(detected_equipment)
        return score >= self.entry_threshold


class EmotionalAnalysis(Base):
    """Emotional analysis results from AWS Rekognition"""
    __tablename__ = 'emotional_analyses'
    
    id = Column(Integer, primary_key=True)
    personal_entry_id = Column(Integer, ForeignKey('personal_entries.id'), nullable=False, unique=True)
    
    # Analysis metadata
    faces_detected = Column(Integer, nullable=False, default=0)
    dominant_emotion = Column(String(50), nullable=True)
    overall_confidence = Column(Float, nullable=True)
    image_quality = Column(String(20), nullable=True)  # excellent, good, fair, poor, unknown
    
    # Complete analysis results
    analysis_data = Column(JSONB, nullable=True)  # Store complete Rekognition response
    recommendations = Column(JSONB, nullable=True)  # Store recommendations array
    
    # Timestamps
    analyzed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    personal_entry = relationship("PersonalEntry", back_populates="emotional_analysis")
    
    def __repr__(self):
        return f'<EmotionalAnalysis {self.id}: Entry {self.personal_entry_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'personal_entry_id': self.personal_entry_id,
            'faces_detected': self.faces_detected,
            'dominant_emotion': self.dominant_emotion,
            'overall_confidence': self.overall_confidence,
            'image_quality': self.image_quality,
            'analysis_data': self.analysis_data,
            'recommendations': self.recommendations,
            'analyzed_at': self.analyzed_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def set_analysis_results(self, analysis_result):
        """
        Set emotional analysis results from Rekognition analysis
        
        Args:
            analysis_result: EmotionalAnalysisResponse object from rekognition_emotions service
        """
        # Set basic fields
        self.faces_detected = analysis_result.faces_detected
        self.dominant_emotion = analysis_result.dominant_emotion
        self.overall_confidence = analysis_result.overall_confidence
        self.image_quality = analysis_result.image_quality
        
        # Store complete analysis data
        self.analysis_data = {
            'faces_detected': analysis_result.faces_detected,
            'dominant_emotion': analysis_result.dominant_emotion,
            'overall_confidence': analysis_result.overall_confidence,
            'image_quality': analysis_result.image_quality,
            'analysis_timestamp': analysis_result.analysis_timestamp.isoformat(),
            'face_analyses': [
                {
                    'face_id': face.face_id,
                    'emotions': [
                        {
                            'emotion': emotion.emotion,
                            'confidence': emotion.confidence,
                            'label': emotion.emotion
                        }
                        for emotion in face.emotions
                    ],
                    'bounding_box': face.bounding_box,
                    'quality': face.quality,
                    'pose': face.pose,
                    'age_range': face.age_range,
                    'gender': face.gender
                }
                for face in analysis_result.face_analyses
            ]
        }
        
        # Store recommendations
        self.recommendations = analysis_result.recommendations
        
        # Mark JSONB columns as modified for SQLAlchemy
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(self, 'analysis_data')
        flag_modified(self, 'recommendations')


class PersonalEntry(Base):
    """Personal entry tracking security equipment when entering rooms"""
    __tablename__ = 'personal_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    room_name = Column(String(100), nullable=False)
    image_url = Column(String(500), nullable=True)
    equipment = Column(JSONB, nullable=False, default=lambda: {})
    # New approval fields
    is_approved = Column(Boolean, nullable=True)  # True=approved, False=denied, None=pending
    equipment_score = Column(Float, nullable=True)  # Calculated equipment compliance score
    approval_reason = Column(String(500), nullable=True)  # Reason for approval/denial
    entered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="personal_entries")
    emotional_analysis = relationship("EmotionalAnalysis", back_populates="personal_entry", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<PersonalEntry {self.id}: User {self.user_id}>'
    
    def to_dict(self):
        # Safely handle emotional_analysis relationship to avoid DetachedInstanceError
        emotional_analysis_data = None
        try:
            if self.emotional_analysis:
                emotional_analysis_data = self.emotional_analysis.to_dict()
        except Exception:
            # If we can't access emotional_analysis (e.g., DetachedInstanceError), set to None
            emotional_analysis_data = None
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_name': self.room_name,
            'image_url': self.image_url,
            'equipment': self.equipment,
            'is_approved': self.is_approved,
            'equipment_score': self.equipment_score,
            'approval_reason': self.approval_reason,
            'entered_at': self.entered_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None,
            'emotional_analysis': emotional_analysis_data
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
    
    def calculate_and_set_approval_status(self):
        """
        Calculate approval status based on room configuration and update the entry
        Returns tuple of (is_approved, score, reason)
        """
        # Import here to avoid circular imports
        from database.services import RoomEquipmentConfigurationService
        
        room_config = RoomEquipmentConfigurationService.get_by_room_name(self.room_name)
        
        if not room_config or not room_config.is_active:
            # Fallback to legacy compliance check if no room config exists
            is_compliant = self.is_compliant()
            self.is_approved = is_compliant
            self.equipment_score = 100.0 if is_compliant else 0.0
            self.approval_reason = "Legacy compliance check - no room configuration found"
            return self.is_approved, self.equipment_score, self.approval_reason
        
        # Calculate score based on room configuration
        score = room_config.calculate_equipment_score(self.equipment or {})
        is_approved = room_config.is_entry_approved(self.equipment or {})
        
        # Generate approval reason
        if is_approved:
            reason = f"Entry approved - Score: {score:.1f}% (threshold: {room_config.entry_threshold}%)"
        else:
            reason = f"Entry denied - Score: {score:.1f}% below threshold: {room_config.entry_threshold}%"
        
        # Update the entry
        self.is_approved = is_approved
        self.equipment_score = score
        self.approval_reason = reason
        
        return is_approved, score, reason
    
    def get_approval_status_display(self) -> str:
        """Get human-readable approval status"""
        if self.is_approved is None:
            return "Pending Review"
        elif self.is_approved:
            return "Approved"
        else:
            return "Denied"
    
    def get_approval_badge_color(self) -> str:
        """Get color for approval status badge"""
        if self.is_approved is None:
            return "yellow"  # Pending
        elif self.is_approved:
            return "green"   # Approved
        else:
            return "red"     # Denied
