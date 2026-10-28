"""Check required environment configuration and external service connectivity.

Usage:
    python diagnose.py            # config + MongoDB check
    python diagnose.py --gemini   # also makes one tiny live Gemini request
"""
import asyncio
import sys

from app.config import get_settings
from app.database import client, initialize_database


async def main() -> int:
    settings = get_settings()
    print(f"Python {sys.version.split()[0]}")
    print(f"Gemini model: {settings.gemini_model}")
    try:
        await initialize_database()
        print("[ OK ] MongoDB connection and indexes are available")
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] MongoDB: {type(exc).__name__}: {str(exc)[:200]}")
        print("       Check MONGODB_URI, Atlas network access, and database credentials.")
        await client.close()
        return 1

    key = settings.gemini_api_key or ""
    if key and not key.lower().startswith(("your", "changeme", "xxx")):
        if "--gemini" in sys.argv:
            from app.services.gemini import generate
            try:
                reply = await generate("Reply with the single word: OK")
                print(f"[ OK ] Gemini responded: {reply.strip()[:40]!r}")
            except Exception as exc:  # noqa: BLE001
                print(f"[FAIL] Gemini: {getattr(exc, 'detail', exc)}")
                await client.close()
                return 1
        else:
            print("[ OK ] Gemini API key is configured (run with --gemini for a live test)")
    else:
        print("[WARN] GEMINI_API_KEY is not configured; AI endpoints will return HTTP 503")
    await client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
