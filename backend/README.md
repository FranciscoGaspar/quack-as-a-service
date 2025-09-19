# 🦆 Quack as a Service - Database Layer

A PostgreSQL database layer for tracking personal security equipment compliance when entering rooms.

## 🏗️ Architecture

- **Database**: PostgreSQL with SQLAlchemy ORM
- **Object Detection Integration**: Ready for ML model results
- **Service Layer**: High-level database operations

## 📦 Components

### Database Models

- **User**: People using the system (ID, name, timestamps)
- **PersonalEntry**: Equipment tracking when entering rooms (ID, user_id, timestamps, image_url, equipment JSON)

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
- PostgreSQL 12+
- pip

### Setup

1. **Run the automated setup script:**

   ```bash
   cd backend
   ./setup_env.sh
   ```

2. **Configure your database:**

   - Edit `.env` file with your PostgreSQL credentials
   - Example: `DATABASE_URL=postgresql://username:password@localhost:5432/quack_service`

3. **Initialize database:**
   ```bash
   python init_db.py
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

### PostgreSQL Setup

1. **Install PostgreSQL:**

   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql

   # Ubuntu
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Create database and user:**

   ```sql
   -- Connect to PostgreSQL
   psql -U postgres

   -- Create database
   CREATE DATABASE quack_service;

   -- Create user
   CREATE USER quackuser WITH PASSWORD 'quackpass';

   -- Grant permissions
   GRANT ALL PRIVILEGES ON DATABASE quack_service TO quackuser;

   -- Exit
   \q
   ```

3. **Update .env file:**
   ```bash
   DATABASE_URL=postgresql://quackuser:quackpass@localhost:5432/quack_service
   ```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/quack_service
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Object Detection
DETECTION_THRESHOLD=0.3
TEXT_QUERIES=a mask. a glove. a hairnet.

# File Storage
UPLOAD_FOLDER=uploads
DETECTION_OUTPUT_FOLDER=detected_frames
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

## 🛠️ Service Classes

### UserService

- `create_user(name)` - Create new user
- `get_user_by_id(user_id)` - Get user by ID
- `get_all_users()` - Get all users
- `update_user(user_id, name)` - Update user
- `delete_user(user_id)` - Delete user

### PersonalEntryService

- `create_entry(user_id, image_url, equipment)` - Create entry
- `get_entry_by_id(entry_id)` - Get entry by ID
- `get_user_entries(user_id)` - Get user's entries
- `get_recent_entries(limit)` - Get recent entries
- `update_equipment(entry_id, **equipment)` - Update equipment
- `get_compliant_entries()` - Get compliant entries
- `get_non_compliant_entries()` - Get non-compliant entries

### AnalyticsService

- `get_database_stats()` - Overall database statistics
- `get_equipment_statistics()` - Equipment usage stats
- `get_user_statistics(user_id)` - User-specific stats
- `get_daily_statistics(days)` - Daily analytics

### DetectionIntegrationService

- `process_detection_results(user_id, image_url, results)` - Process ML results
- `batch_process_detections(detections)` - Process multiple detections

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**

   - Check PostgreSQL is running: `brew services start postgresql`
   - Verify DATABASE_URL in .env file
   - Test connection: `psql -d quack_service -U your_username`

2. **Import Errors**

   - Activate virtual environment: `source venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

3. **Permission Errors**
   - Ensure database user has proper permissions
   - Check database and user exist

## 📄 License

[Add your license here]
