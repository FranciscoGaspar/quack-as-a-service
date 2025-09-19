"""
Health check and system status endpoints.
"""

from fastapi import APIRouter, HTTPException

from database.services import UserService, PersonalEntryService

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "🦆 Quack as a Service API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }


@router.get("/health")
async def health_check():
    """Detailed health check with database connection test."""
    try:
        # Test database connection by getting counts
        users_count = len(UserService.get_all())
        entries_count = len(PersonalEntryService.get_all())
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0",
            "stats": {
                "users": users_count,
                "entries": entries_count
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Database connection failed: {str(e)}"
        )
