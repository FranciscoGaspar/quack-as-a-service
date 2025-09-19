# 📦 API Collections for Testing Tools

Ready-to-import collections for popular API testing tools.

## 🚀 Available Collections

### 📮 Postman Collection

- **File**: `postman_collection.json`
- **Format**: Postman Collection v2.1
- **Features**: Organized folders, environment variables, sample workflows

### 🌙 Insomnia Collection

- **File**: `insomnia_collection.json`
- **Format**: Insomnia v4 Export
- **Features**: Request groups, environment support, clean interface

## 📥 How to Import

### Postman Import

1. **Open Postman**
2. **Click Import** (top left)
3. **Upload Files** → Select `postman_collection.json`
4. **Import** → Collection appears in sidebar
5. **Set Environment**:
   - Create new environment
   - Add variable: `baseUrl` = `http://localhost:8000`

### Insomnia Import

1. **Open Insomnia**
2. **Click** the workspace dropdown
3. **Import/Export** → **Import Data**
4. **From File** → Select `insomnia_collection.json`
5. **Import** → Collection appears in workspace
6. **Environment is auto-configured** with `baseUrl`

## 🗂️ Collection Structure

### 📂 Organized Folders

```
🦆 Quack as a Service API/
├── 🏥 Health Endpoints
│   ├── Root Health Check
│   └── Detailed Health Check
├── 👥 User Management
│   ├── Create User
│   ├── Get All Users
│   ├── Get User by ID
│   ├── Update User
│   └── Delete User
├── 🏠 Personal Entries
│   ├── Create Entry (Compliant)
│   ├── Create Entry (Non-Compliant)
│   ├── Create Entry (Anonymous)
│   ├── Get All Entries
│   ├── Get Entries (Limited)
│   ├── Get Entry by ID
│   ├── Update Entry
│   └── Delete Entry
├── 🔧 Equipment Updates
│   ├── Fix Missing Equipment
│   └── Remove Equipment
├── 🔍 Query Endpoints
│   ├── Get User's Entries
│   ├── Get User's Entries (Limited)
│   ├── Get Room's Entries
│   └── Get Room's Entries (Limited)
├── ⚠️ Error Test Cases
│   ├── Create User - Empty Name
│   ├── Create User - Missing Name
│   ├── Create Entry - Missing Room Name
│   ├── Create Entry - Invalid User ID
│   ├── Get Non-Existent User
│   ├── Get Non-Existent Entry
│   └── Get Non-Existent User's Entries
└── 📊 Sample Workflow (Postman only)
    ├── 1. Create Test User - John
    ├── 2. Create Test User - Jane
    ├── 3. John Enters Lab (Non-Compliant)
    ├── 4. Fix John's Equipment
    ├── 5. Jane Enters Clean Room (Compliant)
    ├── 6. Check Lab Entries
    ├── 7. Check John's History
    └── 8. Final System Health
```

## 🎯 Quick Start Workflow

### 1. Import Collection

Choose your preferred tool and import the corresponding JSON file.

### 2. Start Your API

```bash
./start.sh  # Starts database + API at localhost:8000
```

### 3. Test Basic Endpoints

- **Health Check**: `GET /health`
- **Create User**: `POST /users`
- **Create Entry**: `POST /entries`

### 4. Run Complete Workflow (Postman)

Execute the "📊 Sample Workflow" folder requests in order to see a complete user journey.

## 🔧 Environment Variables

Both collections use a `baseUrl` variable:

| Variable  | Value                   | Description         |
| --------- | ----------------------- | ------------------- |
| `baseUrl` | `http://localhost:8000` | API server base URL |

**To change the API URL**: Update the `baseUrl` variable in your tool's environment settings.

## 📋 Pre-configured Request Examples

### ✅ Compliant Entry

```json
{
  "user_id": 1,
  "room_name": "Laboratory A",
  "equipment": {
    "mask": true,
    "right_glove": true,
    "left_glove": true,
    "hairnet": true,
    "safety_glasses": true
  }
}
```

### ⚠️ Non-Compliant Entry

```json
{
  "user_id": 2,
  "room_name": "Laboratory B",
  "equipment": {
    "mask": true,
    "right_glove": true,
    "left_glove": false,
    "hairnet": false,
    "safety_glasses": true
  }
}
```

### 🔧 Equipment Fix

```json
{
  "left_glove": true,
  "hairnet": true
}
```

## 🧪 Testing Tips

### Postman Tips

- **Run Collection**: Use Collection Runner for automated testing
- **Use Variables**: Click on `{{baseUrl}}` to verify environment
- **Check Tests**: Some requests include basic response validation
- **Export Results**: Save test results after running

### Insomnia Tips

- **Send & Download**: Right-click requests for more options
- **Request Chaining**: Use response values in subsequent requests
- **Code Generation**: Generate cURL/code snippets easily
- **Plugin Support**: Install plugins for enhanced functionality

## 🔄 Alternative Testing Methods

If you prefer other tools:

1. **cURL**: Use `curl_examples.md` for copy-paste commands
2. **CLI Script**: Run `./test_endpoints.sh` for automated testing
3. **Python**: Use `backend/test_api.py` for programmatic testing
4. **Browser**: Visit `http://localhost:8000/docs` for Swagger UI

## 🐛 Troubleshooting

### Collection Import Issues

- **Verify JSON format**: Ensure files aren't corrupted
- **Check tool version**: Use recent versions of Postman/Insomnia
- **Try alternative formats**: Use cURL examples if import fails

### Request Failures

- **Check API status**: Ensure API is running (`./start.sh`)
- **Verify base URL**: Confirm `baseUrl` matches your setup
- **Database connection**: Run health check first
- **Check request body**: Ensure JSON formatting is correct

### Environment Issues

- **Missing variables**: Verify `baseUrl` is set correctly
- **Wrong port**: Default is 8000, check your API startup logs
- **Network issues**: Try `curl http://localhost:8000/health`

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Architecture Guide**: `backend/ARCHITECTURE.md`
- **cURL Examples**: `curl_examples.md`
- **Test Scripts**: `test_endpoints.sh`
