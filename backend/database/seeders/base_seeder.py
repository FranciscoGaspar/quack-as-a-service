#!/usr/bin/env python3
"""
Base seeder class for database seeding operations.
Provides common functionality for all seeders.
"""

import sys
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import random

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_dir)

from database.connection import create_session


class BaseSeeder(ABC):
    """Base class for all database seeders"""
    
    def __init__(self):
        self.session = None
        self.created_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    def __enter__(self):
        """Context manager entry"""
        self.session = create_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            self.session.close()
    
    @abstractmethod
    def seed(self) -> bool:
        """Main seeding method - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_seeder_name(self) -> str:
        """Get the name of this seeder"""
        pass
    
    def log_info(self, message: str):
        """Log info message"""
        print(f"   ℹ️  {message}")
    
    def log_success(self, message: str):
        """Log success message"""
        print(f"   ✅ {message}")
        self.created_count += 1
    
    def log_skip(self, message: str):
        """Log skip message"""
        print(f"   ⏭️  {message}")
        self.skipped_count += 1
    
    def log_error(self, message: str):
        """Log error message"""
        print(f"   ❌ {message}")
        self.error_count += 1
    
    def commit(self):
        """Commit the current transaction"""
        if self.session:
            self.session.commit()
    
    def rollback(self):
        """Rollback the current transaction"""
        if self.session:
            self.session.rollback()
    
    def get_summary(self) -> Dict[str, int]:
        """Get seeding summary"""
        return {
            'created': self.created_count,
            'skipped': self.skipped_count,
            'errors': self.error_count
        }
    
    def check_data_exists(self, model_class) -> bool:
        """Check if data already exists for a model"""
        if self.session:
            count = self.session.query(model_class).count()
            return count > 0
        return False
    
    def clear_model_data(self, model_class, model_name: str = None) -> bool:
        """Clear all data for a specific model"""
        if not model_name:
            model_name = model_class.__name__
        
        try:
            if self.session:
                count = self.session.query(model_class).count()
                if count > 0:
                    self.log_info(f"Clearing {count} {model_name} records...")
                    self.session.query(model_class).delete()
                    self.log_success(f"Cleared {count} {model_name} records")
                    return True
                else:
                    self.log_skip(f"No {model_name} records to clear")
                    return True
        except Exception as e:
            self.log_error(f"Failed to clear {model_name} records: {e}")
            return False


class SeederRunner:
    """Runs multiple seeders in sequence"""
    
    def __init__(self):
        self.seeders: List[BaseSeeder] = []
        self.results: Dict[str, Dict[str, int]] = {}
    
    def add_seeder(self, seeder: BaseSeeder):
        """Add a seeder to the runner"""
        self.seeders.append(seeder)
    
    def run_all(self, force: bool = False) -> bool:
        """Run all seeders"""
        print("🌱 Starting database seeding...")
        print("=" * 60)
        
        total_created = 0
        total_skipped = 0
        total_errors = 0
        
        for seeder in self.seeders:
            print(f"\n🚀 Running {seeder.get_seeder_name()}...")
            
            try:
                with seeder as s:
                    success = s.seed()
                    if success:
                        summary = s.get_summary()
                        self.results[seeder.get_seeder_name()] = summary
                        
                        total_created += summary['created']
                        total_skipped += summary['skipped']
                        total_errors += summary['errors']
                        
                        print(f"   ✅ {seeder.get_seeder_name()} completed")
                    else:
                        print(f"   ❌ {seeder.get_seeder_name()} failed")
                        total_errors += 1
                        
            except Exception as e:
                print(f"   ❌ {seeder.get_seeder_name()} failed with error: {e}")
                total_errors += 1
        
        print("\n" + "=" * 60)
        print("📊 Seeding Summary:")
        print(f"   Created: {total_created}")
        print(f"   Skipped: {total_skipped}")
        print(f"   Errors:  {total_errors}")
        
        if total_errors == 0:
            print("\n🎉 All seeders completed successfully!")
            return True
        else:
            print(f"\n⚠️  {total_errors} seeder(s) had errors")
            return False
    
    def get_results(self) -> Dict[str, Dict[str, int]]:
        """Get detailed results from all seeders"""
        return self.results


# Utility functions for generating realistic test data
def random_date_in_range(days_back: int = 30) -> datetime:
    """Generate a random datetime within the last N days"""
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days_back)
    random_days = random.randint(0, days_back)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    
    return start_date + timedelta(
        days=random_days,
        hours=random_hours,
        minutes=random_minutes
    )


def random_equipment_detection() -> Dict[str, bool]:
    """Generate random equipment detection results"""
    equipment_types = ['mask', 'gloves', 'hairnet']
    
    # Generate realistic equipment detection patterns
    equipment = {}
    
    # Mask detection (70% chance)
    equipment['mask'] = random.random() < 0.86
    
    # Gloves detection (80% chance for both)
    equipment['gloves'] = random.random() < 0.70
    
    # Hairnet detection (60% chance)
    equipment['hairnet'] = random.random() < 0.88
    
    
    return equipment


def random_emotion_data() -> Dict[str, Any]:
    """Generate random emotional analysis data"""
    emotions = ['HAPPY', 'SAD', 'DISGUSTED', 'FEAR', 'CALM']
    image_qualities = ['excellent', 'good', 'fair', 'poor', 'unknown']
    
    dominant_emotion = random.choice(emotions)
    confidence = random.uniform(75, 100)
    image_quality = random.choice(image_qualities)
    faces_detected = 1
    
    # Generate face analysis data
    face_analyses = []
    for i in range(faces_detected):
        face_emotions = []
        for emotion in emotions:
            face_emotions.append({
                'emotion': emotion,
                'confidence': random.uniform(75, 100),
                'label': emotion
            })
        
        face_analysis = {
            'face_id': f"face_{i+1}",
            'emotions': face_emotions,
            'bounding_box': {
                'Width': random.uniform(0.1, 0.3),
                'Height': random.uniform(0.1, 0.3),
                'Left': random.uniform(0.1, 0.6),
                'Top': random.uniform(0.1, 0.6)
            },
            'quality': {
                'Brightness': random.uniform(0.1, 1.0),
                'Sharpness': random.uniform(0.1, 1.0)
            },
            'pose': {
                'Roll': random.uniform(-30, 30),
                'Yaw': random.uniform(-30, 30),
                'Pitch': random.uniform(-30, 30)
            },
            'age_range': {
                'Low': random.randint(20, 40),
                'High': random.randint(40, 60)
            },
            'gender': {
                'Value': random.choice(['Male', 'Female']),
                'Confidence': random.uniform(75, 100)
            }
        }
        face_analyses.append(face_analysis)
    
    return {
        'faces_detected': faces_detected,
        'dominant_emotion': dominant_emotion,
        'overall_confidence': confidence,
        'image_quality': image_quality,
        'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
        'face_analyses': face_analyses
    }


def random_recommendations() -> List[str]:
    """Generate random recommendations based on emotional analysis"""
    all_recommendations = [
        "Consider providing stress management resources",
        "Schedule a wellness check-in",
        "Review workload distribution",
        "Provide additional training support",
        "Consider team building activities",
        "Review safety protocols",
        "Provide emotional support resources",
        "Schedule regular breaks",
        "Consider workload adjustments",
        "Provide positive reinforcement"
    ]
    
    # Return 1-3 random recommendations
    num_recommendations = random.randint(1, 3)
    return random.sample(all_recommendations, num_recommendations)
