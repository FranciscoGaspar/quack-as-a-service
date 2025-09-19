"""
Application configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings."""
    
    # API settings
    API_TITLE: str = "🦆 Quack as a Service API"
    API_DESCRIPTION: str = "Room Entry Tracking API with Security Equipment Compliance"
    API_VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://quack:quack@localhost:5432/quack")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]  # Configure properly for production
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Object Detection settings (for future use)
    DETECTION_THRESHOLD: float = float(os.getenv("DETECTION_THRESHOLD", "0.3"))
    TEXT_QUERIES: str = os.getenv("TEXT_QUERIES", "a mask. a glove. a hairnet.")
    
    # File Storage settings (for future use)
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    DETECTION_OUTPUT_FOLDER: str = os.getenv("DETECTION_OUTPUT_FOLDER", "detected_frames")

# Create settings instance
settings = Settings()
