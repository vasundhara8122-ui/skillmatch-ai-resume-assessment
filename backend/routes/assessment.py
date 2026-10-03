from fastapi import APIRouter, HTTPException
from backend.database import get_db_connection
from backend.models import AssessmentSubmit
from backend.services.scoring_service import calculate_scores, check_answer
from backend.services.job_match_service import calculate_skill_match

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


@router.get("/{assessment_id}")
def get_assessment(assessment_id: int):
    db = get_db_connection()
    try:
        assessment = db.execute("SELECT * FROM assessments WHERE id = %s", (assessment_id,)).fetchone()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        questions = db.execute(
            """SELECT q.id, q.skill, q.type, q.level, q.question, q.option_a, q.option_b,
                      q.option_c, q.option_d, q.points
               FROM assessment_questions aq
               JOIN questions q ON aq.question_id = q.id
               WHERE aq.assessment_id = %s
               ORDER BY q.skill, q.type""",
            (assessment_id,),
        ).fetchall()
    finally:
        db.close()

    return {
        "assessment_id": assessment_id,
        "level": assessment["level"],
        "status": assessment["status"],
        "questions": questions,
        "total_questions": len(questions),
    }


@router.post("/{assessment_id}/submit")
def submit_assessment(assessment_id: int, data: AssessmentSubmit):
    db = get_db_connection()
    try:
        assessment = db.execute("SELECT * FROM assessments WHERE id = %s", (assessment_id,)).fetchone()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        if assessment["status"] == "completed":
            raise HTTPException(status_code=400, detail="Assessment already submitted")

        db.execute("UPDATE assessments SET status = 'in_progress', started_at = CURRENT_TIMESTAMP WHERE id = %s", (assessment_id,))

        db.execute("DELETE FROM answers WHERE assessment_id = %s", (assessment_id,))

        for answer in data.answers:
            question = db.execute("SELECT * FROM questions WHERE id = %s", (answer.question_id,)).fetchone()
            if not question:
                continue

            is_correct = check_answer(question, answer.candidate_answer)
            points = question["points"] if is_correct else 0

            db.execute(
                """INSERT INTO answers (assessment_id, question_id, candidate_answer, is_correct, points_earned)
                   VALUES (%s, %s, %s, %s, %s)""",
                (assessment_id, answer.question_id, answer.candidate_answer, bool(is_correct), points),
            )

        db.execute("UPDATE assessments SET started_at = COALESCE(started_at, CURRENT_TIMESTAMP) WHERE id = %s", (assessment_id,))
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Submission error: {str(e)[:100]}")
    finally:
        db.close()

    try:
        scores = calculate_scores(assessment_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Score calculation error: {str(e)[:100]}")

    db = get_db_connection()
    try:
        candidate = db.execute(
            """SELECT c.* FROM candidates c JOIN assessments a ON c.id = a.candidate_id WHERE a.id = %s""",
            (assessment_id,),
        ).fetchone()

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found for this assessment")

        detected_skills = [
            row["name"] for row in db.execute(
                """SELECT s.name FROM candidate_skills cs JOIN skills s ON cs.skill_id = s.id
                   WHERE cs.candidate_id = %s""", (candidate["id"],)
            ).fetchall()
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading candidate: {str(e)[:100]}")
    finally:
        db.close()

    try:
        matches = calculate_skill_match(assessment_id, detected_skills)
    except Exception as e:
        matches = []

    return {
        "success": True,
        "scores": scores,
        "skill_matches": matches,
        "candidate_id": candidate["id"],
    }


@router.get("/{assessment_id}/result")
def get_result(assessment_id: int):
    db = get_db_connection()
    try:
        result = db.execute("SELECT * FROM results WHERE assessment_id = %s", (assessment_id,)).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Result not found. Submit the assessment first.")

        skill_scores = db.execute(
            "SELECT * FROM skill_scores WHERE assessment_id = %s", (assessment_id,)
        ).fetchall()

        matches = db.execute(
            "SELECT * FROM skill_matches WHERE assessment_id = %s", (assessment_id,)
        ).fetchall()

        assessment = db.execute("SELECT * FROM assessments WHERE id = %s", (assessment_id,)).fetchone()
        candidate = db.execute(
            "SELECT * FROM candidates WHERE id = (SELECT candidate_id FROM assessments WHERE id = %s)",
            (assessment_id,),
        ).fetchone()
    finally:
        db.close()

    return {
        "result": result,
        "skill_scores": skill_scores,
        "skill_matches": matches,
        "candidate": candidate,
        "assessment": assessment,
    }


@router.post("/{assessment_id}/send-invitation")
def send_invitation(assessment_id: int):
    db = get_db_connection()
    try:
        assessment = db.execute("SELECT * FROM assessments WHERE id = %s", (assessment_id,)).fetchone()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        candidate = db.execute("SELECT * FROM candidates WHERE id = %s", (assessment["candidate_id"],)).fetchone()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
    finally:
        db.close()

    from backend.services.email_service import send_assessment_email, generate_password

    password = generate_password()

    db = get_db_connection()
    try:
        db.execute("UPDATE candidates SET password = %s WHERE id = %s", (password, candidate["id"]))
        db.execute("UPDATE assessments SET invitation_sent = 1 WHERE id = %s", (assessment_id,))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update invitation: {str(e)[:100]}")
    finally:
        db.close()

    result = send_assessment_email(
        candidate["name"], candidate["email"], assessment["level"], assessment_id, password
    )

    return result
