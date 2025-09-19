# 🦆 Quack as a Service - Database Layer

A PostgreSQL database layer for tracking personal security equipment compliance when entering rooms.

## 🏗️ Architecture

- **Database**: PostgreSQL with SQLAlchemy ORM
- **Object Detection Integration**: Ready for ML model results
- **Service Layer**: High-level database operations

## 📦 Components

### Database Models

- **User**: People using the system (ID, name, timestamps)
- **PersonalEntry**: Equipment tracking when entering rooms (ID, user_id, room_name, timestamps, image_url, equipment JSON)

### Equipment Tracking

The `equipment` field in `PersonalEntry` is a JSON object tracking:

- `mask`: Boolean
- `right_glove`: Boolean
- `left_glove`: Boolean
- `hairnet`: Boolean
- `safety_glasses`: Boolean
- Additional equipment as needed

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Git

### Super Simple Setup

1. **One command start (from project root):**
   ```bash
   ./start.sh
   ```
   This does everything: starts database, sets up environment, initializes DB!

### Manual Setup

1. **Start PostgreSQL with Docker:**

   ```bash
   docker-compose up -d db
   ```

2. **Set up backend:**

   ```bash
   cd backend
   ./setup_env.sh
   ```

3. **Test it works:**
   ```bash
   source venv/bin/activate
   python example_usage.py
   ```

### Manual Setup (Alternative)

1. **Create virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL settings
   ```

3. **Initialize database:**
   ```bash
   python init_db.py
   ```

## 🗄️ Database Configuration

### Docker Compose Setup (Recommended)

The project includes a `docker-compose.yml` that sets up PostgreSQL automatically:

```bash
# Start database
docker-compose up -d db

# Check it's running
docker-compose ps

# Stop database
docker-compose down
```

**Database credentials:**

- Host: `localhost:5432`
- Database: `quack`
- Username: `quack`
- Password: `quack`

### Manual PostgreSQL Setup (Alternative)

If you prefer local PostgreSQL:

1. **Install and create database:**

   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   createdb quack
   ```

2. **Update .env file:**
   ```bash
   DATABASE_URL=postgresql://quack:quack@localhost:5432/quack
   ```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database (matches Docker Compose)
DATABASE_URL=postgresql://quack:quack@localhost:5432/quack
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600

# Object Detection
MODEL_ID=IDEA-Research/grounding-dino-base
DETECTION_THRESHOLD=0.3
TEXT_QUERIES=a mask. a glove. a hairnet.

# File Storage
UPLOAD_FOLDER=uploads
DETECTION_OUTPUT_FOLDER=detected_frames
MAX_CONTENT_LENGTH=16777216

# Camera Configuration
DEFAULT_CAMERA_INDEX=0
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
CAMERA_FPS=30
```

## 💻 Usage Examples

### Basic CRUD Operations

```python
from database import UserService, PersonalEntryService

# User CRUD
user = UserService.create(name="John Doe")
user = UserService.get_by_id(user.id)
users = UserService.get_all()
user = UserService.update(user.id, name="John Smith")
UserService.delete(user.id)

# Personal Entry CRUD
entry = PersonalEntryService.create(
    user_id=user.id,
    room_name="Laboratory A",
    equipment={
        "mask": True,
        "right_glove": True,
        "left_glove": False,
        "hairnet": True
    },
    image_url="/path/to/image.jpg"
)

# Read entries
entry = PersonalEntryService.get_by_id(entry.id)
entries = PersonalEntryService.get_all()
user_entries = PersonalEntryService.get_by_user(user.id)
room_entries = PersonalEntryService.get_by_room("Laboratory A")

# Update entry
entry = PersonalEntryService.update(entry.id, room_name="Lab A - Section 2")
PersonalEntryService.update_equipment(entry.id, mask=True, left_glove=True)

# Delete entry
PersonalEntryService.delete(entry.id)

# Check compliance
is_compliant = entry.is_compliant()  # False (missing left_glove)
missing_items = entry.get_missing_equipment()  # ['left_glove']
```

### Room-Based Queries

```python
# Get all entries for a specific room
lab_entries = PersonalEntryService.get_by_room("Laboratory A")
clean_room_entries = PersonalEntryService.get_by_room("Clean Room B")

# Get recent entries across all rooms
recent_entries = PersonalEntryService.get_all(limit=10)
```

## 📊 Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Personal entries table
CREATE TABLE personal_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    room_name VARCHAR(100) NOT NULL,
    image_url VARCHAR(500),
    equipment JSONB NOT NULL DEFAULT '{}',
    entered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 🛠️ Service Classes (Basic CRUD)

### UserService

- `create(name)` - Create new user
- `get_by_id(user_id)` - Get user by ID
- `get_all()` - Get all users
- `update(user_id, name)` - Update user
- `delete(user_id)` - Delete user

### PersonalEntryService

- `create(user_id, room_name, equipment, image_url)` - Create entry
- `get_by_id(entry_id)` - Get entry by ID
- `get_all(limit)` - Get all entries
- `get_by_user(user_id, limit)` - Get user's entries
- `get_by_room(room_name, limit)` - Get room's entries
- `update(entry_id, room_name, equipment, image_url)` - Update entry
- `update_equipment(entry_id, **equipment)` - Update specific equipment
- `delete(entry_id)` - Delete entry

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**

   - Check PostgreSQL is running: `docker-compose ps`
   - Verify DATABASE_URL in .env file: `postgresql://quack:quack@localhost:5432/quack`
   - Test connection: `docker exec -it quack-db psql -U quack -d quack`

2. **Import Errors**

   - Activate virtual environment: `source venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

3. **Permission Errors**
   - Ensure database user has proper permissions
   - Check database and user exist

## 📄 License

[Add your license here]
