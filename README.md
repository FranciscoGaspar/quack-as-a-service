# 🦆 Quack as a Service

<img width="1024" height="1024" alt="ChatGPT Image Sept 19 2025 from Team Suggestion (2)" src="https://github.com/user-attachments/assets/b1dc517b-3ad2-4113-bf3f-609d724f77bc" />

**A PostgreSQL database system for tracking personal security equipment compliance when entering rooms.**

## 🚀 Quick Start

```bash
# Clone and start everything
git clone <your-repo>
cd quack-as-a-service
./start.sh
```

## 🛠️ What's Inside

- **PostgreSQL Database** - Room entry tracking with equipment compliance
- **SQLAlchemy ORM** - Clean database models and services
- **Docker Compose** - Easy PostgreSQL setup
- **Basic CRUD API** - User and PersonalEntry management

## 💻 Usage Example

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
    ├── database/            # SQLAlchemy models & services
    ├── example_usage.py     # Try this first!
    ├── requirements.txt     # Python dependencies
    └── .env                 # Database configuration
```

## 🗄️ Database Schema

- **users** - ID, name, timestamps
- **personal_entries** - ID, user_id, room_name, equipment (JSON), timestamps

Equipment JSON tracks: `mask`, `right_glove`, `left_glove`, `hairnet`, `safety_glasses`, etc.

## ⚡ Commands

```bash
./start.sh                   # Start everything
./stop.sh                    # Stop database
docker-compose ps            # Check status
cd backend && python example_usage.py  # Test database
```

## 🔧 Development

```bash
cd backend
source venv/bin/activate     # Activate Python environment
python example_usage.py     # Test the database
```

#### Team:

- Guido Pereira
- Francisco Gaspar
- Francisco Oliveira
- João Ferreira
