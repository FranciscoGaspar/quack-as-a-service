# 🦆 Quack as a Service

<img width="1024" height="1024" alt="ChatGPT Image Sept 19 2025 from Team Suggestion (2)" src="https://github.com/user-attachments/assets/b1dc517b-3ad2-4113-bf3f-609d724f77bc" />

**A PostgreSQL database system for tracking personal security equipment compliance when entering rooms.**

> 📖 **[Complete Setup Guide →](SETUP.md)** | 🔍 **[API Documentation →](http://localhost:8000/docs)**

## 🚀 Quick Start

```bash
# Clone and start everything
git clone <your-repo>
cd quack-as-a-service
./start.sh
```

## 🛠️ What's Inside

- **FastAPI REST API** - Modern, fast API with clean architecture
- **PostgreSQL Database** - Room entry tracking with equipment compliance
- **SQLAlchemy ORM** - Clean database models and services
- **Docker Compose** - Easy PostgreSQL setup
- **Modular Design** - Organized routes, config, and business logic
- **Automatic API Docs** - Swagger UI at `/docs`

## 💻 Usage Example

### API Usage (HTTP)

```bash
# Create user
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe"}'

# Track room entry with equipment
curl -X POST "http://localhost:8000/entries" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "room_name": "Laboratory A",
    "equipment": {
      "mask": true,
      "right_glove": true,
      "left_glove": false,
      "hairnet": true
    }
  }'

# Get all entries
curl "http://localhost:8000/entries"
```

### Python SDK Usage

```python
from database import UserService, PersonalEntryService

# Create user
user = UserService.create(name="John Doe")

# Track room entry with equipment
entry = PersonalEntryService.create(
    user_id=user.id,
    room_name="Laboratory A",
    equipment={
        "mask": True,
        "right_glove": True,
        "left_glove": False,  # Missing!
        "hairnet": True
    }
)

# Check compliance
print(f"Compliant: {entry.is_compliant()}")  # False
print(f"Missing: {entry.get_missing_equipment()}")  # ['left_glove']
```

## 📁 Project Structure

```
quack-as-a-service/
├── docker-compose.yml       # PostgreSQL database
├── start.sh / stop.sh       # Easy start/stop scripts
└── backend/
    ├── main.py              # Clean FastAPI app setup (76 lines!)
    ├── core/                # Configuration & settings
    ├── api/routes/          # Organized route handlers
    │   ├── health.py        # Health check endpoints
    │   ├── users.py         # User management endpoints
    │   └── entries.py       # Room entry endpoints
    ├── database/            # SQLAlchemy models & services
    ├── schemas.py           # Pydantic validation models
    ├── run_api.py           # Standalone API runner
    ├── test_api.py          # Automated API tests
    ├── ARCHITECTURE.md      # Architecture documentation
    ├── postman_collection.json      # Postman collection import
    └── insomnia_collection.json     # Insomnia collection import
```

## 🗄️ Database Schema

- **users** - ID, name, timestamps
- **personal_entries** - ID, user_id, room_name, equipment (JSON), timestamps

Equipment JSON tracks: `mask`, `right_glove`, `left_glove`, `hairnet`, `safety_glasses`, etc.

## ⚡ Commands

```bash
./start.sh                   # Start everything (DB + API)
./stop.sh                    # Stop database
docker-compose ps            # Check status

# API Testing
./test_endpoints.sh          # Test all API endpoints with cURL
curl http://localhost:8000/health                    # Quick health check
open http://localhost:8000/docs                      # Interactive API docs

# Import to API Tools
# Import postman_collection.json into Postman
# Import insomnia_collection.json into Insomnia

# Manual API startup
cd backend && python run_api.py                      # Start API only
cd backend && python test_api.py                     # Automated API tests
```

## 🔧 Development

```bash
cd backend
source venv/bin/activate     # Activate Python environment

# API Development
python run_api.py            # Start API server
python example_usage.py     # Test database SDK

# API Testing
curl http://localhost:8000/health
curl http://localhost:8000/users
curl http://localhost:8000/entries

# API Seed
python seed_custom.py --clean --all 6

```

## 📚 API Documentation

Once the API is running, visit:

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Main Endpoints

- `GET /users` - List all users
- `POST /users` - Create user
- `GET /entries` - List all entries
- `POST /entries` - Create entry
- `GET /rooms/{room_name}/entries` - Get room entries
- `PATCH /entries/{id}/equipment` - Update equipment

#### Team:

- Guido Pereira
- Francisco Gaspar
- Francisco Oliveira
- João Ferreira
