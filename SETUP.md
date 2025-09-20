# 🦆 Quack as a Service - Setup Guide

## Quick Start

```bash
# Clone and start the application
git clone <your-repo-url>
cd quack-as-a-service
./start.sh
```

The startup script will automatically:
- ✅ Set up the ML virtual environment (`backend/venv-ml/`)
- ✅ Install all dependencies (API + ML)
- ✅ Start PostgreSQL database
- ✅ Initialize database tables
- ✅ Start the FastAPI server

## 🐍 Virtual Environment Setup

This project uses **two approaches** for Python dependencies:

### Option 1: Automated Setup (Recommended)
```bash
./start.sh  # Handles everything automatically
```

### Option 2: Manual Setup
```bash
cd backend

# Create ML-compatible virtual environment
python3 -m venv venv-ml
source venv-ml/bin/activate

# Install all dependencies
pip install -r requirements.txt      # Core API dependencies
pip install -r requirements-ml.txt   # ML dependencies (PyTorch, etc.)

# Run the application
python run_api.py
```

## 🤖 ML Dependencies

### Why venv-ml?
- **Python Compatibility**: PyTorch requires Python ≤ 3.12, but you might have Python 3.13+
- **Heavy Dependencies**: ML libraries (PyTorch, transformers) are large and optional
- **Clean Separation**: Core API works without ML, with graceful fallback

### What's Included:
- **PyTorch** (CPU version for object detection)
- **Transformers** (Hugging Face for GroundingDINO model)
- **Computer Vision** libraries (OpenCV, matplotlib)

## 🗃️ Database Setup

PostgreSQL is required and managed via Docker:

```bash
# Start database only
docker-compose up -d db

# Initialize tables
cd backend
source venv-ml/bin/activate
python -c "from database import init_db; init_db()"
```

## 🔧 Configuration

### Environment Variables (`backend/.env`):
```bash
# Database
DATABASE_URL=postgresql://quack:quack@localhost:5432/quack

# AI Model
MODEL_ID=IDEA-Research/grounding-dino-base
DETECTION_THRESHOLD=0.3
TEXT_QUERIES=a mask. a glove. a hairnet.

# AWS S3 (Optional - for image storage)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
```

## 🚀 API Endpoints

Once running, access:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

### Key Endpoints:
- `POST /entries/upload-image` - Upload image for AI analysis
- `GET /entries` - List all safety entries
- `GET /users/{user_id}/entries` - User-specific entries

## 🧪 Testing ML Functionality

```bash
cd backend
source venv-ml/bin/activate

# Test ML dependencies
python -c "import image_detection; print('✅ ML setup working!')"

# Test API with ML
python run_api.py
# Upload a test image via /docs interface
```

## 🛠️ Development

### Project Structure:
```
backend/
├── venv-ml/           # ML virtual environment (ignored by Git)
├── api/routes/        # FastAPI route handlers
├── database/          # Database models and services
├── image_detection.py # AI object detection logic
├── requirements.txt   # Core API dependencies
└── requirements-ml.txt # ML-specific dependencies
```

### Adding Dependencies:
- **Core API**: Add to `requirements.txt`
- **ML Features**: Add to `requirements-ml.txt`
- **Always**: Test with both environments

## 🔍 Troubleshooting

### "ML dependencies not available"
```bash
# Ensure you're using venv-ml
cd backend
source venv-ml/bin/activate
pip install -r requirements-ml.txt
```

### "PyTorch not found"
```bash
# Python version check
python --version  # Should be ≤ 3.12 for PyTorch compatibility

# Reinstall in compatible environment
python3.12 -m venv venv-ml
source venv-ml/bin/activate
pip install -r requirements-ml.txt
```

### "Database connection error"
```bash
# Start PostgreSQL
docker-compose up -d db

# Wait a moment, then test
cd backend && source venv-ml/bin/activate
python -c "from database import init_db; init_db()"
```

## 📝 Git Best Practices

### Virtual environments are NOT tracked:
```gitignore
# Already in .gitignore
backend/venv/
backend/venv-ml/
```

### If accidentally tracked:
```bash
git rm --cached -r backend/venv-ml/
git commit -m "Remove venv from tracking"
```

## 🎯 Production Deployment

1. **Environment Setup**: Use `venv-ml` approach
2. **Dependencies**: Install both `requirements.txt` files  
3. **Database**: PostgreSQL with proper connection string
4. **Storage**: Configure AWS S3 for image storage
5. **Security**: Update default database credentials

---

**Need help?** Check the [API documentation](http://localhost:8000/docs) or open an issue.
