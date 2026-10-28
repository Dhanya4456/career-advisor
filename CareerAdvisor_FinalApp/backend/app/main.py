import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.config import get_settings
from app.database import DB_UNAVAILABLE_DETAIL, client, close_database, ensure_database
from app.routers import assessment, auth, career, chat, profile, resume, roadmap, skills

settings = get_settings()
log = logging.getLogger("uvicorn.error")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_ready = False
    if await ensure_database():
        app.state.database_ready = True
        log.info("MongoDB connection OK")
    else:
        log.error(
            "\n\n*** MONGODB NOT REACHABLE ***\n%s\nThe server will keep running and retry on the next request.\n",
            DB_UNAVAILABLE_DETAIL,
        )
    if not (settings.gemini_api_key or "").strip() or settings.gemini_api_key.lower().startswith(("your", "changeme", "xxx")):
        log.warning("GEMINI_API_KEY is not set in backend/.env; AI endpoints will return HTTP 503.")
    # Make sure the skill-quiz question files are present and complete
    try:
        from app.services.assessment import check_bank
        log.info(check_bank())
    except Exception as exc:  # noqa: BLE001
        log.error("\n\n*** SKILL QUIZ PROBLEM ***\n%s\n", exc)
    yield
    await close_database()


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## AI-Powered Career Advisor API

A comprehensive FastAPI backend that powers personalised career guidance using **Google Gemini**.

### Features
- 🔐 **Authentication** — MongoDB-backed accounts and signed JWTs
- 👤 **Student Profile** — Manage degree, skills, interests & goals
- 🎯 **Career Recommendations** — AI-generated role suggestions with salary insights
- 📄 **Resume Analyzer** — ATS scoring, skill extraction, improvement tips
- 🔍 **Skill Gap Analysis** — Compare current vs required skills for any role
- 🗺️ **Learning Roadmap** — Month-by-month plan with projects & certifications
- 💬 **AI Career Chatbot** — Context-aware conversation with full history
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handlers ─────────────────────────────────────────────────
def _cors_headers(request: Request) -> dict:
    # Error responses raised here bypass CORSMiddleware, and without these headers the
    # browser reports "could not reach server" instead of the real error.
    origin = request.headers.get("origin")
    if origin and origin in settings.cors_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}


@app.exception_handler(PyMongoError)
async def database_exception_handler(request: Request, exc: PyMongoError):
    log.error("Database error: %s: %s", type(exc).__name__, str(exc)[:300])
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": DB_UNAVAILABLE_DETAIL},
        headers=_cors_headers(request),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Server error: check the backend terminal for details."},
        headers=_cors_headers(request),
    )


# ── Routers ───────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(auth.router, prefix=PREFIX)
app.include_router(profile.router, prefix=PREFIX)
app.include_router(career.router, prefix=PREFIX)
app.include_router(resume.router, prefix=PREFIX)
app.include_router(skills.router, prefix=PREFIX)
app.include_router(assessment.router, prefix=PREFIX)
app.include_router(roadmap.router, prefix=PREFIX)
app.include_router(chat.router, prefix=PREFIX)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Health check")
async def health():
    if not await ensure_database():
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "disconnected", "app": settings.app_name},
        )
    try:
        await client.admin.command("ping")
    except Exception:  # noqa: BLE001
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "disconnected", "app": settings.app_name},
        )
    app.state.database_ready = True
    return {
        "status": "healthy",
        "database": "connected",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    return {"message": f"Welcome to {settings.app_name} API", "docs": "/docs"}
