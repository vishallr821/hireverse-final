# HireVerse — DSA Evaluation Module

## Quick Start (2 commands)
```bash
docker compose up --build
python scripts/smoke_test.py
```
Open: http://localhost:8000

## Manual Start (no Docker Compose)
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Demo Flow (2 minutes)
1. Open http://localhost:8000/login
2. Register with any email + password
3. Click any problem on the Problems page
4. Write or paste a solution in the editor
5. Click Run Tests — see results, complexity, AI feedback
6. If all pass: see follow-up interview question

## Tech Stack
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL (asyncpg), SQLAlchemy, Alembic
- **Caching:** Redis
- **Authentication:** JWT, Passlib (bcrypt)
- **Code Execution:** Docker sandbox with subprocess fallback
- **AI Mentorship:** Groq API (llama-3.3-70b-versatile)
- **Frontend:** Jinja2 Templates, Tailwind CSS (via CDN), Monaco Editor (via CDN), Vanilla JavaScript

## Team
Team Error-404 | SRM TRP Engineering College | HACK-SPRINT 2026
