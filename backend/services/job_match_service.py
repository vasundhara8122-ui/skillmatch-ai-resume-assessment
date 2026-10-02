from backend.database import get_db_connection


def calculate_skill_match(assessment_id: int, detected_skills: list[str]) -> list[dict]:
    conn = get_db_connection()
    try:
        skill_scores = conn.execute(
            "SELECT skill, percentage FROM skill_scores WHERE assessment_id = %s",
            (assessment_id,),
        ).fetchall()

        skill_perf = {row["skill"]: row["percentage"] for row in skill_scores}

        roles = conn.execute("SELECT id, name FROM job_roles").fetchall()
        matches = []

        conn.execute("DELETE FROM skill_matches WHERE assessment_id = %s", (assessment_id,))

        for role in roles:
            role_skills = conn.execute(
                "SELECT skill, weight FROM job_role_skills WHERE role_id = %s",
                (role["id"],),
            ).fetchall()

            total_weight = 0
            matched_weight = 0

            for rs in role_skills:
                skill = rs["skill"]
                weight = rs["weight"]
                total_weight += weight

                if skill in detected_skills:
                    perf = skill_perf.get(skill, 50)
                    matched_weight += weight * (perf / 100)
                elif skill in skill_perf:
                    perf = skill_perf.get(skill, 30)
                    matched_weight += weight * (perf / 100) * 0.5

            match_pct = (matched_weight / total_weight * 100) if total_weight > 0 else 0
            match_pct = round(match_pct, 1)

            conn.execute(
                "INSERT INTO skill_matches (assessment_id, role_name, match_percentage) VALUES (%s, %s, %s)",
                (assessment_id, role["name"], match_pct),
            )
            matches.append({"role": role["name"], "match_percentage": match_pct})

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return matches
