from fastapi import APIRouter, HTTPException
from backend.database import get_db_connection
from backend.config import DEMO_COMPANY_EMAIL, DEMO_COMPANY_PASSWORD
from backend.models import CompanyLogin, StudentLogin

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/company/login")
def company_login(data: CompanyLogin):
    if data.email == DEMO_COMPANY_EMAIL and data.password == DEMO_COMPANY_PASSWORD:
        return {"success": True, "role": "company", "name": "SkillMatch Demo Company", "email": data.email}
    raise HTTPException(status_code=401, detail="Invalid company credentials")


@router.post("/student/login")
def student_login(data: StudentLogin):
    db = get_db_connection()
    try:
        candidate = db.execute(
            "SELECT * FROM candidates WHERE email = %s ORDER BY id DESC LIMIT 1", (data.email,)
        ).fetchone()
    finally:
        db.close()

    if not candidate:
        raise HTTPException(status_code=401, detail="No candidate found with this email. Please use the email from your resume.")

    if not candidate["password"]:
        raise HTTPException(status_code=401, detail="Your assessment is not ready yet. Please wait for the HR to send you an invitation email.")

    if data.password != candidate["password"]:
        raise HTTPException(status_code=401, detail="Invalid password. Please use the password from your assessment invitation email.")

    return {
        "success": True,
        "role": "student",
        "candidate_id": candidate["id"],
        "name": candidate["name"],
        "email": candidate["email"],
    }
