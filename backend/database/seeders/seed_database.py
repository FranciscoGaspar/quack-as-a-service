#!/usr/bin/env python3
"""
Main database seeder runner for Quack as a Service.

This script orchestrates all database seeders to populate the database with realistic test data.

Usage:
    python seed_database.py              # Run all seeders
    python seed_database.py --force      # Force re-seed (clear existing data)
    python seed_database.py --users      # Run only user seeder
    python seed_database.py --rooms      # Run only room configuration seeder
    python seed_database.py --entries    # Run only personal entry seeder
    python seed_database.py --emotions   # Run only emotional analysis seeder
    python seed_database.py --status     # Show seeding status
"""

import sys
import os
import argparse
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import create_session, get_engine
from database.models import User, PersonalEntry, RoomEquipmentConfiguration, EmotionalAnalysis
from database.seeders.base_seeder import SeederRunner
from database.seeders.user_seeder import UserSeeder
from database.seeders.room_configuration_seeder import RoomEquipmentConfigurationSeeder
from database.seeders.personal_entry_seeder import PersonalEntrySeeder
from database.seeders.emotional_analysis_seeder import EmotionalAnalysisSeeder


def clear_database(force=False):
    """Clear all data from the database"""
    if not force:
        print("⚠️  WARNING: This will delete ALL data from the database!")
        print("   This action cannot be undone.")
        
        confirm = input("   Are you sure you want to continue? (type 'yes' to confirm): ")
        if confirm.lower() != 'yes':
            print("   Operation cancelled.")
            return False
    
    print("🗑️  Clearing database...")
    
    session = create_session()
    try:
        # Delete in reverse dependency order to avoid foreign key constraints
        print("   🧹 Deleting emotional analyses...")
        session.query(EmotionalAnalysis).delete()
        
        print("   🧹 Deleting personal entries...")
        session.query(PersonalEntry).delete()
        
        print("   🧹 Deleting room equipment configurations...")
        session.query(RoomEquipmentConfiguration).delete()
        
        print("   🧹 Deleting users...")
        session.query(User).delete()
        
        # Also clear migration history if it exists
        try:
            from database.migrate import MigrationHistory
            print("   🧹 Clearing migration history...")
            session.query(MigrationHistory).delete()
        except Exception:
            # MigrationHistory table might not exist, that's okay
            pass
        
        session.commit()
        
        print("✅ Database cleared successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def show_seeding_status():
    """Show current seeding status"""
    print("📊 Database Seeding Status")
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
        print(f"Emotional Analyses:       {emotion_count:4d}")
        
        print("\n📈 Summary:")
        total_records = user_count + room_config_count + entry_count + emotion_count
        
        if total_records == 0:
            print("   Database is empty - run seeders to populate data")
        elif total_records < 100:
            print("   Database has minimal data - consider running full seeding")
        elif total_records < 500:
            print("   Database has moderate data - good for testing")
        else:
            print("   Database is well populated - ready for development")
        
        # Check for missing relationships
        if user_count > 0 and entry_count == 0:
            print("   ⚠️  Users exist but no entries - run PersonalEntrySeeder")
        if room_config_count > 0 and entry_count == 0:
            print("   ⚠️  Room configs exist but no entries - run PersonalEntrySeeder")
        if entry_count > 0 and emotion_count == 0:
            print("   ℹ️  Entries exist but no emotional analyses - run EmotionalAnalysisSeeder")
        
    finally:
        session.close()


def run_seeders(seeders_to_run=None, force=False, clean_first=False):
    """Run specified seeders"""
    if force or clean_first:
        if not clear_database(force=force):
            return False
    
    runner = SeederRunner()
    
    # Add all seeders
    runner.add_seeder(UserSeeder())
    runner.add_seeder(RoomEquipmentConfigurationSeeder())
    runner.add_seeder(PersonalEntrySeeder())
    runner.add_seeder(EmotionalAnalysisSeeder())
    
    # Filter seeders if specific ones requested
    if seeders_to_run:
        filtered_seeders = []
        for seeder in runner.seeders:
            seeder_name = seeder.get_seeder_name().lower()
            if any(requested in seeder_name for requested in seeders_to_run):
                filtered_seeders.append(seeder)
        
        if not filtered_seeders:
            print(f"❌ No seeders found matching: {', '.join(seeders_to_run)}")
            return False
        
        runner.seeders = filtered_seeders
    
    # Run seeders
    success = runner.run_all()
    
    if success:
        print("\n🎉 Database seeding completed successfully!")
        print("\n📊 Final Results:")
        results = runner.get_results()
        for seeder_name, summary in results.items():
            print(f"   {seeder_name}:")
            print(f"     Created: {summary['created']}")
            print(f"     Skipped: {summary['skipped']}")
            print(f"     Errors:  {summary['errors']}")
        
        print("\n🌐 Your database is now ready for development!")
        print("   • 30 factory workers with QR codes")
        print("   • 12 room configurations with equipment requirements")
        print("   • 50 personal entries with equipment detection")
        print("   • 50 emotional analyses with AWS Rekognition data")
        
    return success


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Database seeder for Quack as a Service")
    parser.add_argument("--force", action="store_true", help="Force re-seed (clear existing data without confirmation)")
    parser.add_argument("--clean", action="store_true", help="Clean database before seeding (with confirmation)")
    parser.add_argument("--users", action="store_true", help="Run only user seeder")
    parser.add_argument("--rooms", action="store_true", help="Run only room configuration seeder")
    parser.add_argument("--entries", action="store_true", help="Run only personal entry seeder")
    parser.add_argument("--emotions", action="store_true", help="Run only emotional analysis seeder")
    parser.add_argument("--status", action="store_true", help="Show seeding status")
    
    args = parser.parse_args()
    
    if args.status:
        show_seeding_status()
        return
    
    # Determine which seeders to run
    seeders_to_run = []
    if args.users:
        seeders_to_run.append("user")
    if args.rooms:
        seeders_to_run.append("room")
    if args.entries:
        seeders_to_run.append("entry")
    if args.emotions:
        seeders_to_run.append("emotional")
    
    # Run seeders
    success = run_seeders(
        seeders_to_run if seeders_to_run else None, 
        force=args.force, 
        clean_first=args.clean
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
