from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.permission import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
)
from app.services.permission_service import (
    create_permission,
    get_permissions,
    update_permission,
    delete_permission,
)
from app.core.dependencies import require_permission
from app.models.user import User
from app.models.permission import Permission
from app.services.audit_service import create_audit_log

router = APIRouter(
    prefix="/api/permissions",
    tags=["Permissions"],
)


@router.post(
    "/",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_permission_endpoint(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("permission.manage")
    ),
):
    return create_permission(
        db=db,
        permission_data=permission_data,
        actor_user_id=current_user.id,
    )


@router.get(
    "/",
    response_model=list[PermissionResponse],
)
def get_permissions_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("permission.read")
    ),
):
    return get_permissions(db)


@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
)
def update_permission_endpoint(
    permission_id: int,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("permission.manage")
    ),
):
    try:
        return update_permission(
            db=db,
            permission_id=permission_id,
            permission_data=permission_data,
            actor_user_id=current_user.id,
        )

    except ValueError as exc:
        message = str(exc)

        if "System permissions cannot be modified" in message:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )


@router.delete("/{permission_id}")
def delete_permission_endpoint(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("permission.manage")
    ),
):
    try:
        delete_permission(
            db=db,
            permission_id=permission_id,
            actor_user_id=current_user.id,
        )

        return {
            "message": "Permission deleted successfully",
            "permission_id": permission_id,
        }

    except ValueError as exc:
        message = str(exc)

        if "System permissions cannot be deleted" in message:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )

@router.post("/{permission_id}/system-status")
def change_permission_system_status(
    permission_id: int,
    is_system: bool,
    current_user: User = Depends(
        require_permission("system.permission.manage")
    ),
    db: Session = Depends(get_db),
):
    permission = db.get(Permission, permission_id)

    if permission is None:
        raise HTTPException(
            status_code=404,
            detail="Permission not found",
        )

    old_status = permission.is_system

    if old_status == is_system:
        return {
            "success": False,
            "permission_id": permission.id,
            "name": permission.name,
            "is_system": permission.is_system,
            "message": "Permission system status is already set to this value.",
        }

    permission.is_system = is_system

    db.commit()
    db.refresh(permission)

    create_audit_log(
        db=db,
        actor_user_id=current_user.id,
        action="permission.system_status.change",
        resource_type="PERMISSION",
        resource_id=permission.id,
        details=(
            f"Changed permission '{permission.name}' system status "
            f"from {old_status} to {is_system}"
        ),
    )

    return {
        "success": True,
        "permission_id": permission.id,
        "name": permission.name,
        "is_system": permission.is_system,
    }