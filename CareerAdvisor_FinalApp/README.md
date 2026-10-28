# AI Career Advisor

React/Vite frontend + FastAPI backend, MongoDB Atlas for storage, Google Gemini for AI features, JWT authentication.

## Requirements
Python 3.11+ (3.12 recommended), Node.js 18+, a MongoDB Atlas cluster, a Gemini API key (Google AI Studio).

## Setup

### Backend (Windows PowerShell)
```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env        # then edit .env with your real values
python diagnose.py --gemini        # checks MongoDB + one live Gemini call
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Linux/macOS: `python3 -m venv .venv && source .venv/bin/activate`, `cp .env.example .env`.

### Frontend
```bash
cd frontend/career-advisor
npm install
npm run dev          # http://localhost:5173
```
Optional: copy `.env.example` to `.env` to change `VITE_API_URL` (default `http://localhost:8000/api/v1`).

`start-backend.bat` / `start-frontend.bat` do the same on Windows. API docs: http://localhost:8000/docs, health: http://localhost:8000/health.

## Environment variables
Backend `backend/.env` (never commit; see `backend/.env.example`):

| Variable | Notes |
|---|---|
| `MONGODB_URI` | required; Atlas connection string (URL-encode special characters in the password) |
| `MONGODB_DATABASE` | default `career_advisor` |
| `JWT_SECRET` | required; random, 32+ characters |
| `JWT_EXPIRE_MINUTES` | default 10080 |
| `GEMINI_API_KEY` | required for AI features |
| `GEMINI_MODEL` | default `gemini-3.8-flash` |
| `GEMINI_TIMEOUT_SECONDS` | default 60 |
| `ALLOWED_ORIGINS` | comma-separated frontend origins (CORS) |
| `MAX_FILE_SIZE_MB`, `UPLOAD_DIR`, `APP_NAME`, `APP_VERSION`, `DEBUG` | optional |

Frontend `frontend/career-advisor/.env`: `VITE_API_URL`.

In Atlas: create a read/write database user and add your IP under **Network Access**.

## Tests
```powershell
cd backend
python -m unittest discover -s tests -v
cd ../frontend/career-advisor
npm run build
```
