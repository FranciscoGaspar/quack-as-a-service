#!/bin/bash

echo "🛑 Stopping Quack as a Service..."
echo "=================================="

# Stop Python processes (FastAPI backend)
echo "🛑 Stopping FastAPI backend..."
pkill -f "python.*main.py" || echo "No FastAPI process found"
pkill -f "uvicorn.*main:app" || echo "No uvicorn process found"

# Stop Node.js processes (Next.js frontend)
echo "🛑 Stopping Next.js frontend..."
pkill -f "next-server" || echo "No Next.js process found"
pkill -f "node.*next" || echo "No Next.js process found"

# Wait a moment for processes to stop
sleep 2

# Check if ports are free
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 still in use, force killing..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
fi

if lsof -i :3000 > /dev/null 2>&1; then
    echo "⚠️  Port 3000 still in use, force killing..."
    lsof -ti :3000 | xargs kill -9 2>/dev/null || true
fi

echo "✅ All services stopped!"
echo ""
echo "To restart: ./start.sh"
