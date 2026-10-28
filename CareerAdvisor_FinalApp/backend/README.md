# AI Career Advisor Backend

FastAPI backend with MongoDB Atlas persistence, MongoDB-backed accounts and JWT authentication, and Google Gemini AI features.

## Requirements

- Python 3.11 or newer
- MongoDB Atlas cluster and database user
- Google AI Studio API key for AI endpoints

## Setup (Windows PowerShell)

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set:

- `MONGODB_URI`: Atlas connection string from **Connect > Drivers**. URL-encode special characters in the database user's password.
- `MONGODB_DATABASE`: database name, default `career_advisor`.
- `JWT_SECRET`: a private random value of at least 32 characters.
- `GEMINI_API_KEY`: key from Google AI Studio. It remains on the backend.
- `ALLOWED_ORIGINS`: comma-separated frontend origins.

In Atlas, add the development machine's IP to Network Access and create a database user with read/write access. Collections and indexes are created automatically when the backend starts. Existing SQL data is not automatically copied; export and migrate it separately if you need to retain existing accounts or results.

## Run

```powershell
python diagnose.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: `http://localhost:8000/docs`  
Health: `http://localhost:8000/health`

The health endpoint returns HTTP 503 when MongoDB cannot be reached. The diagnostics check the MongoDB connection and report whether Gemini is configured; a real Gemini response is verified by using an AI endpoint.

## Data and security

Each profile and result document is keyed by a generated user ID. All history reads, updates, and deletes filter by the authenticated user. Chat messages are embedded in their owner-scoped chat session. Passwords are stored as PBKDF2 hashes; JWT signing uses `JWT_SECRET`. Do not commit `.env` files or share secrets.

The API keeps the existing `/api/v1` routes and response fields. Authentication endpoints are `POST /api/v1/auth/register` and `POST /api/v1/auth/login`; use the returned bearer token for protected routes.