#!/usr/bin/env python3
"""
Database migration script to add qr_code column to users table.

Run this script to add the new QR code column to your existing database:
    python add_qr_code_to_users.py
"""

import sys
import os
from sqlalchemy import text
from database.connection import create_session

def add_qr_code_column():
    """Add qr_code column to users table if it doesn't exist."""
    
    session = create_session()
    
    try:
        # Check if column already exists
        check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'qr_code';
        """
        
        result = session.execute(text(check_column_query)).fetchone()
        
        if result:
            print("✅ qr_code column already exists on users table - no migration needed")
            return True
        
        # Add the new column
        print("📊 Adding qr_code column to users table...")
        
        add_column_query = """
        ALTER TABLE users 
        ADD COLUMN qr_code VARCHAR(255) UNIQUE;
        """
        
        session.execute(text(add_column_query))
        session.commit()
        
        print("✅ Successfully added qr_code column to users table")
        return True
        
    except Exception as e:
        print(f"❌ Error adding qr_code column: {e}")
        session.rollback()
        return False
        
    finally:
        session.close()

def remove_old_qr_codes_column():
    """Remove the old qr_codes column from personal_entries if it exists."""
    
    session = create_session()
    
    try:
        # Check if old column exists
        check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'personal_entries' 
        AND column_name = 'qr_codes';
        """
        
        result = session.execute(text(check_column_query)).fetchone()
        
        if result:
            print("🧹 Removing old qr_codes column from personal_entries table...")
            
            remove_column_query = """
            ALTER TABLE personal_entries 
            DROP COLUMN qr_codes;
            """
            
            session.execute(text(remove_column_query))
            session.commit()
            
            print("✅ Successfully removed old qr_codes column from personal_entries table")
        else:
            print("ℹ️  No old qr_codes column found in personal_entries table")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error removing old qr_codes column: {e}")
        print("💡 This is not critical - you can remove it manually if needed")
        session.rollback()
        return True  # Don't fail the migration for this
        
    finally:
        session.close()

def main():
    """Main migration function."""
    print("🚀 Starting user QR code migration...")
    
    try:
        # Step 1: Add qr_code column to users
        success1 = add_qr_code_column()
        
        # Step 2: Remove old qr_codes column from personal_entries (cleanup)
        success2 = remove_old_qr_codes_column()
        
        if success1:
            print("\n✅ Migration completed successfully!")
            print("💡 You can now assign QR codes to users and detect them in images")
            print("📝 Example usage:")
            print("   1. Update a user with a QR code: PUT /users/{id} with 'qr_code' field")
            print("   2. Upload images without user_id - the QR code will identify the user")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
