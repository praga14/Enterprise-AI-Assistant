from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db

from app.models.user import User
from app.models.document import Document
from app.models.chat_message import ChatMessage
from app.models.audit_log import AuditLog


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # -----------------------------
    # Total users
    # -----------------------------
    total_users = db.scalar(
        select(func.count(User.id))
    ) or 0

    # -----------------------------
    # Active users
    # -----------------------------
    active_users = db.scalar(
        select(func.count(User.id))
        .where(User.is_active.is_(True))
    ) or 0

    # -----------------------------
    # Total documents
    # -----------------------------
    documents = db.scalar(
        select(func.count(Document.id))
    ) or 0

    # -----------------------------
    # AI conversations
    #
    # There is currently no separate
    # conversation/session table.
    #
    # Therefore each assistant response
    # is counted as one AI interaction.
    # -----------------------------
    ai_conversations = db.scalar(
        select(func.count(ChatMessage.id))
        .where(ChatMessage.role == "assistant")
    ) or 0

    # -----------------------------
    # Total audit events
    # -----------------------------
    audit_events = db.scalar(
        select(func.count(AuditLog.id))
    ) or 0

    # -----------------------------
    # Recent activity
    # -----------------------------
    actor_user = aliased(User)
    target_user = aliased(User)

    recent_statement = (
        select(
            AuditLog.id,
            AuditLog.action,
            AuditLog.resource_type,
            AuditLog.resource_id,
            AuditLog.details,
            AuditLog.created_at,

            actor_user.username.label("actor_username"),
            actor_user.full_name.label("actor_full_name"),

            target_user.username.label("target_username"),
            target_user.full_name.label("target_full_name"),
        )
        .outerjoin(
            actor_user,
            AuditLog.actor_user_id == actor_user.id,
        )
        .outerjoin(
            target_user,
            AuditLog.target_user_id == target_user.id,
        )
        .order_by(
            AuditLog.created_at.desc()
        )
        .limit(5)
    )

    recent_records = db.execute(recent_statement).all()

    recent_activity = []

    for record in recent_records:

        timestamp = None

        if record.created_at:
            timestamp = record.created_at.isoformat()

            # Audit timestamps are stored as UTC without
            # timezone information in the current database.
            if not timestamp.endswith("Z"):
                timestamp += "Z"

        recent_activity.append(
            {
                "id": record.id,
                "timestamp": timestamp,
                "action": record.action,
                "resource": record.resource_type,
                "resource_id": record.resource_id,
                "actor": (
                    record.actor_full_name
                    or record.actor_username
                    or "-"
                ),
                "actor_username": record.actor_username,
                "target_user": record.target_full_name,
                "target_username": record.target_username,
                "details": record.details,
            }
        )

    return {
        "total_users": total_users,
        "active_users": active_users,
        "documents": documents,
        "ai_conversations": ai_conversations,
        "audit_events": audit_events,
        "recent_activity": recent_activity,
    }