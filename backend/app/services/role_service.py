
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.schemas.role import RoleCreate
from app.services.audit_log_service import create_audit_log


def create_role(
    db: Session,
    role_data: RoleCreate,
    actor_user_id: int,
) -> Role:

    role = Role(
        name=role_data.name,
        description=role_data.description,
    )

    db.add(role)
    db.flush()

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="CREATE_ROLE",
        resource_type="ROLE",
        resource_id=role.id,
        details=f"Role '{role.name}' created",
    )

    db.commit()
    db.refresh(role)

    return role


def get_roles(db: Session) -> list[Role]:
    return db.query(Role).all()


def delete_role(
    db: Session,
    role_id: int,
    actor_user_id: int,
) -> None:

    role = db.get(Role, role_id)

    if role is None:
        raise ValueError("Role not found")

    if role.is_system:
        raise ValueError("System roles cannot be deleted")

    db.query(RolePermission).filter(
        RolePermission.role_id == role_id
    ).delete()

    db.query(UserRole).filter(
        UserRole.role_id == role_id
    ).delete()

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="DELETE_ROLE",
        resource_type="ROLE",
        resource_id=role.id,
        details=f"Role '{role.name}' deleted",
    )

    db.delete(role)
    db.commit()


def deactivate_role(
    db: Session,
    role_id: int,
    actor_user_id: int,
) -> Role:

    role = db.get(Role, role_id)

    if role is None:
        raise ValueError("Role not found")

    if role.is_system:
        raise ValueError("System roles cannot be deactivated")

    if not role.is_active:
        raise ValueError("Role is already inactive")

    role.is_active = False

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="DEACTIVATE_ROLE",
        resource_type="ROLE",
        resource_id=role.id,
        details=f"Role '{role.name}' deactivated",
    )

    db.commit()
    db.refresh(role)

    return role


def reactivate_role(
    db: Session,
    role_id: int,
    actor_user_id: int,
) -> Role:

    role = db.get(Role, role_id)

    if role is None:
        raise ValueError("Role not found")

    if role.is_system:
        raise ValueError("System roles cannot be reactivated")

    if role.is_active:
        raise ValueError("Role is already active")

    role.is_active = True

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="REACTIVATE_ROLE",
        resource_type="ROLE",
        resource_id=role.id,
        details=f"Role '{role.name}' reactivated",
    )

    db.commit()
    db.refresh(role)

    return role