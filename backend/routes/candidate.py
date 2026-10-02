import os
import logging
from fastapi import APIRouter, HTTPException
from backend.database import get_db_connection
from backend.config import UPLOAD_DIR

router = APIRouter(prefix="/api/candidate", tags=["candidate"])
logger = logging.getLogger("skillmatch")


@router.get("/list/all")
def list_candidates():
    db = get_db_connection()
    try:
        candidates = db.execute("SELECT * FROM candidates ORDER BY id DESC").fetchall()
        result = []
        for c in candidates:
            skills = db.execute(
                """SELECT s.name FROM candidate_skills cs
                   JOIN skills s ON cs.skill_id = s.id WHERE cs.candidate_id = %s""",
                (c["id"],),
            ).fetchall()
            assessment = db.execute(
                "SELECT * FROM assessments WHERE candidate_id = %s ORDER BY id DESC LIMIT 1", (c["id"],)
            ).fetchone()
            result_row = db.execute(
                "SELECT * FROM results WHERE assessment_id = %s",
                (assessment["id"],)
            ).fetchone() if assessment else None
            match_row = db.execute(
                "SELECT MAX(match_percentage) as best FROM skill_matches WHERE assessment_id = %s",
                (assessment["id"],)
            ).fetchone() if assessment else None

            result.append({
                "id": c["id"],
                "name": c["name"],
                "email": c["email"],
                "degree": c["degree"],
                "level": c["level"],
                "skills": [row["name"] for row in skills],
                "assessment_status": assessment["status"] if assessment else "pending",
                "score": result_row["percentage"] if result_row else None,
                "best_match": match_row["best"] if match_row and match_row["best"] else None,
            })
    finally:
        db.close()
    return result


@router.get("/{candidate_id}")
def get_candidate(candidate_id: int):
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

        assessment = db.execute(
            "SELECT * FROM assessments WHERE candidate_id = %s ORDER BY id DESC LIMIT 1", (candidate_id,)
        ).fetchone()
    finally:
        db.close()

    return {
        "candidate": candidate,
        "skills": skills,
        "assessment_id": assessment["id"] if assessment else None,
        "assessment_status": assessment["status"] if assessment else None,
    }


@router.get("/by-email/{email}")
def get_candidate_by_email(email: str):
    db = get_db_connection()
    try:
        candidate = db.execute("SELECT * FROM candidates WHERE email = %s ORDER BY id DESC LIMIT 1", (email,)).fetchone()
        if not candidate:
            raise HTTPException(status_code=404, detail="No candidate found with this email")

        skills = db.execute(
            """SELECT s.name FROM candidate_skills cs
               JOIN skills s ON cs.skill_id = s.id WHERE cs.candidate_id = %s""",
            (candidate["id"],),
        ).fetchall()

        assessment = db.execute(
            "SELECT * FROM assessments WHERE candidate_id = %s ORDER BY id DESC LIMIT 1", (candidate["id"],)
        ).fetchone()
    finally:
        db.close()

    return {
        "candidate": candidate,
        "skills": [row["name"] for row in skills],
        "assessment_id": assessment["id"] if assessment else None,
        "assessment_status": assessment["status"] if assessment else None,
    }


@router.post("/clear-test-data")
def clear_test_data():
    """Development-only endpoint to delete all candidate/assessment test data.

    Preserves: companies, skills, questions, job_roles, job_role_skills, and table structure.
    Deletes (in FK-safe order):
      email_logs, skill_matches, skill_scores, results, answers,
      assessment_questions, assessments, candidate_skills, resumes, candidates
    Also removes uploaded resume files belonging to deleted candidates.
    """
    db = get_db_connection()
    try:
        filenames = db.execute("SELECT filename FROM resumes").fetchall()
        candidate_count = db.execute("SELECT COUNT(*) AS c FROM candidates").fetchone()["c"]

        # Delete child tables first (FK-safe order), then parent tables
        db.execute("DELETE FROM email_logs")
        db.execute("DELETE FROM skill_matches")
        db.execute("DELETE FROM skill_scores")
        db.execute("DELETE FROM results")
        db.execute("DELETE FROM answers")
        db.execute("DELETE FROM assessment_questions")
        db.execute("DELETE FROM assessments")
        db.execute("DELETE FROM candidate_skills")
        db.execute("DELETE FROM resumes")
        db.execute("DELETE FROM candidates")

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear test data: {str(e)[:150]}")
    finally:
        db.close()

    # Remove uploaded resume files
    deleted_files = []
    for row in filenames:
        fname = row["filename"]
        fpath = os.path.join(str(UPLOAD_DIR), os.path.basename(fname))
        try:
            if os.path.exists(fpath):
                os.remove(fpath)
                deleted_files.append(fname)
        except Exception as e:
            logger.warning("Could not delete uploaded file %s: %s", fname, e)

    logger.info("Cleared test data: %d candidates deleted, %d files removed", candidate_count, len(deleted_files))

    return {
        "success": True,
        "message": f"Test data cleared successfully. {candidate_count} candidate(s) removed.",
        "deleted_files": deleted_files,
    }
