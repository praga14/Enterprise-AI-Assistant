from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.services.audit_log_service import create_audit_log


def assign_permission_to_role(
    db: Session,
    role_id: int,
    permission_id: int,
    actor_user_id: int,
) -> RolePermission:

    role = db.get(Role, role_id)

    if role is None:
        raise ValueError("Role not found")

    if role.is_system:
        raise ValueError(
            "System role permissions can only be changed through backend administration"
        )

    if not role.is_active:
        raise ValueError("Cannot assign permission to an inactive role")

    permission = db.get(Permission, permission_id)

    if permission is None:
        raise ValueError("Permission not found")

    if not permission.is_active:
        raise ValueError("Cannot assign an inactive permission")

    existing_assignment = db.scalar(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
    )

    if existing_assignment:
        raise ValueError("Permission already assigned to role")

    role_permission = RolePermission(
        role_id=role_id,
        permission_id=permission_id,
    )

    db.add(role_permission)

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="GRANT_PERMISSION",
        resource_type="PERMISSION",
        resource_id=permission_id,
        details=(
            f"Permission '{permission.name}' granted "
            f"to role '{role.name}'"
        ),
    )

    db.commit()
    db.refresh(role_permission)

    return role_permission

def get_role_permissions(
    db: Session,
    role_id: int,
) -> list[Permission]:
    role = db.get(Role, role_id)

    if role is None:
        raise ValueError("Role not found")

    statement = (
        select(Permission)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id,
        )
        .where(
            RolePermission.role_id == role_id,
        )
    )

    return list(db.scalars(statement).all())

def remove_permission_from_role(
    db: Session,
    role_id: int,
    permission_id: int,
    actor_user_id: int,
) -> None:

    role = db.get(Role, role_id)

    if role is None:
        raise ValueError("Role not found")

    if role.is_system:
        raise ValueError(
            "System role permissions can only be changed through backend administration"
        )

    permission = db.get(Permission, permission_id)

    if permission is None:
        raise ValueError("Permission not found")

    role_permission = db.scalar(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
    )

    if role_permission is None:
        raise ValueError(
            "Permission is not assigned to this role"
        )

    db.delete(role_permission)

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="REVOKE_PERMISSION",
        resource_type="PERMISSION",
        resource_id=permission_id,
        details=(
            f"Permission '{permission.name}' revoked "
            f"from role '{role.name}'"
        ),
    )

    db.commit()