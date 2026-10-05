from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.role import RoleCreate, RoleResponse
from app.services.role_service import (
    create_role,
    get_roles,
    delete_role,
    deactivate_role,
    reactivate_role,
)
from app.services.role_permission_service import (
    get_role_permissions,
    remove_permission_from_role,
)
from app.core.dependencies import require_permission
from app.models.user import User
from app.models.role import Role
from app.services.audit_service import create_audit_log

router = APIRouter(
    prefix="/api/roles",
    tags=["Roles"],
)


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role_endpoint(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("role.manage")
    ),
):
    return create_role(
        db=db,
        role_data=role_data,
        actor_user_id=current_user.id,
    )



@router.get(
    "/",
    response_model=list[RoleResponse],
)
def get_roles_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("role.read")
    ),
):
    return get_roles(db)


@router.patch("/{role_id}/deactivate", response_model=RoleResponse)
def deactivate_role_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("role.manage")
    ),
):
    try:
        return deactivate_role(
            db=db,
            role_id=role_id,
            actor_user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.patch("/{role_id}/reactivate", response_model=RoleResponse)
def reactivate_role_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("role.manage")
    ),
):
    try:
        return reactivate_role(
            db=db,
            role_id=role_id,
            actor_user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

@router.delete("/{role_id}")
def delete_role_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("role.manage")
    ),
):
    try:
        delete_role(
            db=db,
            role_id=role_id,
            actor_user_id=current_user.id,
        )

        return {
            "message": "Role deleted successfully",
            "role_id": role_id,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )



@router.get("/{role_id}/permissions")
def get_role_permissions_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("role.read")
    ),
):
    try:
        permissions = get_role_permissions(
            db,
            role_id,
        )

        return permissions

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )



@router.delete("/{role_id}/permissions/{permission_id}")
def remove_permission_from_role_endpoint(
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
            "message": "Permission removed from role successfully",
            "role_id": role_id,
            "permission_id": permission_id,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post("/{role_id}/system-status")
def change_role_system_status(
    role_id: int,
    is_system: bool,
    current_user: User = Depends(
        require_permission("system.role.manage")
    ),
    db: Session = Depends(get_db),
):
    role = db.get(Role, role_id)

    if role is None:
        raise HTTPException(
            status_code=404,
            detail="Role not found",
        )

    old_status = role.is_system

    if old_status == is_system:
        return {
            "success": False,
            "role_id": role.id,
            "name": role.name,
            "is_system": role.is_system,
            "message": "Role system status is already set to this value.",
        }

    role.is_system = is_system

    db.commit()
    db.refresh(role)

    create_audit_log(
        db=db,
        actor_user_id=current_user.id,
        action="role.system_status.change",
        resource_type="ROLE",
        resource_id=role.id,
        details=(
            f"Changed role '{role.name}' system status "
            f"from {old_status} to {is_system}"
        ),
    )

    return {
        "success": True,
        "role_id": role.id,
        "name": role.name,
        "is_system": role.is_system,
    }