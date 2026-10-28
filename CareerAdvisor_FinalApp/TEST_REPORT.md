# Test report

**Environment limit:** the build sandbox had no internet access (pip and npm both failed with DNS errors), so no dependencies could be installed. The frontend build, the backend server, the unit tests, MongoDB Atlas and Gemini were **not run**. Nothing below should be read as "runs end to end"; please run the commands in README.md first.

## Verified (static checks / offline tests)
- All backend `.py` files parse (`py_compile`/AST).
- Every frontend API call (`/auth/login`, `/auth/register`, `/profile`, `/career/recommend`, `/resume/analyze`, `/roadmap/generate`, `/chat/message`, `/assessment/start|submit`) matches an existing backend route, HTTP method, and request body field names (read by hand).
- Auth integration by inspection: token stored on login/register, sent as `Authorization: Bearer`, 401 on a protected call clears the session and returns to /login; protected routes redirect when signed out.
- CORS: origins come from `ALLOWED_ORIGINS` (includes localhost:5173 and 127.0.0.1:5173); error responses also carry CORS headers.
- Question bank (40 skills, 400 questions), quiz building, grading and `latest_results` (with a stubbed DB).
- Text-coercion helpers used for AI output (offline).
- No secrets or `.env` files in the project.

## Fixed across Parts 1 and 2
- Crash in `latest_results` (broke `/assessment/latest` and career recommendations after a quiz).
- Gemini default model changed from `gemini-2.5-flash` (now restricted for new accounts) to `gemini-3.8-flash`; configurable timeout; clearer error messages; no retry on timeouts/quota.
- MongoDB: connection retry on later requests, 503 instead of 500 when unavailable, config checks for placeholder URI/JWT secret.
- AI responses that return numbers/objects instead of strings, or a non-object JSON, no longer cause HTTP 500 (`schemas`, `generate_json`).
- Chat no longer leaves an empty session when Gemini fails.

## Not verified / unresolved
- `npm install` / `npm run build` and the UI in a browser.
- `pip install`, server startup, `test_auth.py`.
- Real Atlas connection and live Gemini calls (including that `gemini-3.8-flash` works with your key/quota). Use `python diagnose.py --gemini`.
- The new pydantic validators and schema coercion were written but never executed.
- Profile update ignores `null` values, so a field cannot be cleared back to empty from the Profile page (existing behaviour, left unchanged).
- Dependency versions in `requirements.txt` are open ranges; pin them after a successful install.
