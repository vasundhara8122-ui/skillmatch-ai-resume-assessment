from fastapi import APIRouter, HTTPException
from backend.database import get_db_connection

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/candidate/{candidate_id}")
def get_candidate_report(candidate_id: int):
    db = get_db_connection()
    try:
        assessment = db.execute(
            "SELECT * FROM assessments WHERE candidate_id = %s ORDER BY id DESC LIMIT 1", (candidate_id,)
        ).fetchone()
        if not assessment:
            raise HTTPException(status_code=404, detail="No assessment found for this candidate")
    finally:
        db.close()
    return get_report(assessment["id"])


@router.get("/{assessment_id}")
def get_report(assessment_id: int):
    db = get_db_connection()
    try:
        assessment = db.execute("SELECT * FROM assessments WHERE id = %s", (assessment_id,)).fetchone()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        candidate = db.execute("SELECT * FROM candidates WHERE id = %s", (assessment["candidate_id"],)).fetchone()
        skills = db.execute(
            """SELECT s.name FROM candidate_skills cs
               JOIN skills s ON cs.skill_id = s.id WHERE cs.candidate_id = %s""",
            (candidate["id"],),
        ).fetchall()

        result = db.execute("SELECT * FROM results WHERE assessment_id = %s", (assessment_id,)).fetchone()
        skill_scores = db.execute("SELECT * FROM skill_scores WHERE assessment_id = %s", (assessment_id,)).fetchall()
        matches = db.execute("SELECT * FROM skill_matches WHERE assessment_id = %s", (assessment_id,)).fetchall()

        answers = db.execute(
            """SELECT a.*, q.skill, q.type FROM answers a
               JOIN questions q ON a.question_id = q.id
               WHERE a.assessment_id = %s""",
            (assessment_id,),
        ).fetchall()

        coding_answers = [a for a in answers if a["type"] == "coding"]
    finally:
        db.close()

    return {
        "candidate": candidate,
        "skills": [row["name"] for row in skills],
        "assessment": assessment,
        "result": result if result else None,
        "skill_scores": skill_scores,
        "skill_matches": matches,
        "coding_answers": coding_answers,
    }
