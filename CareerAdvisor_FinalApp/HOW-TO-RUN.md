# Run the Career Advisor

This workspace contains the existing React/Vite frontend and FastAPI backend. User accounts, profiles, assessments, AI outputs, and chat history are stored in MongoDB; Gemini requests are made only by the backend.

## One-time setup

1. Install Python 3.11+ and Node.js 18+.
2. In `backend`, create and activate a virtual environment, then install dependencies:

   ```powershell
   cd backend
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

3. Configure `backend/.env` with a MongoDB Atlas URI, database name, a private `JWT_SECRET` (at least 32 random characters), and your `GEMINI_API_KEY`. In Atlas, create a read/write database user and allow the machine's IP under Network Access.
4. Configure `ALLOWED_ORIGINS` as a comma-separated list such as `http://localhost:5173,http://127.0.0.1:5173`.
5. In `frontend/career-advisor`, install frontend packages with `npm install`. Set `VITE_API_URL=http://localhost:8000/api/v1` in its `.env` if the API is hosted elsewhere.

## Start

Run `start-backend.bat` and `start-frontend.bat`, or use terminals:

```powershell
# backend
cd backend
.\.venv\Scripts\Activate.ps1
python diagnose.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
# frontend
cd frontend/career-advisor
npm run dev
```

Open `http://localhost:5173`. API docs are at `http://localhost:8000/docs`; `/health` confirms MongoDB connectivity. AI features require a valid Gemini API key. MongoDB collections and indexes are created automatically. Existing data in Supabase/PostgreSQL is not imported automatically.

Keep both `.env` files private. Never put the Gemini key or MongoDB URI in frontend code.

## Verification

The frontend production build and backend auth unit tests can be run locally without cloud credentials:

```powershell
cd frontend/career-advisor
npm run build
cd ../../backend
$env:MONGODB_URI = "mongodb://127.0.0.1:27017"
$env:JWT_SECRET = "test-only-secret-value-that-is-at-least-32-chars"
python -m unittest discover -s tests -v
```

These checks do not prove Atlas connectivity or live Gemini generation. `python diagnose.py` checks MongoDB connectivity using your configured Atlas URI; AI endpoint calls verify Gemini using your key. Existing PostgreSQL/Supabase data is not imported automatically.