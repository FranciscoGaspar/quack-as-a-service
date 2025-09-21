#!/usr/bin/env python3
"""
Custom database seeder script for Quack as a Service.

This script allows you to specify exactly how many objects to create for each model.
Useful for testing with different data sizes or creating specific scenarios.

Usage:
    python seed_custom.py                          # Use default counts
    python seed_custom.py --users 10               # Create 10 users
    python seed_custom.py --users 5 --entries 20   # Create 5 users, 20 entries
    python seed_custom.py --all 100                # Create 100 of each model
    python seed_custom.py --clean                  # Clean database first
    python seed_custom.py --status                 # Show current status
"""

import sys
import os
import argparse
import random
from datetime import datetime, timezone
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database.connection import create_session
from database.models import User, PersonalEntry, RoomEquipmentConfiguration, EmotionalAnalysis
from database.seeders.base_seeder import SeederRunner
from database.seeders.user_seeder import UserSeeder
from database.seeders.room_configuration_seeder import RoomEquipmentConfigurationSeeder
from database.seeders.personal_entry_seeder import PersonalEntrySeeder
from database.seeders.emotional_analysis_seeder import EmotionalAnalysisSeeder


def show_database_status():
    """Show current database status"""
    print("📊 Database Status")
    print("=" * 50)
    
    session = create_session()
    try:
        # Count records in each table
        user_count = session.query(User).count()
        room_config_count = session.query(RoomEquipmentConfiguration).count()
        entry_count = session.query(PersonalEntry).count()
        emotion_count = session.query(EmotionalAnalysis).count()
        
        print(f"Users:                    {user_count:4d}")
        print(f"Room Configurations:      {room_config_count:4d}")
        print(f"Personal Entries:        {entry_count:4d}")
        print(f"Emotional Analyses:      {emotion_count:4d}")
        
        print("\n📈 Summary:")
        total_records = user_count + room_config_count + entry_count + emotion_count
        
        if total_records == 0:
            print("   Database is empty")
        elif total_records < 50:
            print("   Database has minimal data")
        elif total_records < 150:
            print("   Database has moderate data")
        else:
            print("   Database is well populated")
        
    finally:
        session.close()


def clean_database():
    """Clean all data from the database"""
    print("🗑️  Cleaning database...")
    
    session = create_session()
    try:
        # Delete in reverse dependency order
        session.query(EmotionalAnalysis).delete()
        session.query(PersonalEntry).delete()
        session.query(RoomEquipmentConfiguration).delete()
        session.query(User).delete()
        
        # Clear migration history if it exists
        try:
            from database.migrate import MigrationHistory
            session.query(MigrationHistory).delete()
        except Exception:
            pass
        
        session.commit()
        print("✅ Database cleaned successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        session.rollback()
        return False
    finally:
        session.close()


class CustomUserSeeder(UserSeeder):
    """Custom user seeder with configurable count"""
    
    def __init__(self, count=30):
        super().__init__()
        self.target_count = count
    
    def seed(self) -> bool:
        """Seed users with specified count"""
        try:
            # Check if users already exist
            if self.check_data_exists(User):
                self.log_skip(f"Users already exist - skipping user creation")
                return True
            
            self.log_info(f"Creating {self.target_count} factory worker users...")
            
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
                {"name": "Drew Davis", "role": "Machine Operator", "qr_code": "QR_DREW_030"},
                {"name": "Emma Wilson", "role": "Quality Inspector", "qr_code": "QR_EMMA_031"},
                {"name": "Felix Brown", "role": "Packaging Specialist", "qr_code": "QR_FELIX_032"},
                {"name": "Gina Lee", "role": "Safety Coordinator", "qr_code": "QR_GINA_033"},
                {"name": "Hugo Taylor", "role": "Warehouse Worker", "qr_code": "QR_HUGO_034"},
                {"name": "Ivy Garcia", "role": "Production Manager", "qr_code": "QR_IVY_035"},
                {"name": "Jake Anderson", "role": "Forklift Operator", "qr_code": "QR_JAKE_036"},
                {"name": "Kara Thompson", "role": "Assembly Line Worker", "qr_code": "QR_KARA_037"},
                {"name": "Leo Rodriguez", "role": "Machine Operator", "qr_code": "QR_LEO_038"},
                {"name": "Mia Patel", "role": "Quality Inspector", "qr_code": "QR_MIA_039"},
                {"name": "Nate Kim", "role": "Packaging Specialist", "qr_code": "QR_NATE_040"},
                {"name": "Oscar White", "role": "Production Supervisor", "qr_code": "QR_OSCAR_041"},
                {"name": "Penny Johnson", "role": "Maintenance Technician", "qr_code": "QR_PENNY_042"},
                {"name": "Quincy Davis", "role": "Safety Coordinator", "qr_code": "QR_QUINCY_043"},
                {"name": "Ruby Wilson", "role": "Warehouse Worker", "qr_code": "QR_RUBY_044"},
                {"name": "Steve Garcia", "role": "Forklift Operator", "qr_code": "QR_STEVE_045"},
                {"name": "Tara Brown", "role": "Assembly Line Worker", "qr_code": "QR_TARA_046"},
                {"name": "Ulysses Taylor", "role": "Machine Operator", "qr_code": "QR_ULYSSES_047"},
                {"name": "Vera Lee", "role": "Quality Inspector", "qr_code": "QR_VERA_048"},
                {"name": "Wade Anderson", "role": "Packaging Specialist", "qr_code": "QR_WADE_049"},
                {"name": "Xara Thompson", "role": "Production Manager", "qr_code": "QR_XARA_050"}
            ]
            
            # Take only the requested number of workers
            workers_to_create = factory_workers[:self.target_count]
            
            created_users = []
            
            for worker_data in workers_to_create:
                try:
                    from database.services import UserService
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
            return True
            
        except Exception as e:
            self.log_error(f"User seeding failed: {e}")
            self.rollback()
            return False


