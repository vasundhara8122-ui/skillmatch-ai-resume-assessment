import re

SKILL_KEYWORDS = {
    "Python": [r"\bpython\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "HTML": [r"\bhtml\b"],
    "CSS": [r"\bcss\b"],
    "MySQL": [r"\bmysql\b", r"\bmaria\s*db\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "React": [r"\breact\b"],
    "Node": [r"\bnode(\.js)?\b"],
    "SQL": [r"\bsql\b"],
    "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"],
    "MongoDB": [r"\bmongodb\b"],
    "Java": [r"\bjava\b"],
    "C++": [r"\bc\+\+\b"],
    "C": [r"\bc\b(?!#|\+\+)"],
    "Git": [r"\bgit\b"],
    "Docker": [r"\bdocker\b"],
    "REST API": [r"\brest\s*api\b", r"\brestful\b"],
    "DSA": [r"\bdsa\b", r"\bdata\s*structures\b", r"\balgorithms\b"],
    "DOM": [r"\bdom\b"],
    "Responsive Design": [r"\bresponsive\b"],
    "Problem Solving": [r"\bproblem\s*solving\b"],
    "Backend Basics": [r"\bbackend\b"],
    "Database": [r"\bdatabase\b"],
}

SKILL_CATEGORIES = {
    "Python": "Programming Language",
    "JavaScript": "Programming Language",
    "Java": "Programming Language",
    "C++": "Programming Language",
    "C": "Programming Language",
    "HTML": "Web Technology",
    "CSS": "Web Technology",
    "React": "Web Technology",
    "Node": "Web Technology",
    "DOM": "Web Technology",
    "Responsive Design": "Web Technology",
    "MySQL": "Database",
    "PostgreSQL": "Database",
    "MongoDB": "Database",
    "SQL": "Database",
    "Database": "Database",
    "FastAPI": "Framework",
    "Flask": "Framework",
    "Django": "Framework",
    "REST API": "Concept",
    "DSA": "Concept",
    "Problem Solving": "Concept",
    "Backend Basics": "Concept",
    "Git": "Tool",
    "Docker": "Tool",
}


def extract_skills(text: str) -> list[str]:
    detected = []
    text_lower = text.lower()
    for skill, patterns in SKILL_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                if skill not in detected:
                    detected.append(skill)
                break
    return detected


def get_skill_category(skill: str) -> str:
    return SKILL_CATEGORIES.get(skill, "Other")


def determine_level(degree: str) -> str:
    """Determine assessment level from qualification string.

    POSTGRADUATE (M.Sc, MCA, M.Tech, MBA, Master's) -> Level 2 (Hard)
    UNDERGRADUATE (B.Sc, B.Tech, BCA, Bachelor's)   -> Level 1 (Medium)
    """
    from backend.services.resume_parser import classify_education_level
    education_level = classify_education_level(degree)
    if education_level == "POSTGRADUATE":
        return "Level 2"
    return "Level 1"


def get_difficulty(level: str) -> str:
    """Return difficulty label for a given assessment level."""
    if level == "Level 2":
        return "HARD"
    return "MEDIUM"
