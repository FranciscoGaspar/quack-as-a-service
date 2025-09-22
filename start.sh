#!/bin/bash

echo "🦆 Starting Quack as a Service..."
echo "================================="

# Step 2: Check if backend is set up with ML dependencies
cd backend
if [ ! -d "venv-ml" ]; then
    echo "⚙️  Setting up backend ML environment..."
    python3 -m venv venv-ml
    source venv-ml/bin/activate
    pip install -r requirements.txt
    pip install -r requirements-ml.txt
    echo "✅ Backend ML environment ready!"
else
    echo "✅ Backend ML environment already exists!"
    source venv-ml/bin/activate
    pip install -r requirements.txt  # Update dependencies
    pip install -r requirements-ml.txt
    echo "✅ Dependencies updated!"
fi

# Step 3: Create .env if needed
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://quack:quackquack@localhost:5432/quack
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600

# Migration Configuration
RUN_MIGRATIONS=true  # Set to false to skip auto-migrations on startup

# AI Model Configuration
MODEL_ID=IDEA-Research/grounding-dino-base
DETECTION_THRESHOLD=0.3
TEXT_QUERIES=a mask. a glove. a hairnet.

# File Storage Configuration
UPLOAD_FOLDER=uploads
DETECTION_OUTPUT_FOLDER=detected_frames

# AWS S3 Configuration (Required for image uploads)
# Replace with your actual AWS credentials and bucket name
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
S3_BUCKET_NAME=your-s3-bucket-name
AWS_REGION=us-east-1
EOF
    echo "✅ .env file created!"
    echo ""
    echo "⚠️  AWS S3 Configuration Required!"
    echo "📝 Please edit backend/.env and add your AWS credentials:"
    echo "   - AWS_ACCESS_KEY_ID=your_actual_key"
    echo "   - AWS_SECRET_ACCESS_KEY=your_actual_secret" 
    echo "   - S3_BUCKET_NAME=your_bucket_name"
    echo "   - AWS_REGION=your_preferred_region"
    echo ""
fi

# Step 4: Initialize database and run migrations
echo "🗄️  Initializing database..."
source venv-ml/bin/activate

# Create basic tables first
python -c "from database.connection import init_db; init_db(); print('✅ Database tables created!')"

# Run any pending migrations (can be disabled with RUN_MIGRATIONS=false)
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "📋 Running database migrations..."
    if python3 database/migrate.py; then
        echo "✅ All migrations completed successfully!"
    else
        echo "⚠️  Some migrations had issues - check output above"
    fi
else
    echo "⏭️  Skipping migrations (RUN_MIGRATIONS=false)"
fi

echo "✅ Database initialization complete!"

# Step 5: Test the system
echo "🧪 Testing the system..."
python -c "
from database.services import UserService, PersonalEntryService, RoomEquipmentConfigurationService

users = UserService.get_all()
entries = PersonalEntryService.get_all()
configs = RoomEquipmentConfigurationService.get_all()
print(f'✅ Database test: {len(users)} users, {len(entries)} entries, {len(configs)} room configurations')

# Test approval system
if configs:
    print('✅ Room Approval System: ACTIVE')
    for config in configs[:3]:  # Show first 3 configs
        print(f'   - {config.room_name}: {config.entry_threshold}% threshold')
else:
    print('⚠️  Room Approval System: No configurations found')
"

# Step 6: Start the API
echo "🚀 Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Room Configurations API: http://localhost:8000/room-configurations"
echo ""

# Set PyTorch MPS fallback for fall detection compatibility
export PYTORCH_ENABLE_MPS_FALLBACK=1
echo "🍎 MPS fallback enabled for Apple Silicon compatibility"

# Start the API server in background
echo "Starting API server in background..."
python main.py &
API_PID=$!
echo "✅ API server started (PID: $API_PID)"
sleep 3

cd ..

# Step 7: Setup and start Frontend
echo "🌐 Setting up Frontend..."
cd frontend

# Install frontend dependencies if not already installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
    echo "✅ Frontend dependencies installed!"
else
    echo "✅ Frontend dependencies already installed!"
fi

# Start the frontend
echo "🚀 Starting Next.js frontend..."
echo "Frontend will be available at: http://localhost:3000"
echo "Room Configurations: http://localhost:3000/room-configurations"
echo ""
echo "🎉 ROOM APPROVAL SYSTEM FEATURES:"
echo "   • Room equipment configurations with weights"
echo "   • Automatic entry approval/denial based on thresholds"
echo "   • Real-time analytics and performance tracking"
echo "   • Enhanced factory entries with approval status"
echo ""
echo "Press Ctrl+C to stop all services"
echo "==================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $API_PID 2>/dev/null
    exit 0
}
trap cleanup INT

# Start the frontend (this will run in foreground)
npm run dev