class CustomPersonalEntrySeeder(PersonalEntrySeeder):
    """Custom personal entry seeder with configurable count"""
    
    def __init__(self, count=50):
        super().__init__()
        self.target_count = count
    
    def seed(self) -> bool:
        """Seed personal entries with specified count"""
        try:
            # Check if entries already exist
            if self.check_data_exists(PersonalEntry):
                self.log_skip(f"Personal entries already exist - skipping creation")
                return True
            
            # Get dependencies
            from database.services import UserService, RoomEquipmentConfigurationService
            users = UserService.get_all()
            room_configs = RoomEquipmentConfigurationService.get_all()
            
            if not users:
                self.log_error("No users found - run UserSeeder first")
                return False
            
            if not room_configs:
                self.log_error("No room configurations found - run RoomEquipmentConfigurationSeeder first")
                return False
            
            self.log_info(f"Creating {self.target_count} personal entries with equipment detection data...")
            
            # Generate realistic entry scenarios
            entry_scenarios = self._generate_entry_scenarios(users, room_configs)
            
            created_entries = []
            
            for scenario in entry_scenarios:
                try:
                    from database.services import PersonalEntryService
                    entry = PersonalEntryService.create(
                        user_id=scenario["user_id"],
                        room_name=scenario["room_name"],
                        equipment=scenario["equipment"],
                        image_url=scenario["image_url"],
                        calculate_approval=True
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
            return True
            
        except Exception as e:
            self.log_error(f"Personal entry seeding failed: {e}")
            self.rollback()
            return False
    
    def _generate_entry_scenarios(self, users, room_configs):
        """Generate realistic entry scenarios"""
        scenarios = []
        
        # Room names from configurations
        room_names = [config.room_name for config in room_configs]
        
        # Generate entries for the last 30 days
        for i in range(self.target_count):
            user = random.choice(users)
            room_name = random.choice(room_names)
            
            # Get room configuration to generate realistic equipment
            room_config = next((config for config in room_configs if config.room_name == room_name), None)
            
            if room_config:
                # Generate equipment based on room requirements
                equipment = self._generate_realistic_equipment(room_config)
            else:
                # Fallback to random equipment
                from database.seeders.base_seeder import random_equipment_detection
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


class CustomEmotionalAnalysisSeeder(EmotionalAnalysisSeeder):
    """Custom emotional analysis seeder with configurable count"""
    
    def __init__(self, count=50):
        super().__init__()
        self.target_count = count
    
    def seed(self) -> bool:
        """Seed emotional analyses with specified count"""
        try:
            # Check if emotional analyses already exist
            if self.check_data_exists(EmotionalAnalysis):
                self.log_skip(f"Emotional analyses already exist - skipping creation")
                return True
            
            # Get personal entries to analyze
            from database.services import PersonalEntryService
            entries = PersonalEntryService.get_all()
            
            if not entries:
                self.log_error("No personal entries found - run PersonalEntrySeeder first")
                return False
            
            self.log_info(f"Creating {self.target_count} emotional analyses with AWS Rekognition-like data...")
            
            # Select exactly the requested number of entries for emotional analysis
            import random
            entries_to_analyze = random.sample(entries, min(len(entries), self.target_count))
            
            created_analyses = []
            
            for entry in entries_to_analyze:
                try:
                    # Generate realistic emotional analysis data
                    from database.seeders.base_seeder import random_emotion_data, random_recommendations
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
                        analyzed_at=entry.entered_at,
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
            return True
            
        except Exception as e:
            self.log_error(f"Emotional analysis seeding failed: {e}")
            return False


def run_custom_seeders(users=30, rooms=12, entries=50, emotions=50, clean_first=False):
    """Run custom seeders with specified counts"""
    if clean_first:
        if not clean_database():
            return False
    
    print(f"🌱 Starting custom database seeding...")
    print(f"   Users: {users}")
    print(f"   Room Configurations: {rooms}")
    print(f"   Personal Entries: {entries}")
    print(f"   Emotional Analyses: {emotions}")
    print("=" * 60)
    
    runner = SeederRunner()
    
    # Add custom seeders with specified counts
    runner.add_seeder(CustomUserSeeder(users))
    runner.add_seeder(RoomEquipmentConfigurationSeeder())  # Always create all room configs
    runner.add_seeder(CustomPersonalEntrySeeder(entries))
    runner.add_seeder(CustomEmotionalAnalysisSeeder(emotions))
    
    # Run seeders
    success = runner.run_all()
    
    if success:
        print("\n🎉 Custom database seeding completed successfully!")
        print("\n📊 Final Results:")
        results = runner.get_results()
        for seeder_name, summary in results.items():
            print(f"   {seeder_name}:")
            print(f"     Created: {summary['created']}")
            print(f"     Skipped: {summary['skipped']}")
            print(f"     Errors:  {summary['errors']}")
        
        print(f"\n🌐 Your database now contains:")
        print(f"   • {users} factory workers with QR codes")
        print(f"   • 12 room configurations with equipment requirements")
        print(f"   • {entries} personal entries with equipment detection")
        print(f"   • {emotions} emotional analyses with AWS Rekognition data")
        
    return success


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Custom database seeder for Quack as a Service")
    parser.add_argument("--users", type=int, default=30, help="Number of users to create (default: 30)")
    parser.add_argument("--rooms", type=int, default=12, help="Number of room configurations to create (default: 12)")
    parser.add_argument("--entries", type=int, default=50, help="Number of personal entries to create (default: 50)")
    parser.add_argument("--emotions", type=int, default=50, help="Number of emotional analyses to create (default: 50)")
    parser.add_argument("--all", type=int, help="Create this many of each model (overrides individual counts)")
    parser.add_argument("--clean", action="store_true", help="Clean database before seeding")
    parser.add_argument("--status", action="store_true", help="Show database status")
    
    args = parser.parse_args()
    
    if args.status:
        show_database_status()
        return
    
    # Use --all value if provided
    if args.all:
        rooms = entries = emotions = args.all
    else:
        rooms = args.rooms
        entries = args.entries
        emotions = args.emotions
    
    users = 6
    
    # Validate counts
    if users < 0 or rooms < 0 or entries < 0 or emotions < 0:
        print("❌ Counts must be non-negative")
        sys.exit(1)
    
    if entries > 0 and users == 0:
        print("❌ Cannot create entries without users")
        sys.exit(1)
    
    if emotions > 0 and entries == 0:
        print("❌ Cannot create emotional analyses without entries")
        sys.exit(1)
    
    # Run custom seeders
    success = run_custom_seeders(
        users=users,
        rooms=rooms,
        entries=entries,
        emotions=emotions,
        clean_first=args.clean
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
