from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user_role import UserRoleCreate
from app.services.user_role_service import assign_role_to_user
from app.core.dependencies import require_permission
from app.models.user import User


router = APIRouter(
    prefix="/api/user-roles",
    tags=["User Roles"],
)


@router.post("/")
def assign_role(
    data: UserRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("access.grant")
    ),
):
    try:
        return assign_role_to_user(
            db=db,
            user_id=data.user_id,
            role_id=data.role_id,
            actor_user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )