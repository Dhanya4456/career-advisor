from functools import lru_cache
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Always read backend/.env, no matter which folder the server is started from
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8-sig",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ────────────────────────────────────────────
    app_name: str = "AI Career Advisor"
    app_version: str = "1.0.0"
    debug: bool = False
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # ── MongoDB ────────────────────────────────────────
    mongodb_uri: str
    mongodb_database: str = "career_advisor"

    # ── Authentication ─────────────────────────────────
    jwt_secret: str = Field(min_length=32)
    jwt_expire_minutes: int = 60 * 24 * 7

    # ── Google Gemini ──────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    gemini_timeout_seconds: int = Field(default=120, ge=5, le=300)

    # ── File Upload ────────────────────────────────────
    max_file_size_mb: int = 10
    upload_dir: str = "uploads"

    @field_validator("mongodb_uri")
    @classmethod
    def _check_mongodb_uri(cls, value: str) -> str:
        value = (value or "").strip().strip("\"'")
        if not value.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MONGODB_URI must start with mongodb:// or mongodb+srv:// (set it in backend/.env)")
        if "<" in value or ">" in value:
            raise ValueError(
                "MONGODB_URI still contains placeholders like <username>/<password>; "
                "paste your real MongoDB Atlas connection string into backend/.env"
            )
        return value

    @field_validator("jwt_secret")
    @classmethod
    def _check_jwt_secret(cls, value: str) -> str:
        if value.lower().startswith("replace-with"):
            raise ValueError("JWT_SECRET is still the .env.example placeholder; set your own random secret in backend/.env")
        return value

    @field_validator("gemini_api_key", mode="before")
    @classmethod
    def _clean_gemini_key(cls, value):
        return (value or "").strip().strip("\"'")

    @field_validator("gemini_model", mode="before")
    @classmethod
    def _clean_gemini_model(cls, value):
        return (value or "").strip() or "gemini-3.8-flash"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
