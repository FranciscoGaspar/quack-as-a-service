#!/bin/bash

echo "🛑 Stopping Quack as a Service..."
echo "=================================="

# Stop PostgreSQL
docker-compose down

echo "✅ All services stopped!"
echo ""
echo "To restart: ./start.sh"
