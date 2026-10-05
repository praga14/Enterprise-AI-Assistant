from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.schemas.permission import PermissionCreate, PermissionUpdate
from app.services.audit_log_service import create_audit_log


def create_permission(
    db: Session,
    permission_data: PermissionCreate,
    actor_user_id: int,
) -> Permission:

    permission = Permission(
        name=permission_data.name,
        description=permission_data.description,
        resource=permission_data.resource,
        action=permission_data.action,
        is_system=False,
    )

    db.add(permission)
    db.flush()

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="CREATE_PERMISSION",
        resource_type="PERMISSION",
        resource_id=permission.id,
        details=f"Permission '{permission.name}' created",
    )

    db.commit()
    db.refresh(permission)

    return permission


def get_permissions(db: Session) -> list[Permission]:
    return db.query(Permission).all()


def update_permission(
    db: Session,
    permission_id: int,
    permission_data: PermissionUpdate,
    actor_user_id: int,
) -> Permission:

    permission = db.get(Permission, permission_id)

    if permission is None:
        raise ValueError("Permission not found")

    if permission.is_system:
        raise ValueError("System permissions cannot be modified")

    changes = permission_data.model_dump(
        exclude_unset=True
    )

    for field, value in changes.items():
        setattr(permission, field, value)

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="UPDATE_PERMISSION",
        resource_type="PERMISSION",
        resource_id=permission.id,
        details=f"Permission '{permission.name}' updated",
    )

    db.commit()
    db.refresh(permission)

    return permission


def delete_permission(
    db: Session,
    permission_id: int,
    actor_user_id: int,
) -> None:

    permission = db.get(Permission, permission_id)

    if permission is None:
        raise ValueError("Permission not found")

    if permission.is_system:
        raise ValueError("System permissions cannot be deleted")

    db.query(RolePermission).filter(
        RolePermission.permission_id == permission_id
    ).delete()

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="DELETE_PERMISSION",
        resource_type="PERMISSION",
        resource_id=permission.id,
        details=f"Permission '{permission.name}' deleted",
    )

    db.delete(permission)
    db.commit()


def user_has_permission(
    db: Session,
    user_id: int,
    permission_name: str,
) -> bool:

    statement = (
        select(Permission.id)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id,
        )
        .join(
            UserRole,
            UserRole.role_id == RolePermission.role_id,
        )
        .where(
            UserRole.user_id == user_id,
            Permission.name == permission_name,
            Permission.is_active.is_(True),
        )
    )

    permission_id = db.scalar(statement)

    return permission_id is not None