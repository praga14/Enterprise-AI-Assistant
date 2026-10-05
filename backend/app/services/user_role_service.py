from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.services.audit_log_service import create_audit_log


def assign_role_to_user(
    db: Session,
    user_id: int,
    role_id: int,
    actor_user_id: int,
) -> UserRole:

    user = db.get(User, user_id)

    if user is None:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("Cannot assign a role to an inactive user")

    role = db.get(Role, role_id)

    if role is None:
        raise ValueError("Role not found")

    if not role.is_active:
        raise ValueError("Cannot assign an inactive role")

    if user_id == actor_user_id:
        raise ValueError("Users cannot assign roles to themselves")

    existing_assignment = db.scalar(
        select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
    )

    if existing_assignment:
        raise ValueError("Role already assigned to user")

    user_role = UserRole(
        user_id=user_id,
        role_id=role_id,
    )

    db.add(user_role)

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="GRANT_ROLE",
        resource_type="ROLE",
        resource_id=role_id,
        target_user_id=user_id,
        details=f"Role '{role.name}' granted to user '{user.username}'",
    )

    db.commit()
    db.refresh(user_role)

    return user_role


def get_user_roles(
    db: Session,
    user_id: int,
) -> list[Role]:

    user = db.get(User, user_id)

    if user is None:
        raise ValueError("User not found")

    statement = (
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
    )

    return list(db.scalars(statement).all())


def remove_role_from_user(
    db: Session,
    user_id: int,
    role_id: int,
    actor_user_id: int,
) -> None:

    user = db.get(User, user_id)

    if user is None:
        raise ValueError("User not found")

    role = db.get(Role, role_id)

    if role is None:
        raise ValueError("Role not found")

    user_role = db.scalar(
        select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
    )

    if user_role is None:
        raise ValueError("Role is not assigned to this user")

    db.delete(user_role)

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="REVOKE_ROLE",
        resource_type="ROLE",
        resource_id=role_id,
        target_user_id=user_id,
        details=f"Role '{role.name}' revoked from user '{user.username}'",
    )

    db.commit()