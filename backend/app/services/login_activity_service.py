from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def get_logins_for_date(
    db: Session,
    login_date: date,
):
    start_datetime = datetime.combine(
        login_date,
        time.min,
    )

    end_datetime = datetime.combine(
        login_date,
        time.max,
    )

    statement = (
        select(AuditLog, User)
        .join(User, User.id == AuditLog.actor_user_id)
        .where(
            AuditLog.action == "LOGIN",
            AuditLog.created_at >= start_datetime,
            AuditLog.created_at <= end_datetime,
        )
        .order_by(AuditLog.created_at.asc())
    )

    return db.execute(statement).all()


def answer_login_activity(
    db: Session,
    question: str,
) -> dict:
    normalized = question.lower().strip()

    if "yesterday" in normalized:
        login_date = date.today() - timedelta(days=1)
    else:
        login_date = date.today()

    rows = get_logins_for_date(
        db=db,
        login_date=login_date,
    )

    logins = []

    for audit_log, user in rows:
        logins.append({
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "login_time": audit_log.created_at,
        })

    if not logins:
        answer = f"No login activity was recorded for {login_date}."
    else:
        lines = [
            f"- {item['full_name']} ({item['username']}) — "
            f"{item['login_time'].strftime('%I:%M %p')}"
            for item in logins
        ]

        answer = (
            f"Login activity for {login_date}:\n"
            + "\n".join(lines)
        )

    return {
        "question_type": "login_activity",
        "date": str(login_date),
        "login_count": len(logins),
        "logins": logins,
        "answer": answer,
    }