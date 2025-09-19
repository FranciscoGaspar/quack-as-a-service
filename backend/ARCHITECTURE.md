# 🏗️ API Architecture

Clean, organized FastAPI application structure for maintainability and scalability.

## 📂 Directory Structure

```
backend/
├── main.py                  # FastAPI app setup & configuration
├── run_api.py              # Standalone API server launcher
├── schemas.py              # Pydantic models for validation
├── test_api.py             # API testing script
├── core/                   # Core application configuration
│   ├── __init__.py
│   └── config.py           # Settings & environment variables
├── api/                    # API layer
│   ├── __init__.py
│   └── routes/             # Route handlers by domain
│       ├── __init__.py
│       ├── health.py       # Health check endpoints
│       ├── users.py        # User management endpoints
│       └── entries.py      # Personal entry endpoints
└── database/               # Data layer
    ├── __init__.py
    ├── connection.py       # Database connection management
    ├── models.py           # SQLAlchemy ORM models
    └── services.py         # Business logic & CRUD operations
```

## 🎯 Design Principles

### 1. **Separation of Concerns**

- **Routes**: Handle HTTP requests/responses only
- **Services**: Business logic and database operations
- **Models**: Data structure definitions
- **Config**: Environment and application settings

### 2. **Single Responsibility**

- Each module has one clear purpose
- Routes are grouped by domain (users, entries, health)
- Configuration is centralized

### 3. **Easy Testing**

- Clear interfaces between layers
- Dependency injection ready
- Isolated route testing possible

### 4. **Maintainability**

- Small, focused files
- Clear import paths
- Consistent patterns

## 🔌 How It Works

### 1. **Application Setup** (`main.py`)

```python
from core.config import settings
from api.routes import health, users, entries

app = FastAPI(title=settings.API_TITLE, ...)
app.include_router(health.router)
app.include_router(users.router)
app.include_router(entries.router)
```

### 2. **Route Definition** (`api/routes/users.py`)

```python
from database.services import UserService
from schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserResponse)
async def create_user(user: UserCreate):
    db_user = UserService.create(name=user.name)
    return UserResponse.model_validate(db_user)
```

### 3. **Configuration** (`core/config.py`)

```python
class Settings:
    API_TITLE: str = "🦆 Quack as a Service API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "...")

settings = Settings()
```

## 🚀 Benefits

- ✅ **Easy to Navigate** - Find code quickly by domain
- ✅ **Easy to Test** - Test routes independently
- ✅ **Easy to Extend** - Add new routes/domains cleanly
- ✅ **Easy to Maintain** - Small files, clear responsibilities
- ✅ **Easy to Scale** - Add features without complexity

## 📝 Adding New Features

### New Route Group

1. Create `api/routes/new_domain.py`
2. Define router with endpoints
3. Add to `main.py`: `app.include_router(new_domain.router)`

### New Endpoint

1. Add to appropriate route file
2. Use existing services or create new ones
3. Add Pydantic schemas if needed

### New Configuration

1. Add to `core/config.py`
2. Use throughout the app via `settings`

## 🧪 Testing

```bash
# Test structure
python -c "from main import app; print('✅ Structure OK')"

# Run API
python run_api.py

# Test endpoints
python test_api.py
```
