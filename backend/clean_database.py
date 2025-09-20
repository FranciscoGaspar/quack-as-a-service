#!/usr/bin/env python3
"""
Database cleaner script for Quack as a Service.

This script provides a quick way to clean all data from the database.
Useful for development when you need to start fresh without running seeders.

Usage:
    python clean_database.py              # Clean with confirmation prompt
    python clean_database.py --force      # Clean without confirmation
    python clean_database.py --status     # Show current database status
"""

import sys
import os
import argparse
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import create_session, get_engine
from database.models import User, PersonalEntry, RoomEquipmentConfiguration, EmotionalAnalysis


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
        
        # Show relationships
        if user_count > 0 and entry_count > 0:
            avg_entries_per_user = entry_count / user_count
            print(f"   Average entries per user: {avg_entries_per_user:.1f}")
        
        if entry_count > 0 and emotion_count > 0:
            analysis_coverage = (emotion_count / entry_count) * 100
            print(f"   Emotional analysis coverage: {analysis_coverage:.1f}%")
        
    finally:
        session.close()


def clean_database(force=False):
    """Clean all data from the database"""
    if not force:
        print("⚠️  WARNING: This will delete ALL data from the database!")
        print("   This action cannot be undone.")
        print("   Tables that will be cleared:")
        print("     • emotional_analyses")
        print("     • personal_entries") 
        print("     • room_equipment_configurations")
        print("     • users")
        print("     • migration_history (if exists)")
        
        confirm = input("\n   Are you sure you want to continue? (type 'yes' to confirm): ")
        if confirm.lower() != 'yes':
            print("   Operation cancelled.")
            return False
    
    print("🗑️  Cleaning database...")
    
    session = create_session()
    try:
        # Show what we're about to delete
        user_count = session.query(User).count()
        room_config_count = session.query(RoomEquipmentConfiguration).count()
        entry_count = session.query(PersonalEntry).count()
        emotion_count = session.query(EmotionalAnalysis).count()
        
        print(f"   📊 Found {user_count} users, {room_config_count} room configs, {entry_count} entries, {emotion_count} analyses")
        
        # Delete in reverse dependency order to avoid foreign key constraints
        print("   🧹 Deleting emotional analyses...")
        deleted_emotions = session.query(EmotionalAnalysis).delete()
        print(f"      Deleted {deleted_emotions} emotional analyses")
        
        print("   🧹 Deleting personal entries...")
        deleted_entries = session.query(PersonalEntry).delete()
        print(f"      Deleted {deleted_entries} personal entries")
        
        print("   🧹 Deleting room equipment configurations...")
        deleted_configs = session.query(RoomEquipmentConfiguration).delete()
        print(f"      Deleted {deleted_configs} room configurations")
        
        print("   🧹 Deleting users...")
        deleted_users = session.query(User).delete()
        print(f"      Deleted {deleted_users} users")
        
        # Also clear migration history if it exists
        try:
            from database.migrate import MigrationHistory
            print("   🧹 Clearing migration history...")
            deleted_migrations = session.query(MigrationHistory).delete()
            print(f"      Deleted {deleted_migrations} migration records")
        except Exception:
            # MigrationHistory table might not exist, that's okay
            print("      No migration history table found")
        
        session.commit()
        
        print("\n✅ Database cleaned successfully!")
        print(f"   Total records deleted: {deleted_users + deleted_configs + deleted_entries + deleted_emotions}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error cleaning database: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Database cleaner for Quack as a Service")
    parser.add_argument("--force", action="store_true", help="Clean without confirmation prompt")
    parser.add_argument("--status", action="store_true", help="Show database status")
    
    args = parser.parse_args()
    
    if args.status:
        show_database_status()
        return
    
    # Clean the database
    success = clean_database(force=args.force)
    
    if success:
        print("\n🎉 Database is now clean and ready for fresh data!")
        print("💡 You can now run seeders to populate with test data:")
        print("   python database/seeders/seed_database.py")
    else:
        print("\n❌ Database cleaning failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
