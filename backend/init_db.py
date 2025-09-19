#!/usr/bin/env python3
"""Database initialization script for Quack as a Service - Database Only"""
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
from database import init_db, get_engine, User, PersonalEntry
from database.services import UserService, PersonalEntryService

# Load environment variables
load_dotenv()

def initialize_database():
    """Initialize PostgreSQL database and create tables"""
    print("🦆 Quack as a Service - Database Initialization")
    print("=" * 50)
    
    try:
        # Initialize database
        print("🔗 Connecting to PostgreSQL database...")
        engine = init_db()
        
        # Check if tables were created successfully
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")
        
        # Create default user if none exists
        existing_users = UserService.get_all()
        if not existing_users:
            print("👤 Creating default users...")
            
            # Create sample users
            admin_user = UserService.create(name='Admin User')
            test_user = UserService.create(name='Test User')
            
            print("✅ Default users created!")
            print(f"   - {admin_user.name} (ID: {admin_user.id})")
            print(f"   - {test_user.name} (ID: {test_user.id})")
            
            # Create sample entries
            print("📝 Creating sample personal entries...")
            sample_entry_1 = PersonalEntryService.create(
                user_id=admin_user.id,
                room_name='Laboratory A',
                image_url='/images/admin_entry_1.jpg',
                equipment={'mask': True, 'right_glove': True, 'left_glove': False, 'hairnet': True}
            )
            
            sample_entry_2 = PersonalEntryService.create(
                user_id=test_user.id,
                room_name='Clean Room B',
                image_url='/images/test_entry_1.jpg',
                equipment={'mask': False, 'right_glove': True, 'left_glove': True, 'hairnet': False}
            )
            
            print("✅ Sample entries created!")
            print(f"   - Entry {sample_entry_1.id} for {admin_user.name} in {sample_entry_1.room_name}")
            print(f"   - Entry {sample_entry_2.id} for {test_user.name} in {sample_entry_2.room_name}")
            
        else:
            print(f"👤 {len(existing_users)} users already exist in database")
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nYou can now:")
        print("  - Use the database services in your code")
        print("  - Run 'python live_detection.py' to start live detection")
        print("  - Connect to your PostgreSQL database to view the data")
        print("\nDatabase connection URL:")
        print(f"  {os.getenv('DATABASE_URL', 'Not configured')}")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your DATABASE_URL in .env file")
        print("3. Ensure the database exists and user has permissions")
        print("4. Verify psycopg2-binary is installed: pip install psycopg2-binary")
        sys.exit(1)

def show_database_info():
    """Display database connection information"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Parse database URL to show connection info (hide password)
        if database_url.startswith('postgresql://'):
            parts = database_url.replace('postgresql://', '').split('/')
            if len(parts) >= 2:
                connection_info = parts[0]
                database_name = parts[1]
                
                if '@' in connection_info:
                    user_pass, host_port = connection_info.split('@')
                    if ':' in user_pass:
                        username = user_pass.split(':')[0]
                    else:
                        username = user_pass
                else:
                    username = 'unknown'
                    host_port = connection_info
                
                print(f"🔗 Database: {database_name}")
                print(f"👤 User: {username}")
                print(f"🖥️  Host: {host_port}")
        else:
            print(f"🔗 Database URL: {database_url}")
    else:
        print("❌ No DATABASE_URL found in environment")

if __name__ == '__main__':
    print("🦆 Initializing Quack as a Service Database...")
    show_database_info()
    print()
    
    # Ask for confirmation
    confirm = input("Do you want to initialize the database? (y/N): ").lower().strip()
    if confirm in ['y', 'yes']:
        initialize_database()
    else:
        print("Database initialization cancelled.")
