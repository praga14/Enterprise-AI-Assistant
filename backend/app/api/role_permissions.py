from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.role_permission import RolePermissionCreate
from app.services.role_permission_service import (
    assign_permission_to_role,
    remove_permission_from_role,
)
from app.core.dependencies import require_permission
from app.models.user import User


router = APIRouter(
    prefix="/api/role-permissions",
    tags=["Role Permissions"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
def assign_permission(
    data: RolePermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("access.grant")
    ),
):
    try:
        role_permission = assign_permission_to_role(
            db=db,
            role_id=data.role_id,
            permission_id=data.permission_id,
            actor_user_id=current_user.id,
        )

        return {
            "message": "Permission assigned successfully",
            "role_id": role_permission.role_id,
            "permission_id": role_permission.permission_id,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

@router.delete("/{role_id}/{permission_id}")
def remove_permission(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("access.grant")
    ),
):
    try:
        remove_permission_from_role(
            db=db,
            role_id=role_id,
            permission_id=permission_id,
            actor_user_id=current_user.id,
        )

        return {
            "message": "Permission removed successfully",
            "role_id": role_id,
            "permission_id": permission_id,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )