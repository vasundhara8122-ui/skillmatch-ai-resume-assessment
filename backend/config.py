import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

FRONTEND_DIR = BASE_DIR / "frontend"
# Vercel uses a read-only filesystem except for /tmp
if os.getenv("VERCEL") == "1":
    UPLOAD_DIR = Path("/tmp/uploads")
else:
    UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "defaultdb")
DB_SSL_REQUIRED = os.getenv("DB_SSL_REQUIRED", "true").lower() in ("true", "1", "yes")

EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "SkillMatch AI")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")

DEMO_COMPANY_EMAIL = os.getenv("DEMO_COMPANY_EMAIL", "hr@skillmatch.ai")
DEMO_COMPANY_PASSWORD = os.getenv("DEMO_COMPANY_PASSWORD", "hr123")
