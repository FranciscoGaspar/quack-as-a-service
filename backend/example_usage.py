#!/usr/bin/env python3
"""Example usage of the Quack as a Service database layer - Basic CRUD"""

from database.services import UserService, PersonalEntryService

def main():
    """Demonstrate basic CRUD operations"""
    print("🦆 Quack as a Service - Basic CRUD Examples")
    print("=" * 50)
    
    # USER CRUD OPERATIONS
    print("1. User CRUD Operations")
    print("-" * 30)
    
    # Create users
    user1 = UserService.create(name="Alice Johnson")
    user2 = UserService.create(name="Bob Smith")
    print(f"✅ Created users: {user1.name} (ID: {user1.id}), {user2.name} (ID: {user2.id})")
    
    # Read users
    all_users = UserService.get_all()
    print(f"📖 Total users: {len(all_users)}")
    
    user_by_id = UserService.get_by_id(user1.id)
    print(f"🔍 Found user by ID: {user_by_id.name}")
    
    # Update user
    updated_user = UserService.update(user1.id, name="Alice Williams")
    print(f"✏️  Updated user: {updated_user.name}")
    
    # PERSONAL ENTRY CRUD OPERATIONS
    print("\n2. Personal Entry CRUD Operations")
    print("-" * 40)
    
    # Create entries
    entry1 = PersonalEntryService.create(
        user_id=user1.id,
        room_name="Laboratory A",
        equipment={
            "mask": True,
            "right_glove": True,
            "left_glove": True,
            "hairnet": True
        },
        image_url="/images/alice_lab_a.jpg"
    )
    print(f"✅ Created entry: ID {entry1.id} - {user1.name} entering {entry1.room_name}")
    
    entry2 = PersonalEntryService.create(
        user_id=user2.id,
        room_name="Clean Room B",
        equipment={
            "mask": False,
            "right_glove": True,
            "left_glove": True,
            "hairnet": False
        },
        image_url="/images/bob_clean_room.jpg"
    )
    print(f"✅ Created entry: ID {entry2.id} - {user2.name} entering {entry2.room_name}")
    
    # Read entries
    all_entries = PersonalEntryService.get_all()
    print(f"📖 Total entries: {len(all_entries)}")
    
    user1_entries = PersonalEntryService.get_by_user(user1.id)
    print(f"🔍 {user1.name}'s entries: {len(user1_entries)}")
    
    lab_entries = PersonalEntryService.get_by_room("Laboratory A")
    print(f"🔍 Laboratory A entries: {len(lab_entries)}")
    
    # Update entry
    updated_entry = PersonalEntryService.update(
        entry1.id,
        room_name="Laboratory A - Section 2",
        equipment={
            "mask": True,
            "right_glove": True,
            "left_glove": True,
            "hairnet": True,
            "safety_glasses": True  # Added safety glasses
        }
    )
    print(f"✏️  Updated entry: {updated_entry.room_name}")
    
    # Update specific equipment
    PersonalEntryService.update_equipment(entry2.id, mask=True, hairnet=True)
    updated_entry2 = PersonalEntryService.get_by_id(entry2.id)
    print(f"✏️  Updated equipment for {user2.name}: {updated_entry2.equipment}")
    
    # Check compliance
    print(f"🔍 Entry 1 compliant: {updated_entry.is_compliant()}")
    print(f"🔍 Entry 2 compliant: {updated_entry2.is_compliant()}")
    print(f"🔍 Entry 2 missing: {updated_entry2.get_missing_equipment()}")
    
    print("\n3. Summary")
    print("-" * 15)
    
    final_users = UserService.get_all()
    final_entries = PersonalEntryService.get_all()
    
    print(f"📊 Total users: {len(final_users)}")
    print(f"📊 Total entries: {len(final_entries)}")
    
    for entry in final_entries:
        user_name = entry.user.name if entry.user else "Unknown"
        compliant = "✅" if entry.is_compliant() else "❌"
        print(f"   {compliant} {user_name} → {entry.room_name}")
    
    print("\n✅ Basic CRUD operations completed!")
    print("\nTo delete entries or users:")
    print(f"   PersonalEntryService.delete({entry1.id})")
    print(f"   UserService.delete({user1.id})  # Also deletes user's entries")

if __name__ == "__main__":
    main()