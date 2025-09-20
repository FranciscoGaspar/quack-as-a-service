#!/usr/bin/env python3
"""
Emotional Analysis seeder for creating realistic AWS Rekognition emotional analysis data.
"""

import sys
import os
from typing import List, Dict, Any
import random
from datetime import datetime, timezone

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_dir)

from database.connection import create_session
from database.models import EmotionalAnalysis, PersonalEntry
from database.services import PersonalEntryService
from .base_seeder import BaseSeeder, random_emotion_data, random_recommendations


class EmotionalAnalysisSeeder(BaseSeeder):
    """Seeder for EmotionalAnalysis model"""
    
    def get_seeder_name(self) -> str:
        return "Emotional Analysis Seeder"
    
    def seed(self) -> bool:
        """Seed emotional analyses with realistic AWS Rekognition data"""
        try:
            # Check if emotional analyses already exist
            if self.check_data_exists(EmotionalAnalysis):
                self.log_skip(f"Emotional analyses already exist - skipping creation")
                return True
            
            # Get personal entries to analyze
            entries = PersonalEntryService.get_all()
            
            if not entries:
                self.log_error("No personal entries found - run PersonalEntrySeeder first")
                return False
            
            self.log_info("Creating emotional analyses with AWS Rekognition-like data...")
            
            # Select exactly 50 entries for emotional analysis
            entries_to_analyze = random.sample(entries, min(len(entries), 50))  # Analyze exactly 50 entries
            
            created_analyses = []
            
            for entry in entries_to_analyze:
                try:
                    # Generate realistic emotional analysis data
                    emotion_data = random_emotion_data()
                    recommendations = random_recommendations()
                    
                    # Create emotional analysis record
                    analysis = EmotionalAnalysis(
                        personal_entry_id=entry.id,
                        faces_detected=emotion_data['faces_detected'],
                        dominant_emotion=emotion_data['dominant_emotion'],
                        overall_confidence=emotion_data['overall_confidence'],
                        image_quality=emotion_data['image_quality'],
                        analysis_data=emotion_data,
                        recommendations=recommendations,
                        analyzed_at=entry.entered_at,  # Analysis happens at entry time
                        created_at=datetime.now(timezone.utc)
                    )
                    
                    session = create_session()
                    try:
                        session.add(analysis)
                        session.commit()
                        session.refresh(analysis)
                        created_analyses.append(analysis)
                        
                        self.log_success(f"Created analysis for entry {entry.id}: {analysis.dominant_emotion} ({analysis.overall_confidence:.1%} confidence)")
                        
                    finally:
                        session.close()
                    
                except Exception as e:
                    self.log_error(f"Failed to create emotional analysis for entry {entry.id}: {e}")
            
            self.log_info(f"Successfully created {len(created_analyses)} emotional analyses")
            self.log_info("Analyses include various emotions: HAPPY, SAD, ANGRY, SURPRISED, DISGUSTED, FEAR, CALM, CONFUSED")
            self.log_info("Each analysis includes face detection, emotion confidence scores, image quality assessment, and recommendations")
            
            return True
            
        except Exception as e:
            self.log_error(f"Emotional analysis seeding failed: {e}")
            return False
    
    def get_sample_analyses(self) -> List[EmotionalAnalysis]:
        """Get a sample of created analyses for use by other seeders"""
        session = create_session()
        try:
            return session.query(EmotionalAnalysis).limit(20).all()
        finally:
            session.close()
    
    def get_analyses_by_emotion(self, emotion: str) -> List[EmotionalAnalysis]:
        """Get analyses by dominant emotion"""
        session = create_session()
        try:
            return session.query(EmotionalAnalysis).filter_by(dominant_emotion=emotion.upper()).all()
        finally:
            session.close()
    
    def get_high_confidence_analyses(self, min_confidence: float = 0.8) -> List[EmotionalAnalysis]:
        """Get analyses with high confidence scores"""
        session = create_session()
        try:
            return session.query(EmotionalAnalysis).filter(
                EmotionalAnalysis.overall_confidence >= min_confidence
            ).all()
        finally:
            session.close()
    
    def get_low_confidence_analyses(self, max_confidence: float = 0.6) -> List[EmotionalAnalysis]:
        """Get analyses with low confidence scores"""
        session = create_session()
        try:
            return session.query(EmotionalAnalysis).filter(
                EmotionalAnalysis.overall_confidence <= max_confidence
            ).all()
        finally:
            session.close()
    
    def get_analyses_by_image_quality(self, quality: str) -> List[EmotionalAnalysis]:
        """Get analyses by image quality"""
        session = create_session()
        try:
            return session.query(EmotionalAnalysis).filter_by(image_quality=quality).all()
        finally:
            session.close()
    
    def get_analyses_with_recommendations(self) -> List[EmotionalAnalysis]:
        """Get analyses that have recommendations"""
        session = create_session()
        try:
            return session.query(EmotionalAnalysis).filter(
                EmotionalAnalysis.recommendations.isnot(None)
            ).all()
        finally:
            session.close()
    
    def get_emotion_statistics(self) -> Dict[str, int]:
        """Get statistics about emotions detected"""
        session = create_session()
        try:
            analyses = session.query(EmotionalAnalysis).all()
            emotion_counts = {}
            
            for analysis in analyses:
                emotion = analysis.dominant_emotion
                if emotion:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            return emotion_counts
        finally:
            session.close()
    
    def get_confidence_statistics(self) -> Dict[str, float]:
        """Get statistics about confidence scores"""
        session = create_session()
        try:
            analyses = session.query(EmotionalAnalysis).filter(
                EmotionalAnalysis.overall_confidence.isnot(None)
            ).all()
            
            if not analyses:
                return {}
            
            confidences = [analysis.overall_confidence for analysis in analyses]
            
            return {
                'average': sum(confidences) / len(confidences),
                'min': min(confidences),
                'max': max(confidences),
                'count': len(confidences)
            }
        finally:
            session.close()
    
    def get_image_quality_statistics(self) -> Dict[str, int]:
        """Get statistics about image quality"""
        session = create_session()
        try:
            analyses = session.query(EmotionalAnalysis).all()
            quality_counts = {}
            
            for analysis in analyses:
                quality = analysis.image_quality
                if quality:
                    quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            return quality_counts
        finally:
            session.close()
