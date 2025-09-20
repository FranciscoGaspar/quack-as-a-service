"""
FastAPI application for Quack as a Service - Room Entry Tracking API.

Clean, organized FastAPI app with separated routes and configuration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from database.connection import init_db
from api.routes import health, users, entries, rooms


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Initialize database
    print("🦆 Starting Quack as a Service API...")
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

    yield

    # Shutdown
    print("🦆 Quack API shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    # Create FastAPI app
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(entries.router)
    app.include_router(entries.user_entries_router)
    app.include_router(entries.room_entries_router)
    app.include_router(rooms.router)

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
