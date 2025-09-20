#!/usr/bin/env python3
"""
Migration: Room Equipment Configuration & Approval System

Created: 2024-09-20
Description: 
- Adds room_equipment_configurations table with weights and thresholds
- Adds approval fields to personal_entries table (is_approved, equipment_score, approval_reason)
- Creates default room configurations for existing rooms
- Adds performance indexes
"""

import sys
import os
from sqlalchemy import text, inspect
from database.connection import create_session, get_engine

def check_table_exists(table_name):
    """Check if a table exists"""
    inspector = inspect(get_engine())
    return table_name in inspector.get_table_names()

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(get_engine())
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)

def create_room_equipment_configurations_table():
    """Create the room_equipment_configurations table."""
    
    session = create_session()
    
    try:
        if check_table_exists('room_equipment_configurations'):
            print("   ✅ room_equipment_configurations table already exists")
            return True
        
        print("   📊 Creating room_equipment_configurations table...")
        
        create_table_query = """
        CREATE TABLE room_equipment_configurations (
            id SERIAL PRIMARY KEY,
            room_name VARCHAR(100) NOT NULL UNIQUE,
            equipment_weights JSONB NOT NULL DEFAULT '{}',
            entry_threshold FLOAT NOT NULL DEFAULT 70.0,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            description VARCHAR(500),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        session.execute(text(create_table_query))
        session.commit()
        
        print("   ✅ Successfully created room_equipment_configurations table")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating room_equipment_configurations table: {e}")
        session.rollback()
        return False
        
    finally:
        session.close()

def add_approval_fields_to_personal_entries():
    """Add approval fields to personal_entries table."""
    
    session = create_session()
    
    try:
        # Check if columns already exist
        if check_column_exists('personal_entries', 'is_approved'):
            print("   ✅ Approval fields already exist in personal_entries table")
            return True
        
        print("   📊 Adding approval fields to personal_entries table...")
        
        add_columns_query = """
        ALTER TABLE personal_entries 
        ADD COLUMN is_approved BOOLEAN,
        ADD COLUMN equipment_score FLOAT,
        ADD COLUMN approval_reason VARCHAR(500);
        """
        
        session.execute(text(add_columns_query))
        session.commit()
        
        print("   ✅ Successfully added approval fields to personal_entries table")
        return True
        
    except Exception as e:
        print(f"   ❌ Error adding approval fields: {e}")
        session.rollback()
        return False
        
    finally:
        session.close()

def create_performance_indexes():
    """Create performance indexes for the new tables and columns."""
    
    session = create_session()
    
    try:
        print("   📊 Creating performance indexes...")
        
        indexes_queries = [
            "CREATE INDEX IF NOT EXISTS idx_personal_entries_is_approved ON personal_entries(is_approved);",
            "CREATE INDEX IF NOT EXISTS idx_room_equipment_configurations_room_name ON room_equipment_configurations(room_name);",
            "CREATE INDEX IF NOT EXISTS idx_room_equipment_configurations_is_active ON room_equipment_configurations(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_room_equipment_configurations_weights ON room_equipment_configurations USING GIN(equipment_weights);"
        ]
        
        for query in indexes_queries:
            session.execute(text(query))
        
        session.commit()
        
        print("   ✅ Successfully created performance indexes")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating indexes: {e}")
        session.rollback()
        return False
        
    finally:
        session.close()

def create_default_room_configurations():
    """Create default room equipment configurations."""
    
    session = create_session()
    
    try:
        print("   📊 Creating default room configurations...")
        
        # Check if any configurations already exist
        check_query = "SELECT COUNT(*) FROM room_equipment_configurations;"
        result = session.execute(text(check_query)).fetchone()
        
        if result[0] > 0:
            print("   ✅ Room configurations already exist - skipping defaults")
            return True
        
        # Insert default configurations
        default_configs = [
            {
                "room_name": "production-floor",
                "equipment_weights": '{"mask": 35, "gloves": 30, "hairnet": 35}',
                "entry_threshold": 80.0,
                "is_active": True,
                "description": "Production Floor - High safety requirements with mask, gloves, and hairnet"
            },
            {
                "room_name": "assembly-line", 
                "equipment_weights": '{"gloves": 50, "hairnet": 50}',
                "entry_threshold": 70.0,
                "is_active": True,
                "description": "Assembly Line - Moderate requirements with gloves and hairnet"
            },
            {
                "room_name": "packaging-area",
                "equipment_weights": '{"gloves": 100}',
                "entry_threshold": 60.0,
                "is_active": True,
                "description": "Packaging Area - Basic hygiene requirements with gloves"
            }
        ]
        
        for config in default_configs:
            insert_query = """
            INSERT INTO room_equipment_configurations 
            (room_name, equipment_weights, entry_threshold, is_active, description) 
            VALUES (:room_name, :equipment_weights, :entry_threshold, :is_active, :description);
            """
            
            session.execute(text(insert_query), {
                'room_name': config['room_name'],
                'equipment_weights': config['equipment_weights'],
                'entry_threshold': config['entry_threshold'],
                'is_active': config['is_active'],
                'description': config['description']
            })
        
        session.commit()
        
        print(f"   ✅ Successfully created {len(default_configs)} default room configurations")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating default configurations: {e}")
        session.rollback()
        return False
        
    finally:
        session.close()

def recalculate_existing_entries():
    """Recalculate approval status for existing entries (if any)."""
    
    session = create_session()
    
    try:
        # Check if there are any entries to update
        check_query = "SELECT COUNT(*) FROM personal_entries WHERE is_approved IS NULL;"
        result = session.execute(text(check_query)).fetchone()
        
        if result[0] == 0:
            print("   ✅ No entries need approval status recalculation")
            return True
            
        print(f"   📊 Found {result[0]} entries that need approval status calculation...")
        print("   💡 Entries will be recalculated when accessed via the API")
        
        # We don't recalculate here to avoid import issues during migration
        # The API will handle this automatically when entries are accessed
        
        return True
        
    except Exception as e:
        print(f"   ⚠️  Note: Existing entries will be calculated on first access: {e}")
        return True  # Don't fail migration for this
        
    finally:
        session.close()

def add_room_approval_system():
    """Main migration logic for: Room Equipment Configuration & Approval System"""
    
    print("🏭 Setting up Room Equipment Configuration & Approval System...")
    
    # Step 1: Create room_equipment_configurations table
    if not create_room_equipment_configurations_table():
        return False
    
    # Step 2: Add approval fields to personal_entries
    if not add_approval_fields_to_personal_entries():
        return False
    
    # Step 3: Create performance indexes
    if not create_performance_indexes():
        return False
    
    # Step 4: Create default room configurations
    if not create_default_room_configurations():
        return False
    
    # Step 5: Handle existing entries (optional)
    recalculate_existing_entries()
    
    print("✅ Room Approval System migration completed successfully!")
    print("")
    print("🎉 New Features Available:")
    print("   • Room equipment configurations with customizable weights")
    print("   • Automatic entry approval/denial based on configurable thresholds")
    print("   • Equipment scoring system (0-100%)")
    print("   • Real-time analytics and performance tracking")
    print("   • Enhanced API endpoints for room configuration management")
    print("")
    print("🌐 Access the new features:")
    print("   • API: /room-configurations")
    print("   • Frontend: /room-configurations (when frontend is running)")
    
    return True

def main():
    """Main migration function."""
    print("🚀 Running migration: Room Equipment Configuration & Approval System")
    
    try:
        success = add_room_approval_system()
        
        if success:
            print("\n✅ Migration completed successfully!")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
