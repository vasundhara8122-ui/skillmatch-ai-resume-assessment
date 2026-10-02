from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import traceback

from backend.config import FRONTEND_DIR
from backend.database import init_db
from backend.services.assessment_service import seed_questions, seed_job_roles, seed_skills, seed_demo_company

app = FastAPI(title="SkillMatch AI", version="1.0.0")

frontend_dir = FRONTEND_DIR
if frontend_dir.exists():
    app.mount("/css", StaticFiles(directory=str(frontend_dir / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(frontend_dir / "js")), name="js")

uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
if uploads_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

from backend.routes import auth, resume, assessment, candidate, scoring, report

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(assessment.router)
app.include_router(candidate.router)
app.include_router(scoring.router)
app.include_router(report.router)


def _initialize_database():
    try:
        init_db()
        seed_skills()
        seed_questions()
        seed_job_roles()
        seed_demo_company()
    except Exception as e:
        print(f"Database initialization error: {e}")


@app.on_event("startup")
def startup():
    _initialize_database()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error", "detail": str(exc)[:200]},
        )
    return HTMLResponse(content="<h1>Server Error</h1><p>Something went wrong.</p>", status_code=500)


@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/{page}.html", response_class=HTMLResponse)
def serve_page(page: str):
    file_path = FRONTEND_DIR / f"{page}.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)
