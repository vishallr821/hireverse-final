# HireVerse DSA - Quick Start Guide

## Initial Setup

### 1. Environment Configuration

The `.env` file has been created with default settings. You can modify it if needed:

```bash
# View the .env file
cat .env

# Or edit it
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Server

```bash
uvicorn main:app --reload --port 8001
```

The server will:
- Create database tables automatically
- Seed sample DSA problems
- Start on http://localhost:8001

## Verify Installation

### Check if server is running:
```bash
# Open in browser
http://localhost:8001/problems
```

You should see the DSA problems list page.

### Test API endpoints:
```bash
# Get all problems
curl http://localhost:8001/dsa/problems

# Get specific problem
curl http://localhost:8001/dsa/problems/1
```

## Integration with Resume Parser

The DSA platform is designed to work with the resume-parser project:

1. **Resume Parser** runs on port 8000
2. **DSA Platform** runs on port 8001
3. They communicate via iframe embedding and API calls

### Testing Integration:

1. Start both servers:
```bash
# Terminal 1 - Resume Parser
cd d:\Final\resume-parser
python manage.py runserver 8000

# Terminal 2 - DSA Platform
cd d:\Final\hireverse-dsa
uvicorn main:app --reload --port 8001
```

2. Complete a test in resume-parser with score >= 50%
3. Click "Send to DSA Round"
4. The DSA interface will load with proctoring active

## Database

The default configuration uses SQLite:
- **File**: `dsa_database.db` (created automatically)
- **Location**: Root of hireverse-dsa folder

### View Database:
```bash
# Install sqlite3 browser or use command line
sqlite3 dsa_database.db

# List tables
.tables

# View problems
SELECT * FROM dsa_problems;

# View submissions
SELECT * FROM dsa_submissions;
```

## Configuration Options

### Change Database (Optional)

For PostgreSQL (production):
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/hireverse_dsa
```

### Enable Docker (Optional)

For code execution in containers:
```env
DOCKER_ENABLED=true
```

Make sure Docker Desktop is running.

### Add Groq API Key (Optional)

For AI-powered feedback:
```env
GROQ_API_KEY=your_actual_api_key
```

Get key from: https://console.groq.com/

## Troubleshooting

### Error: "DATABASE_URL is None"
**Solution**: The .env file is now created. Restart the server.

### Error: "Docker not found"
**Solution**: This is just a warning. Code will run using subprocess fallback.

### Error: "Port 8001 already in use"
**Solution**: 
```bash
# Use different port
uvicorn main:app --reload --port 8002

# Or kill existing process
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8001 | xargs kill -9
```

### Error: "Module not found"
**Solution**:
```bash
pip install -r requirements.txt
```

## API Endpoints

### Problems
- `GET /dsa/problems` - List all problems
- `GET /dsa/problems/{id}` - Get specific problem
- `GET /dsa/problems?difficulty=beginner` - Filter by difficulty
- `GET /dsa/problems?category=arrays` - Filter by category

### Submissions
- `POST /dsa/submit` - Submit solution
  ```json
  {
    "problem_id": 1,
    "language": "python",
    "code": "def solution(arr): return arr"
  }
  ```

### Hints
- `POST /dsa/hint` - Get AI hint
  ```json
  {
    "problem_id": 1,
    "code": "partial code",
    "level": 1
  }
  ```

## Sample Problems

The database is seeded with sample problems:
1. Two Sum (Beginner - Arrays)
2. Reverse String (Beginner - Strings)
3. Binary Tree Inorder (Intermediate - Trees)
4. And more...

## Development

### Add New Problems

Edit `db/seed.py` and add to the problems list:
```python
{
    "title": "Your Problem",
    "difficulty": "beginner",
    "category": "arrays",
    "problem_statement": "Description...",
    # ... more fields
}
```

Then restart the server.

### Modify Templates

Templates are in `web/templates/`:
- `base.html` - Base layout
- `problems.html` - Problems list
- `challenge.html` - Coding interface

### Add New Routes

Add to `api/routes/dsa.py`:
```python
@router.get("/your-endpoint")
async def your_function():
    return {"message": "Hello"}
```

## Production Deployment

### Using Gunicorn + Uvicorn Workers:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Using Docker:
```bash
docker-compose up -d
```

### Environment Variables for Production:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
GROQ_API_KEY=actual_key
SECRET_KEY=strong_random_key
ALLOWED_ORIGINS=https://yourdomain.com
```

## Support

If you encounter issues:
1. Check the terminal for error messages
2. Verify .env file exists and is configured
3. Ensure port 8001 is available
4. Check Python version (3.11+ recommended)
5. Verify all dependencies are installed

## Next Steps

1. ✅ Server is running
2. ✅ Database is created
3. ✅ Sample problems loaded
4. → Test the integration with resume-parser
5. → Customize problems for your needs
6. → Add your Groq API key for AI features
7. → Deploy to production

Enjoy using HireVerse DSA! 🚀
