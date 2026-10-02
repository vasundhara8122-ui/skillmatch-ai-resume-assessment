from fastapi import APIRouter, HTTPException
from backend.database import get_db_connection

router = APIRouter(prefix="/api/scoring", tags=["scoring"])


@router.get("/dashboard")
def get_dashboard_stats():
    db = get_db_connection()
    try:
        total_candidates = db.execute("SELECT COUNT(*) as c FROM candidates").fetchone()["c"]
        assessments_sent = db.execute("SELECT COUNT(*) as c FROM assessments WHERE invitation_sent = 1").fetchone()["c"]
        assessments_completed = db.execute("SELECT COUNT(*) as c FROM assessments WHERE status = 'completed'").fetchone()["c"]
        avg_score_row = db.execute("SELECT AVG(percentage) as avg FROM results").fetchone()
        avg_score = round(avg_score_row["avg"], 1) if avg_score_row["avg"] else 0
    finally:
        db.close()

    return {
        "total_candidates": total_candidates,
        "assessments_sent": assessments_sent,
        "assessments_completed": assessments_completed,
        "average_score": avg_score,
    }
