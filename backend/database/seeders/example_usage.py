#!/usr/bin/env python3
"""
Example script demonstrating how to use the database seeders.
This script shows how to run seeders programmatically and access seeded data.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, backend_dir)

from database.seeders.base_seeder import SeederRunner
from database.seeders.user_seeder import UserSeeder
from database.seeders.room_configuration_seeder import RoomEquipmentConfigurationSeeder
from database.seeders.personal_entry_seeder import PersonalEntrySeeder
from database.seeders.emotional_analysis_seeder import EmotionalAnalysisSeeder
from database.services import UserService, PersonalEntryService, RoomEquipmentConfigurationService


def demonstrate_seeders():
    """Demonstrate how to use the seeder system"""
    print("🌱 Database Seeder Demonstration")
    print("=" * 50)
    
    # Create seeder runner
    runner = SeederRunner()
    
    # Add seeders
    runner.add_seeder(UserSeeder())
    runner.add_seeder(RoomEquipmentConfigurationSeeder())
    runner.add_seeder(PersonalEntrySeeder())
    runner.add_seeder(EmotionalAnalysisSeeder())
    
    # Run all seeders
    print("\n🚀 Running all seeders...")
    success = runner.run_all()
    
    if success:
        print("\n📊 Demonstrating seeded data access...")
        
        # Demonstrate accessing seeded data
        users = UserService.get_all()
        print(f"\n👥 Users created: {len(users)}")
        print("   Sample users:")
        for user in users[:3]:
            print(f"     • {user.name} (QR: {user.qr_code})")
        
        room_configs = RoomEquipmentConfigurationService.get_all()
        print(f"\n🏭 Room configurations created: {len(room_configs)}")
        print("   Sample room configurations:")
        for config in room_configs[:3]:
            required_count = sum(1 for level in config.equipment_weights.values() if level == "required")
            print(f"     • {config.room_name}: {required_count} required items")
        
        entries = PersonalEntryService.get_all(limit=5)
        print(f"\n📝 Personal entries created: {len(entries)}")
        print("   Sample entries:")
        for entry in entries:
            status = "Approved" if entry.is_approved else "Denied" if entry.is_approved is False else "Pending"
            print(f"     • {entry.user.name} -> {entry.room_name}: {status} (Score: {entry.equipment_score:.1f}%)")
        
        # Demonstrate emotional analysis statistics
        emotion_seeder = EmotionalAnalysisSeeder()
        emotion_stats = emotion_seeder.get_emotion_statistics()
        if emotion_stats:
            print(f"\n😊 Emotional analysis statistics:")
            for emotion, count in emotion_stats.items():
                print(f"     • {emotion}: {count} analyses")
        
        print("\n🎉 Seeder demonstration completed successfully!")
        
    else:
        print("\n❌ Seeder demonstration failed!")
        return False
    
    return True


def demonstrate_individual_seeders():
    """Demonstrate using individual seeders"""
    print("\n🔧 Individual Seeder Demonstration")
    print("=" * 50)
    
    # Demonstrate UserSeeder
    print("\n👥 User Seeder:")
    with UserSeeder() as seeder:
        users = seeder.get_sample_users()
        print(f"   Created {len(users)} users")
        
        random_user = seeder.get_random_user()
        if random_user:
            print(f"   Random user: {random_user.name}")
    
    # Demonstrate RoomEquipmentConfigurationSeeder
    print("\n🏭 Room Configuration Seeder:")
    with RoomEquipmentConfigurationSeeder() as seeder:
        configs = seeder.get_sample_configs()
        print(f"   Created {len(configs)} room configurations")
        
        high_safety_rooms = seeder.get_high_safety_rooms()
        print(f"   High safety rooms: {len(high_safety_rooms)}")
        for room in high_safety_rooms[:2]:
            print(f"     • {room.room_name}")
    
    # Demonstrate PersonalEntrySeeder
    print("\n📝 Personal Entry Seeder:")
    with PersonalEntrySeeder() as seeder:
        entries = seeder.get_sample_entries()
        print(f"   Created {len(entries)} personal entries")
        
        approved_entries = seeder.get_approved_entries()
        denied_entries = seeder.get_denied_entries()
        print(f"   Approved entries: {len(approved_entries)}")
        print(f"   Denied entries: {len(denied_entries)}")
    
    # Demonstrate EmotionalAnalysisSeeder
    print("\n😊 Emotional Analysis Seeder:")
    with EmotionalAnalysisSeeder() as seeder:
        analyses = seeder.get_sample_analyses()
        print(f"   Created {len(analyses)} emotional analyses")
        
        emotion_stats = seeder.get_emotion_statistics()
        if emotion_stats:
            most_common = max(emotion_stats, key=emotion_stats.get)
            print(f"   Most common emotion: {most_common} ({emotion_stats[most_common]} analyses)")


def main():
    """Main demonstration function"""
    try:
        # Run full demonstration
        success = demonstrate_seeders()
        
        if success:
            # Run individual seeder demonstration
            demonstrate_individual_seeders()
            
            print("\n🎯 Key Features Demonstrated:")
            print("   • Comprehensive seeder system with realistic data")
            print("   • Proper dependency management between seeders")
            print("   • Rich factory worker data with QR codes")
            print("   • Diverse room configurations with safety requirements")
            print("   • Realistic equipment detection scenarios")
            print("   • AWS Rekognition-like emotional analysis data")
            print("   • Easy programmatic access to seeded data")
            
        else:
            print("\n❌ Demonstration failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Demonstration error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
