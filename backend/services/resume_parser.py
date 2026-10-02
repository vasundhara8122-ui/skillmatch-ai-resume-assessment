import re
import logging
from pathlib import Path

from PyPDF2 import PdfReader
from docx import Document

logger = logging.getLogger("skillmatch")

# Postgraduate degree patterns — checked FIRST so we always pick the highest qualification
PG_PATTERNS = [
    r"\bM\.?\s*Sc\b",
    r"\bMSc\b",
    r"\bM\.?\s*Tech\b",
    r"\bMTech\b",
    r"\bM\.?\s*E\b",
    r"\bMCA\b",
    r"\bM\.?\s*A\b(?!\s*N)",  # M.A but not M.AN...
    r"\bMBA\b",
    r"\bM\.?\s*Com\b",
    r"\bMaster(?:'s)?\s+(?:of\s+)?(?:Science|Arts|Commerce|Technology|Engineering|Computer|Business|Application)",
    r"\bMaster(?:'s)?\s+Degree\b",
    r"\bPost\s*Graduate\b",
    r"\bPostgraduate\b",
]

# Undergraduate degree patterns
UG_PATTERNS = [
    r"\bB\.?\s*Sc\b",
    r"\bBSc\b",
    r"\bB\.?\s*Tech\b",
    r"\bBTech\b",
    r"\bB\.?\s*E\b",
    r"\bBE\b",
    r"\bBCA\b",
    r"\bB\.?\s*A\b",
    r"\bB\.?\s*Com\b",
    r"\bBachelor(?:'s)?\s+(?:of\s+)?(?:Science|Arts|Commerce|Technology|Engineering|Computer|Business|Application)",
    r"\bBachelor(?:'s)?\s+Degree\b",
    r"\bUnder\s*Graduate\b",
    r"\bUndergraduate\b",
]


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)


def extract_text(file_path: str, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    if ext == ".txt":
        return Path(file_path).read_text()
    raise ValueError(f"Unsupported file type: {ext}")


def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    patterns = [
        r"(\+91[\s\-]?\d{5}[\s\-]?\d{5})",
        r"(\+91[\s\-]?\d{10})",
        r"(\b91\d{10}\b)",
        r"(\b\d{10}\b)",
        r"(\+?\d[\d\s\-]{8,14}\d)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return ""


def extract_name(text: str) -> str:
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    for line in lines[:10]:
        words = line.split()
        if 2 <= len(words) <= 5 and all(w[0].isupper() or w.isalpha() for w in words):
            if not any(kw in line.lower() for kw in ["email", "phone", "address", "resume", "curriculum", "cv", "@"]):
                return line
    return lines[0] if lines else "Unknown Candidate"


def _find_all_matches(text: str, patterns: list[str]) -> list[str]:
    """Return all lines from the text that match any of the given patterns."""
    matches = []
    for line in text.split("\n"):
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                matches.append(line.strip())
                break
    return matches


def extract_qualification(text: str) -> str:
    """Extract the HIGHEST qualification from resume text.

    Postgraduate degrees are checked first. If any PG degree is found,
    it is returned immediately — even if a bachelor's degree also appears.
    Only if NO postgraduate degree is found do we fall back to undergraduate.
    """
    # Check postgraduate first — highest priority
    for pattern in PG_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Grab the full line for context
            start = match.start()
            line_start = text.rfind("\n", 0, start) + 1
            line_end = text.find("\n", start)
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end].strip()
            return line.rstrip(",.;")

    # Check undergraduate
    for pattern in UG_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = match.start()
            line_start = text.rfind("\n", 0, start) + 1
            line_end = text.find("\n", start)
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end].strip()
            return line.rstrip(",.;")

    return "Not Found"


def classify_education_level(qualification: str) -> str:
    """Classify a qualification string as UNDERGRADUATE or POSTGRADUATE.

    Postgraduate is checked first so that combined qualifications
    like 'B.Sc Computer Science, M.Sc Computer Science' resolve to POSTGRADUATE.
    """
    q_upper = qualification.upper()

    # Postgraduate check — must be checked BEFORE undergraduate
    pg_keywords = [
        "M.SC", "MSC", "M.TECH", "MTECH", "M.E ", "M.E.", " MCA ",
        "MCA", "MBA", "M.COM", "M.A ", "M.A.",
        "MASTER", "POST GRADUATE", "POSTGRADUATE", "POST-GRADUATE",
    ]
    for kw in pg_keywords:
        if kw in q_upper:
            return "POSTGRADUATE"

    # Undergraduate check
    ug_keywords = [
        "B.SC", "BSC", "B.TECH", "BTECH", "B.E ", "B.E.", "BCA",
        "B.COM", "B.A ", "B.A.", "BACHELOR", "UNDER GRADUATE",
        "UNDERGRADUATE", "UNDER-GRADUATE",
    ]
    for kw in ug_keywords:
        if kw in q_upper:
            return "UNDERGRADUATE"

    return "UNDERGRADUATE"


def extract_graduation_year(text: str) -> str:
    match = re.search(r"(20[12]\d)", text)
    return match.group(0) if match else "Not Found"


# Keep the old function name for backward compatibility with existing code
def extract_degree(text: str) -> str:
    return extract_qualification(text)


def parse_resume(file_path: str, filename: str) -> dict:
    text = extract_text(file_path, filename)
    qualification = extract_qualification(text)
    education_level = classify_education_level(qualification)

    logger.info("=== Resume Analysis ===")
    logger.info("Qualification: %s", qualification)
    logger.info("Education Level: %s", education_level)

    return {
        "raw_text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "degree": qualification,
        "qualification": qualification,
        "education_level": education_level,
        "graduation_year": extract_graduation_year(text),
    }
