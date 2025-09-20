"""
Migration: Add emotional analysis fields to personal_entries table
"""

from database.connection import get_session
from sqlalchemy import text

def upgrade():
    """Add emotional analysis fields to personal_entries table."""
    session = get_session()
    try:
        # Add emotional analysis columns
        session.execute(text("""
            ALTER TABLE personal_entries 
            ADD COLUMN IF NOT EXISTS emotional_analysis JSONB,
            ADD COLUMN IF NOT EXISTS dominant_emotion VARCHAR(50),
            ADD COLUMN IF NOT EXISTS emotion_confidence FLOAT,
            ADD COLUMN IF NOT EXISTS faces_detected INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS emotional_analysis_timestamp TIMESTAMP WITH TIME ZONE
        """))
        session.commit()
        print("✅ Added emotional analysis fields to personal_entries table")
    finally:
        session.close()

def downgrade():
    """Remove emotional analysis fields from personal_entries table."""
    session = get_session()
    try:
        # Remove emotional analysis columns
        session.execute(text("""
            ALTER TABLE personal_entries 
            DROP COLUMN IF EXISTS emotional_analysis,
            DROP COLUMN IF EXISTS dominant_emotion,
            DROP COLUMN IF EXISTS emotion_confidence,
            DROP COLUMN IF EXISTS faces_detected,
            DROP COLUMN IF EXISTS emotional_analysis_timestamp
        """))
        session.commit()
        print("✅ Removed emotional analysis fields from personal_entries table")
    finally:
        session.close()

if __name__ == "__main__":
    upgrade()
