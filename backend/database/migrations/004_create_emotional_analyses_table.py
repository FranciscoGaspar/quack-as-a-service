"""
Migration: Create emotional_analyses table and remove emotional analysis fields from personal_entries
"""

from database.connection import get_session
from sqlalchemy import text

def upgrade():
    """Create emotional_analyses table and remove old fields from personal_entries."""
    session = get_session()
    try:
        # Create emotional_analyses table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS emotional_analyses (
                id SERIAL PRIMARY KEY,
                personal_entry_id INTEGER NOT NULL UNIQUE REFERENCES personal_entries(id) ON DELETE CASCADE,
                faces_detected INTEGER NOT NULL DEFAULT 0,
                dominant_emotion VARCHAR(50),
                overall_confidence FLOAT,
                image_quality VARCHAR(20),
                analysis_data JSONB,
                recommendations JSONB,
                analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        
        # Remove old emotional analysis fields from personal_entries
        session.execute(text("""
            ALTER TABLE personal_entries 
            DROP COLUMN IF EXISTS emotional_analysis,
            DROP COLUMN IF EXISTS dominant_emotion,
            DROP COLUMN IF EXISTS emotion_confidence,
            DROP COLUMN IF EXISTS faces_detected,
            DROP COLUMN IF EXISTS emotional_analysis_timestamp
        """))
        
        session.commit()
        print("✅ Created emotional_analyses table and removed old fields from personal_entries")

    finally:
        session.close()

def downgrade():
    """Remove emotional_analyses table and restore old fields to personal_entries."""
    session = get_session()
    try:
        # Drop emotional_analyses table
        session.execute(text("DROP TABLE IF EXISTS emotional_analyses"))
        
        # Restore old emotional analysis fields to personal_entries
        session.execute(text("""
            ALTER TABLE personal_entries 
            ADD COLUMN IF NOT EXISTS emotional_analysis JSONB,
            ADD COLUMN IF NOT EXISTS dominant_emotion VARCHAR(50),
            ADD COLUMN IF NOT EXISTS emotion_confidence FLOAT,
            ADD COLUMN IF NOT EXISTS faces_detected INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS emotional_analysis_timestamp TIMESTAMP WITH TIME ZONE
        """))
        
        session.commit()
        print("✅ Removed emotional_analyses table and restored old fields to personal_entries")

    finally:
        session.close()

def main():
    """Main migration function."""
    print("🚀 Running migration: Create emotional_analyses table and remove emotional analysis fields from personal_entries")
    
    try:
        upgrade()
        print("✅ Migration completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        raise

if __name__ == "__main__":
    main()
