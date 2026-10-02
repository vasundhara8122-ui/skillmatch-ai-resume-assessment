import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.config import (
    EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM_NAME, FRONTEND_URL,
)
from backend.database import get_db_connection


def is_smtp_configured() -> bool:
    return bool(EMAIL_HOST and EMAIL_USERNAME and EMAIL_PASSWORD)


def generate_password(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def send_assessment_email(
    candidate_name: str,
    candidate_email: str,
    level: str,
    assessment_id: int,
    candidate_password: str,
) -> dict:
    difficulty = "Medium" if level == "Level 1" else "Hard"
    assessment_link = f"{FRONTEND_URL}/student-login.html?assessment={assessment_id}"

    subject = "SkillMatch AI - Technical Skill Assessment"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #1e3a5f, #2563eb); padding: 30px; border-radius: 12px; text-align: center;">
            <h1 style="color: white; margin: 0;">SkillMatch AI</h1>
            <p style="color: #cbd5e1; margin-top: 8px;">AI-Powered Skill Assessment</p>
        </div>
        <div style="padding: 30px; background: #f8fafc; border-radius: 0 0 12px 12px;">
            <h2>Hello {candidate_name},</h2>
            <p>Your technical skill assessment has been assigned by your company HR.</p>
            <p><strong>Assessment Level:</strong> {level} - {difficulty}</p>
            <p><strong>Your login email:</strong> {candidate_email}</p>
            <p><strong>Your login password:</strong> {candidate_password}</p>
            <p>Please click the button below to log in and begin your assessment.</p>
            <a href="{assessment_link}"
               style="display: inline-block; background: #2563eb; color: white; padding: 14px 32px;
                      border-radius: 8px; text-decoration: none; font-weight: bold; margin: 20px 0;">
                TAKE ASSESSMENT
            </a>
            <p style="color: #64748b; font-size: 14px; margin-top: 30px;">
                Regards,<br>Company HR<br>SkillMatch AI
            </p>
        </div>
    </body>
    </html>
    """

    text_body = f"""
Hello {candidate_name},

Your technical skill assessment has been assigned by your company HR.

Assessment Level: {level} - {difficulty}

Your login email: {candidate_email}
Your login password: {candidate_password}

Please visit the following link to log in and begin your assessment:
{assessment_link}

Regards,
Company HR
SkillMatch AI
    """

    if not is_smtp_configured():
        db = get_db_connection()
        try:
            db.execute(
                "INSERT INTO email_logs (candidate_id, to_email, subject, body, status) VALUES (%s, %s, %s, %s, %s)",
                (None, candidate_email, subject, text_body, "demo_mode_not_sent"),
            )
            db.commit()
        finally:
            db.close()

        return {
            "success": True,
            "message": f"Demo mode: Email not sent (SMTP not configured). Assessment link and password have been generated.",
            "actually_sent": False,
            "demo_mode": True,
            "assessment_link": assessment_link,
            "candidate_password": candidate_password,
            "candidate": {
                "name": candidate_name,
                "email": candidate_email,
            },
            "assessment": {
                "id": assessment_id,
                "level": level,
            },
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_USERNAME}>"
        msg["To"] = candidate_email
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, candidate_email, msg.as_string())

        log_status = "sent"
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)[:150]}",
            "actually_sent": False,
            "assessment_link": assessment_link,
            "candidate_password": candidate_password,
        }

    db = get_db_connection()
    try:
        db.execute(
            "INSERT INTO email_logs (candidate_id, to_email, subject, body, status) VALUES (%s, %s, %s, %s, %s)",
            (None, candidate_email, subject, text_body, log_status),
        )
        db.commit()
    finally:
        db.close()

    return {
        "success": True,
        "message": f"Assessment invitation sent successfully to {candidate_email}",
        "actually_sent": True,
        "candidate": {
            "name": candidate_name,
            "email": candidate_email,
        },
        "assessment": {
            "id": assessment_id,
            "level": level,
        },
    }
