#!/bin/bash

echo "🦆 Starting Quack as a Service..."
echo "================================="

# Step 1: Start PostgreSQL
echo "📦 Starting PostgreSQL database..."
docker-compose up -d db
sleep 5

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
    echo "✅ Dependencies updated!"
fi

# Step 3: Create .env if needed
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://quack:quack@localhost:5432/quack
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600

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

# Step 4: Initialize database
echo "🗄️  Initializing database..."
source venv-ml/bin/activate
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
