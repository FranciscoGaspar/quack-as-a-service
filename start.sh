#!/bin/bash

echo "🦆 Starting Quack as a Service..."
echo "================================="

# Step 1: Start PostgreSQL
echo "📦 Starting PostgreSQL database..."
docker-compose up -d db
sleep 5

# Step 2: Check if backend is set up
cd backend
if [ ! -d "venv" ]; then
    echo "⚙️  Setting up backend environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Backend environment ready!"
else
    echo "✅ Backend environment already exists!"
    source venv/bin/activate
    pip install -r requirements.txt  # Update dependencies
    echo "✅ Dependencies updated!"
fi

# Step 3: Create .env if needed
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << 'EOF'
DATABASE_URL=postgresql://quack:quack@localhost:5432/quack
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600
MODEL_ID=IDEA-Research/grounding-dino-base
DETECTION_THRESHOLD=0.3
TEXT_QUERIES=a mask. a glove. a hairnet.
UPLOAD_FOLDER=uploads
DETECTION_OUTPUT_FOLDER=detected_frames
EOF
    echo "✅ .env file created!"
fi

# Step 4: Initialize database
echo "🗄️  Initializing database..."
source venv/bin/activate
python -c "from database import init_db; init_db(); print('✅ Database initialized!')"

# Step 5: Test the system
echo "🧪 Testing the system..."
python -c "
from database import UserService, PersonalEntryService
users = UserService.get_all()
entries = PersonalEntryService.get_all()
print(f'✅ Database test: {len(users)} users, {len(entries)} entries')
"

# Step 6: Start the API
echo "🚀 Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the API server"
echo "==================="

# Start the API server (this will run in foreground)
python main.py
