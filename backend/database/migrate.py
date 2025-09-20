#!/usr/bin/env python3
"""
Database migration runner for Quack as a Service.

This script manages and runs database migrations in order.

Usage:
    python migrate.py              # Run all pending migrations
    python migrate.py --status     # Show migration status
    python migrate.py --create "migration_name"  # Create new migration template
"""

import sys
import os
import importlib.util
import argparse
from datetime import datetime
from pathlib import Path
from sqlalchemy import text, Column, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import create_session, get_engine

# Migration tracking table
Base = declarative_base()

class MigrationHistory(Base):
    """Table to track which migrations have been applied."""
    __tablename__ = 'migration_history'
    
    migration_name = Column(String(255), primary_key=True)
    applied_at = Column(DateTime, default=datetime.utcnow)

def ensure_migration_table():
    """Create the migration history table if it doesn't exist."""
    Base.metadata.create_all(get_engine())

def get_applied_migrations():
    """Get list of migrations that have been applied."""
    session = create_session()
    try:
        result = session.query(MigrationHistory.migration_name).all()
        return [row[0] for row in result]
    except Exception:
        # Table might not exist yet
        return []
    finally:
        session.close()

def mark_migration_applied(migration_name):
    """Mark a migration as applied."""
    session = create_session()
    try:
        migration_record = MigrationHistory(migration_name=migration_name)
        session.add(migration_record)
        session.commit()
    finally:
        session.close()

def get_migration_files():
    """Get all migration files in order."""
    migrations_dir = Path(__file__).parent / "migrations"
    
    if not migrations_dir.exists():
        print("❌ Migrations directory not found")
        return []
    
    migration_files = []
    for file_path in migrations_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            migration_files.append(file_path)
    
    # Sort by filename (which should include sequence number)
    migration_files.sort()
    return migration_files

def load_migration_module(file_path):
    """Load a migration module dynamically."""
    spec = importlib.util.spec_from_file_location(
        file_path.stem, file_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_migration(file_path):
    """Run a single migration file."""
    print(f"🚀 Running migration: {file_path.name}")
    
    try:
        # Load the migration module
        module = load_migration_module(file_path)
        
        # Check if it has the expected main function
        if hasattr(module, 'main'):
            # Run the migration
            module.main()
            return True
        else:
            print(f"❌ Migration {file_path.name} doesn't have a main() function")
            return False
            
    except Exception as e:
        print(f"❌ Error running migration {file_path.name}: {e}")
        return False

def run_all_migrations():
    """Run all pending migrations."""
    ensure_migration_table()
    
    migration_files = get_migration_files()
    applied_migrations = get_applied_migrations()
    
    if not migration_files:
        print("ℹ️  No migration files found")
        return True
    
    pending_migrations = []
    for file_path in migration_files:
        if file_path.stem not in applied_migrations:
            pending_migrations.append(file_path)
    
    if not pending_migrations:
        print("✅ All migrations are up to date")
        return True
    
    print(f"📋 Found {len(pending_migrations)} pending migration(s)")
    
    success_count = 0
    for file_path in pending_migrations:
        if run_migration(file_path):
            mark_migration_applied(file_path.stem)
            success_count += 1
            print(f"✅ Migration {file_path.name} completed successfully")
        else:
            print(f"❌ Migration {file_path.name} failed")
            break  # Stop on first failure
    
    if success_count == len(pending_migrations):
        print(f"\n🎉 All {success_count} migration(s) completed successfully!")
        return True
    else:
        print(f"\n⚠️  {success_count}/{len(pending_migrations)} migrations completed")
        return False

def show_migration_status():
    """Show status of all migrations."""
    ensure_migration_table()
    
    migration_files = get_migration_files()
    applied_migrations = get_applied_migrations()
    
    if not migration_files:
        print("ℹ️  No migration files found")
        return
    
    print("📋 Migration Status:")
    print("-" * 50)
    
    for file_path in migration_files:
        status = "✅ Applied" if file_path.stem in applied_migrations else "⏳ Pending"
        print(f"{status:12} {file_path.name}")
    
    applied_count = len([f for f in migration_files if f.stem in applied_migrations])
    total_count = len(migration_files)
    
    print("-" * 50)
    print(f"Applied: {applied_count}/{total_count}")

def create_migration_template(name):
    """Create a new migration file template."""
    migrations_dir = Path(__file__).parent / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    
    # Get next sequence number
    existing_files = get_migration_files()
    next_seq = len(existing_files) + 1
    
    # Create filename
    clean_name = name.lower().replace(" ", "_").replace("-", "_")
    filename = f"{next_seq:03d}_{clean_name}.py"
    file_path = migrations_dir / filename
    
    # Create template content
    template = f'''#!/usr/bin/env python3
"""
Migration: {name}

Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import sys
import os
from sqlalchemy import text
from database.connection import create_session

def {clean_name}():
    """Main migration logic for: {name}"""
    
    session = create_session()
    
    try:
        # TODO: Add your migration logic here
        # Example:
        # session.execute(text("ALTER TABLE users ADD COLUMN new_field VARCHAR(255);"))
        # session.commit()
        
        print("✅ Migration '{name}' completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in migration '{name}': {{e}}")
        session.rollback()
        return False
        
    finally:
        session.close()

def main():
    """Main migration function."""
    print(f"🚀 Running migration: {name}")
    
    try:
        success = {clean_name}()
        
        if success:
            print("✅ Migration completed successfully!")
        else:
            print("❌ Migration failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration failed with error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    # Write the template
    with open(file_path, 'w') as f:
        f.write(template)
    
    print(f"✅ Created migration template: {filename}")
    print(f"📝 Edit the file to add your migration logic")
    return file_path

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Database migration runner")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--create", type=str, help="Create new migration template")
    
    args = parser.parse_args()
    
    if args.status:
        show_migration_status()
    elif args.create:
        create_migration_template(args.create)
    else:
        # Run all pending migrations
        success = run_all_migrations()
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
