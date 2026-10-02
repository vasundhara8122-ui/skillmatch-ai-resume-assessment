import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.database import get_db_connection
from backend.config import UPLOAD_DIR
from backend.services.resume_parser import parse_resume, classify_education_level
from backend.services.skill_extractor import extract_skills, determine_level, get_difficulty, get_skill_category
from backend.services.assessment_service import create_assessment_for_candidate

router = APIRouter(prefix="/api/resume", tags=["resume"])
logger = logging.getLogger("skillmatch")


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".docx", ".txt"):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported")

    safe_name = os.path.basename(file.filename)
    file_path = os.path.join(str(UPLOAD_DIR), safe_name)
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)[:100]}")

    try:
        parsed = parse_resume(file_path, safe_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse resume: {str(e)[:100]}")

    try:
        skills = extract_skills(parsed["raw_text"])
        level = determine_level(parsed["degree"])
        difficulty = get_difficulty(level)
        education_level = parsed.get("education_level") or classify_education_level(parsed["degree"])

        logger.info("=== Candidate Classification ===")
        logger.info("Qualification: %s", parsed["degree"])
        logger.info("Education Level: %s", education_level)
        logger.info("Assessment Level: %s", level)
        logger.info("Difficulty: %s", difficulty)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract skills: {str(e)[:100]}")

    db = get_db_connection()
    try:
        cursor = db.execute(
            "INSERT INTO candidates (company_id, name, email, phone, degree, graduation_year, level) VALUES (1, %s, %s, %s, %s, %s, %s)",
            (parsed["name"], parsed["email"], parsed["phone"], parsed["degree"], parsed["graduation_year"], level),
        )
        candidate_id = cursor.lastrowid

        db.execute(
            "INSERT INTO resumes (candidate_id, filename, raw_text) VALUES (%s, %s, %s)",
            (candidate_id, safe_name, parsed["raw_text"]),
        )

        for skill in skills:
            skill_row = db.execute("SELECT id FROM skills WHERE name = %s", (skill,)).fetchone()
            if skill_row:
                existing = db.execute(
                    "SELECT id FROM candidate_skills WHERE candidate_id = %s AND skill_id = %s",
                    (candidate_id, skill_row["id"]),
                ).fetchone()
                if not existing:
                    db.execute(
                        "INSERT INTO candidate_skills (candidate_id, skill_id) VALUES (%s, %s)",
                        (candidate_id, skill_row["id"]),
                    )

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)[:100]}")
    finally:
        db.close()

    try:
        assessment_id = create_assessment_for_candidate(candidate_id, skills, parsed["degree"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment generation failed: {str(e)[:150]}")

    return {
        "success": True,
        "candidate": {
            "id": candidate_id,
            "name": parsed["name"],
            "email": parsed["email"],
            "phone": parsed["phone"],
            "degree": parsed["degree"],
            "qualification": parsed["degree"],
            "education_level": education_level,
            "graduation_year": parsed["graduation_year"],
            "level": level,
            "difficulty": difficulty,
        },
        "skills": skills,
        "skill_details": [{"name": s, "category": get_skill_category(s)} for s in skills],
        "assessment_id": assessment_id,
        "debug": {
            "qualification": parsed["degree"],
            "education_level": education_level,
            "assessment_level": level,
            "difficulty": difficulty,
        },
    }


@router.get("/analysis/{candidate_id}")
def get_resume_analysis(candidate_id: int):
    db = get_db_connection()
    try:
        candidate = db.execute("SELECT * FROM candidates WHERE id = %s", (candidate_id,)).fetchone()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        skills = db.execute(
            """SELECT s.name, s.category FROM candidate_skills cs
               JOIN skills s ON cs.skill_id = s.id WHERE cs.candidate_id = %s""",
            (candidate_id,),
        ).fetchall()

        resume = db.execute("SELECT * FROM resumes WHERE candidate_id = %s ORDER BY id DESC LIMIT 1", (candidate_id,)).fetchone()

        assessment = db.execute(
            "SELECT * FROM assessments WHERE candidate_id = %s ORDER BY id DESC LIMIT 1", (candidate_id,)
        ).fetchone()
    finally:
        db.close()

    return {
        "candidate": candidate,
        "skills": skills,
        "resume_filename": resume["filename"] if resume else None,
        "assessment_id": assessment["id"] if assessment else None,
        "level": candidate["level"],
    }
