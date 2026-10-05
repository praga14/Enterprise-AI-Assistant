from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.models.document_role import DocumentRole
from app.models.document_user import DocumentUser



def get_user_permissions(db: Session, user_id: int) -> list[Permission]:
    user = db.get(User, user_id)

    if user is None:
        raise ValueError("User not found")

    # Inactive users have no effective permissions
    if not user.is_active:
        return []

    statement = (
        select(Permission)
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
            Permission.is_active.is_(True),
        )
        .distinct()
    )

    return list(db.scalars(statement).all())


def user_can_access_document(
    db: Session,
    user_id: int,
    document_id: int,
) -> bool:
    # Direct user access
    direct_access = db.scalar(
        select(DocumentUser.document_id).where(
            DocumentUser.user_id == user_id,
            DocumentUser.document_id == document_id,
        )
    )

    if direct_access is not None:
        return True

    # Role-based access
    role_access = db.scalar(
        select(DocumentRole.document_id)
        .join(
            UserRole,
            UserRole.role_id == DocumentRole.role_id,
        )
        .where(
            UserRole.user_id == user_id,
            DocumentRole.document_id == document_id,
        )
    )

    return role_access is not None

def user_has_permission(
    db: Session,
    user_id: int,
    permission_name: str,
) -> bool:
    permissions = get_user_permissions(db, user_id)

    return any(
        permission.name == permission_name
        for permission in permissions
    )


def find_user_by_name(
    db: Session,
    name: str,
) -> User | None:
    normalized_name = name.strip()

    statement = (
        select(User)
        .where(
            (User.username.ilike(normalized_name))
            | (User.full_name.ilike(normalized_name))
        )
        .limit(1)
    )

    return db.scalar(statement)