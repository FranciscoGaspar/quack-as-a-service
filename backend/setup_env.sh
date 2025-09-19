#!/bin/bash

# Backend Environment Setup Script for Quack as a Service
echo "🦆 Setting up Quack as a Service Backend Environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker found: $(docker --version)"
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose found: $(docker-compose --version)"
    else
        echo "⚠️  Docker Compose not found. Install it for easier database management."
    fi
else
    echo "⚠️  Docker not found. You can still use a local PostgreSQL installation."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
else
    echo "📦 Virtual environment already exists!"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads detected_frames logs

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env configuration file..."
    cp .env.example .env
    echo "✅ .env file created!"
else
    echo "⚙️  .env file already exists!"
fi

# Configure PostgreSQL connection
echo ""
echo "🔧 Please configure your PostgreSQL database settings in .env:"
echo "   1. Update DATABASE_URL with your PostgreSQL credentials"
echo "   2. Example: postgresql://username:password@localhost:5432/quack_service"
echo "   3. Make sure the database exists and user has permissions"
echo ""
echo "Sample .env configuration:"
echo "DATABASE_URL=postgresql://quackuser:quackpass@localhost:5432/quack_service"
echo ""
read -p "Press Enter to continue after configuring your .env file..."

# Initialize database
echo "🗄️  Initializing database..."
if python init_db.py; then
    echo "✅ Database initialization completed!"
else
    echo "❌ Database initialization failed. Please check your database connection."
    exit 1
fi

echo ""
echo "🎉 Backend environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure PostgreSQL is running:"
echo "   brew services start postgresql (macOS)"
echo "   sudo systemctl start postgresql (Linux)"
echo ""
echo "2. To activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. To use the database in your code:"
echo "   from database import UserService, PersonalEntryService"
echo ""
echo "4. To start live detection:"
echo "   python live_detection.py"
echo ""
echo "5. View your database:"
echo "   psql -d quack_service -U your_username"
