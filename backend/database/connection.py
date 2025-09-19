"""Database connection and configuration"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create declarative base for models
Base = declarative_base()

def get_database_url():
    """Get database URL from environment"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    return database_url

def create_database_engine():
    """Create database engine with connection pooling"""
    database_url = get_database_url()
    
    # PostgreSQL connection pool settings
    pool_size = int(os.getenv('DB_POOL_SIZE', 10))
    max_overflow = int(os.getenv('DB_MAX_OVERFLOW', 20))
    pool_recycle = int(os.getenv('DB_POOL_RECYCLE', 3600))
    
    engine = create_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=pool_recycle,
        echo=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
    
    return engine

def init_db():
    """Initialize database and create tables"""
    engine = create_database_engine()
    
    # Import models to ensure they're registered with Base
    from . import models
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("✅ Database tables created successfully!")
    
    return engine

def get_session():
    """Get database session for standalone usage"""
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# Global engine and session factory
_engine = None
_session_factory = None

def get_engine():
    """Get global database engine"""
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine

def get_session_factory():
    """Get session factory"""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine())
    return _session_factory

def create_session():
    """Create a new database session"""
    return get_session_factory()()
