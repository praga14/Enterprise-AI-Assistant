from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.core.dependencies import require_permission
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_log_service import get_audit_logs
import math
from datetime import date


router = APIRouter(
    prefix="/api/audit-logs",
    tags=["Audit Logs"],
)


@router.get("/")
def get_audit_logs_endpoint(
    actor_user_id: int | None = Query(default=None),
    target_user_id: int | None = Query(default=None),
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),

    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),

    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),

    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("audit.read")
    ),
):
    items, total = get_audit_logs(
    db=db,
    actor_user_id=actor_user_id,
    target_user_id=target_user_id,
    action=action,
    resource_type=resource_type,
    from_date=from_date,
    to_date=to_date,
    page=page,
    page_size=page_size,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }