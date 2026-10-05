from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from datetime import datetime, date, time



def create_audit_log(
    db: Session,
    *,
    actor_user_id: int | None,
    action: str,
    resource_type: str,
    resource_id: int | None = None,
    target_user_id: int | None = None,
    details: str | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        target_user_id=target_user_id,
        details=details,
    )

    db.add(audit_log)

    return audit_log



def get_audit_logs(
    db: Session,
    actor_user_id: int | None = None,
    target_user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
):
    filters = []

    if actor_user_id is not None:
        filters.append(
            AuditLog.actor_user_id == actor_user_id
        )

    if target_user_id is not None:
        filters.append(
            AuditLog.target_user_id == target_user_id
        )

    if action is not None:
        filters.append(
            AuditLog.action == action
        )

    if resource_type is not None:
        filters.append(
            AuditLog.resource_type == resource_type
        )

    if from_date is not None:
        filters.append(
            AuditLog.created_at >= datetime.combine(
                from_date,
                time.min,
            )
        )

    if to_date is not None:
        filters.append(
            AuditLog.created_at <= datetime.combine(
                to_date,
                time.max,
            )
        )

    count_statement = select(
        func.count(AuditLog.id)
    ).where(*filters)

    total = db.scalar(count_statement) or 0

    statement = (
        select(AuditLog)
        .where(*filters)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    items = list(db.scalars(statement).all())

    return items, total