from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.audit_log_service import get_audit_logs


from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def format_audit_time(dt: datetime, include_date: bool = False) -> str:
    """
    Audit timestamps are stored as naive UTC datetimes.
    Convert them to India Standard Time for display.
    """

    if dt is None:
        return "-"

    # Database datetime is naive UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    dt_ist = dt.astimezone(IST)

    if include_date:
        return dt_ist.strftime("%d/%m/%Y, %I:%M:%S %p")

    return dt_ist.strftime("%I:%M %p")


def extract_audit_date(question: str) -> date:
    normalized = question.lower().strip()

    if "today" in normalized:
        return date.today()

    if "yesterday" in normalized:
        return date.today() - timedelta(days=1)

    for date_format in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        for word in normalized.replace("?", " ").split():
            try:
                return datetime.strptime(word, date_format).date()
            except ValueError:
                continue

    return date.today()


def build_audit_records(
    db: Session,
    logs,
) -> list:
    """
    Convert audit log database records into frontend-friendly
    structured records.
    """

    # Collect actor user IDs
    actor_ids = {
        log.actor_user_id
        for log in logs
        if log.actor_user_id is not None
    }

    # Collect target user IDs
    target_user_ids = {
        log.target_user_id
        for log in logs
        if log.target_user_id is not None
    }

    # Lookup both actor and target users in one query
    user_ids = actor_ids | target_user_ids

    users = {}

    if user_ids:
        statement = select(User).where(
            User.id.in_(user_ids)
        )

        users = {
            user.id: user
            for user in db.scalars(statement).all()
        }

    activities = []
    audit_records = []

    for log in logs:

        # -----------------------------
        # Actor
        # -----------------------------

        actor = users.get(log.actor_user_id)

        actor_username = (
            actor.username
            if actor
            else None
        )

        actor_full_name = (
            actor.full_name
            if actor
            else None
        )

        actor_name = (
            actor_full_name
            or actor_username
            or "System"
        )

        # -----------------------------
        # Target user
        # -----------------------------

        target_user = users.get(log.target_user_id)

        target_username = (
            target_user.username
            if target_user
            else None
        )

        target_full_name = (
            target_user.full_name
            if target_user
            else None
        )

        target_name = (
            target_full_name
            or target_username
            if target_user
            else None
        )

        # -----------------------------
        # Existing activity structure
        # -----------------------------

        activities.append({
            "id": log.id,
            "actor_user_id": log.actor_user_id,
            "actor_username": actor_username,
            "actor_full_name": actor_full_name,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "target_user_id": log.target_user_id,
            "target_username": target_username,
            "target_full_name": target_full_name,
            "details": log.details,
            "created_at": log.created_at,
        })

        # -----------------------------
        # Frontend table structure
        # -----------------------------

        audit_records.append({
            "id": log.id,
            "timestamp": (
                log.created_at.isoformat() + "Z"
                if log.created_at
                else None
            ),

            "actor": actor_name,
            "actor_username": actor_username,

            "action": log.action,

            "resource": log.resource_type,
            "resource_id": log.resource_id,

            "target_user_id": log.target_user_id,
            "target_user": target_name,
            "target_username": target_username,

            "details": log.details or "No details",
        })

    return activities, audit_records


def answer_recent_audit_activity(
    db: Session,
    question: str,
    resource_type: str | None = None,
    limit: int = 10,
) -> dict:

    logs, total = get_audit_logs(
        db=db,
        resource_type=resource_type,
        page=1,
        page_size=limit,
    )

    activities, audit_records = build_audit_records(
        db=db,
        logs=logs,
    )

    if not activities:
        answer = "No audit activity was recorded."
    else:
        lines = []

        for item in activities:
            actor_name = (
                item["actor_full_name"]
                or item["actor_username"]
                or "System"
            )

            timestamp = format_audit_time(
                item["created_at"],
                include_date=True,
            )

            lines.append(
                f"- {timestamp} - {actor_name} - "
                f"{item['action']} - {item['resource_type']} - "
                f"{item['details'] or 'No details'}"
            )

        answer = (
            f"Recent audit activity "
            f"({len(activities)} records):\n"
            + "\n".join(lines)
        )

    return {
        "question_type": "recent_audit_activity",
        "resource_type": resource_type,
        "total_available": total,
        "activity_count": len(activities),
        "activities": activities,
        "audit_records": audit_records,
        "answer": answer,
    }


def answer_audit_activity_by_date(
    db: Session,
    question: str,
    resource_type: str | None = None,
    username: str | None = None,
) -> dict:

    audit_date = extract_audit_date(question)

    target_user_id = None

    if username:
        statement = select(User).where(
            User.username.ilike(username)
        )

        target_user = db.scalar(statement)

        if target_user:
            target_user_id = target_user.id

    logs, total = get_audit_logs(
        db=db,
        target_user_id=target_user_id,
        resource_type=resource_type,
        from_date=audit_date,
        to_date=audit_date,
        page=1,
        page_size=50,
    )

    activities, audit_records = build_audit_records(
        db=db,
        logs=logs,
    )

    if not activities:
        answer = (
            f"No audit activity was recorded "
            f"for {audit_date}."
        )
    else:
        lines = []

        for item in activities:
            actor_name = (
                item["actor_full_name"]
                or item["actor_username"]
                or "System"
            )

            timestamp = format_audit_time(
                item["created_at"],
                include_date=False,
            )

            lines.append(
                f"- {timestamp} - {actor_name} - "
                f"{item['action']} - {item['resource_type']} - "
                f"{item['details'] or 'No details'}"
            )

        answer = (
            f"Audit activity for {audit_date} "
            f"({len(activities)} records):\n"
            + "\n".join(lines)
        )

    return {
        "question_type": "audit_activity_by_date",
        "date": str(audit_date),
        "username": username,
        "resource_type": resource_type,
        "activity_count": len(activities),
        "activities": activities,
        "audit_records": audit_records,
        "answer": answer,
    }