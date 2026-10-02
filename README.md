# SkillMatch AI

**AI-Powered Resume Analysis, Skill Assessment & Job-Role Skill Matching**

A platform that helps companies assess a candidate's technical skills using their resume and an online skill assessment.

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript (no frameworks, no build tools)
- **Backend:** Python + FastAPI
- **Database:** MySQL (Aiven MySQL) via PyMySQL
- **Resume Processing:** PyPDF2 (PDF), python-docx (DOCX)
- **Email:** SMTP via Python smtplib (optional — demo mode works without it)
- **Deployment:** Vercel (Python serverless functions)

## Quick Start (Local Development)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your database credentials:
```bash
cp .env.example .env
```

3. Run the server:
```bash
python3 -m uvicorn backend.main:app --reload --port 8000
```

4. Open http://localhost:8000 in your browser.

## Environment Variables

| Variable | Description |
|---|---|
| `DB_HOST` | MySQL host (Aiven) |
| `DB_PORT` | MySQL port (default 3306) |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_NAME` | MySQL database name |
| `EMAIL_HOST` | SMTP host (optional) |
| `EMAIL_PORT` | SMTP port (default 587) |
| `EMAIL_USERNAME` | SMTP username (optional) |
| `EMAIL_PASSWORD` | SMTP password (optional) |
| `EMAIL_FROM_NAME` | Sender display name |
| `FRONTEND_URL` | Public URL for assessment links |
| `DEMO_COMPANY_EMAIL` | Demo HR login email |
| `DEMO_COMPANY_PASSWORD` | Demo HR login password |

## Demo Credentials

### Company / HR
- Email: `hr@skillmatch.ai`
- Password: `hr123`

### Student / Candidate
- Email: the email extracted from the uploaded resume
- Password: auto-generated and shown in demo mode when SMTP is not configured

## How It Works

1. HR logs in and uploads a candidate's resume (PDF, DOCX, or TXT)
2. The system extracts name, email, phone, degree, graduation year, and technical skills
3. Assessment level is determined automatically (Level 1 Medium for UG degrees, Level 2 Hard for PG/Master's degrees)
4. A 30-question assessment is created with strict level separation:
   - Theory: 8 questions
   - MCQ: 6 questions
   - Code Output: 4 questions
   - Debugging: 3 questions
   - Coding: 6 questions
   - SQL: 3 questions
5. HR sends an email invitation (or uses demo mode to get the link + password)
6. The candidate logs in and takes the assessment
7. The system calculates overall score, skill-wise scores, and job-role match percentages
8. HR reviews the detailed assessment report

## Assessment Levels

- **Level 1 (Medium):** UG degrees — B.Sc, BCA, B.Tech, B.E, B.Com, BA
- **Level 2 (Hard):** PG degrees — M.Sc, MCA, M.Tech, MA, Master's

Levels are never mixed. Each assessment uses questions from only one level.

## Job Roles

The system matches candidates against four predefined roles:
- Python Developer
- Frontend Developer
- Backend Developer
- Full Stack Developer

## Vercel Deployment

1. Push your code to GitHub
2. Import the repository into Vercel
3. Add all environment variables (see table above) in Vercel → Settings → Environment Variables
4. Deploy — Vercel will auto-detect the Python runtime from `api/index.py`
5. The app will be available at your Vercel domain

## Project Structure

```
skillmatch-ai/
├── api/                # Vercel serverless entry point
│   └── index.py
├── frontend/           # HTML, CSS, JavaScript
│   ├── css/
│   └── js/
├── backend/            # FastAPI application
│   ├── routes/         # API endpoints
│   ├── services/       # Business logic
│   ├── config.py       # Environment configuration
│   ├── database.py     # MySQL connection layer
│   ├── main.py         # FastAPI app setup
│   └── models.py       # Pydantic models
├── database/           # SQL schema reference
├── uploads/            # Uploaded resumes (local dev only)
├── requirements.txt
├── vercel.json
└── .env.example
```

## Important

The system does NOT make hiring decisions. It provides objective assessment results and skill-match percentages. The company/HR makes the final employment decision.
