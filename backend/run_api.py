#!/usr/bin/env python3
"""
Standalone script to run the FastAPI server.
Use this to start the API separately from the main setup.
"""

import uvicorn
from main import app
from core.config import settings

if __name__ == "__main__":
    print("🦆 Starting Quack as a Service API...")
    print("====================================")
    print(f"API Server: http://{settings.HOST}:{settings.PORT}")
    print(f"Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"Redoc: http://{settings.HOST}:{settings.PORT}/redoc")
    print("")
    print("Press Ctrl+C to stop")
    print("====================================")
    
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.RELOAD,
        log_level="info"
    )