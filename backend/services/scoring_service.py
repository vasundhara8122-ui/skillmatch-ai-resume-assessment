from backend.database import get_db_connection


def normalize_answer(answer: str) -> str:
    if not answer:
        return ""
    return " ".join(answer.strip().lower().split())


def check_answer(question: dict, candidate_answer: str) -> bool:
    if not candidate_answer or not candidate_answer.strip():
        return False

    q_type = question["type"]
    correct = question.get("correct_answer", "") or ""

    if q_type == "mcq":
        return candidate_answer.strip().upper() == correct.strip().upper()

    if q_type == "coding":
        if question["skill"] in ("SQL", "MySQL"):
            return check_sql_answer(question, candidate_answer)
        return check_coding_answer(question, candidate_answer)

    return fuzzy_match(candidate_answer, correct)


def fuzzy_match(candidate: str, correct: str) -> bool:
    if not correct or not candidate:
        return False
    c_norm = normalize_answer(candidate)
    correct_norm = normalize_answer(correct)
    if c_norm == correct_norm:
        return True
    if correct_norm in c_norm or c_norm in correct_norm:
        return True
    correct_keywords = [w for w in correct_norm.split() if len(w) > 3]
    if not correct_keywords:
        return c_norm == correct_norm
    matched = sum(1 for kw in correct_keywords if kw in c_norm)
    return matched >= len(correct_keywords) * 0.6


def check_coding_answer(question: dict, candidate_answer: str) -> bool:
    expected = (question.get("expected_output") or "").strip()
    if not expected:
        return False

    code = candidate_answer.strip()
    if not code:
        return False

    if "def " not in code and "function " not in code and "print(" not in code.lower() and "select" not in code.lower():
        if question["skill"] not in ("HTML", "CSS"):
            return False

    if question["skill"] == "Python":
        if "def " in code:
            test_input = question.get("test_input", "") or ""
            try:
                func_match = code.split("def ")[1].split("(")[0]
                test_code = f"{code}\nprint({func_match}({test_input}))"
            except Exception:
                test_code = code
            output = run_python_safely(test_code)
        else:
            output = run_python_safely(code)
        if output is not None:
            return output.strip() == expected.strip()
        return False

    if question["skill"] == "JavaScript":
        js_keywords = ["function", "=>", "console.log", "return", "var", "let", "const"]
        if any(kw in code for kw in js_keywords):
            if expected.strip() in candidate_answer or len(candidate_answer.strip()) > 20:
                return True
        return False

    if question["skill"] in ("HTML", "CSS"):
        required_elements = {
            "HTML": ["form", "input", "button"],
            "CSS": ["border-radius", "padding"],
        }
        elements = required_elements.get(question["skill"], [])
        matches = sum(1 for el in elements if el.lower() in code.lower())
        return matches >= len(elements) / 2

    return False


def check_sql_answer(question: dict, candidate_answer: str) -> bool:
    expected = (question.get("expected_output") or "").strip().lower()
    answer = candidate_answer.strip().lower()
    if not answer:
        return False

    if answer == expected:
        return True

    keywords = [kw for kw in expected.split() if kw not in ("(", ")", ",", ";", "*", ">", "<", "=")]
    matched = sum(1 for kw in keywords if kw in answer)
    return matched >= len(keywords) * 0.7


def run_python_safely(code: str) -> str | None:
    import subprocess
    import tempfile
    import os

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir="/tmp") as f:
            f.write(code)
            f.flush()
            result = subprocess.run(
                ["python3", f.name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            os.unlink(f.name)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
    except Exception:
        return None


def calculate_scores(assessment_id: int) -> dict:
    conn = get_db_connection()
    try:
        answers = conn.execute(
            """SELECT a.*, q.skill, q.type, q.points
               FROM answers a JOIN questions q ON a.question_id = q.id
               WHERE a.assessment_id = %s""",
            (assessment_id,),
        ).fetchall()

        skill_data = {}
        type_scores = {
            "theory": {"correct": 0, "total": 0},
            "mcq": {"correct": 0, "total": 0},
            "code_output": {"correct": 0, "total": 0},
            "debugging": {"correct": 0, "total": 0},
            "coding": {"correct": 0, "total": 0},
            "sql": {"correct": 0, "total": 0},
        }

        total_questions = len(answers)
        correct_count = 0

        for ans in answers:
            skill = ans["skill"]
            q_type = ans["type"]
            if skill not in skill_data:
                skill_data[skill] = {"theory": {"correct": 0, "total": 0}, "coding": {"correct": 0, "total": 0}, "total": 0, "correct": 0}

            skill_data[skill]["total"] += 1
            if ans["is_correct"]:
                correct_count += 1
                skill_data[skill]["correct"] += 1

            if q_type in ("theory", "mcq", "code_output", "debugging"):
                skill_data[skill]["theory"]["total"] += 1
                if ans["is_correct"]:
                    skill_data[skill]["theory"]["correct"] += 1
            elif q_type in ("coding",):
                skill_data[skill]["coding"]["total"] += 1
                if ans["is_correct"]:
                    skill_data[skill]["coding"]["correct"] += 1

            effective_type = "sql" if skill in ("SQL", "MySQL") and q_type == "coding" else q_type
            if effective_type in type_scores:
                type_scores[effective_type]["total"] += 1
                if ans["is_correct"]:
                    type_scores[effective_type]["correct"] += 1

        conn.execute("DELETE FROM skill_scores WHERE assessment_id = %s", (assessment_id,))
        for skill, data in skill_data.items():
            theory_total = data["theory"]["total"]
            theory_correct = data["theory"]["correct"]
            coding_total = data["coding"]["total"]
            coding_correct = data["coding"]["correct"]
            total = theory_total + coding_total
            earned = theory_correct + coding_correct
            percentage = (earned / total * 100) if total > 0 else 0

            conn.execute(
                """INSERT INTO skill_scores (assessment_id, skill, theory_score, coding_score, total, percentage)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (assessment_id, skill, theory_correct, coding_total, earned, round(percentage, 1)),
            )

        theory_score = type_scores["theory"]["correct"]
        coding_score = type_scores["coding"]["correct"]
        mcq_score = type_scores["mcq"]["correct"]
        sql_score = type_scores["sql"]["correct"]
        code_output_score = type_scores["code_output"]["correct"]
        debugging_score = type_scores["debugging"]["correct"]
        overall = correct_count
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0

        conn.execute("DELETE FROM results WHERE assessment_id = %s", (assessment_id,))
        conn.execute(
            """INSERT INTO results (assessment_id, overall_score, theory_score, coding_score, mcq_score,
               sql_score, code_output_score, debugging_score, total_questions, correct_count, percentage)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (assessment_id, overall, theory_score, coding_score, mcq_score, sql_score,
             code_output_score, debugging_score, total_questions, correct_count, round(percentage, 1)),
        )

        conn.execute("UPDATE assessments SET status = 'completed', submitted_at = CURRENT_TIMESTAMP WHERE id = %s", (assessment_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {
        "overall_score": overall,
        "theory_score": theory_score,
        "coding_score": coding_score,
        "mcq_score": mcq_score,
        "sql_score": sql_score,
        "code_output_score": code_output_score,
        "debugging_score": debugging_score,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "percentage": round(percentage, 1),
    }
