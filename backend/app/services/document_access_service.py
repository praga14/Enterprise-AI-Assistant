from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_role import DocumentRole
from app.models.document_user import DocumentUser
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole


def get_document_access(db: Session, document_id: int) -> dict:
    document = db.get(Document, document_id)

    if document is None:
        raise ValueError("Document not found")

    access_map = {}

    # Role-based access
    role_statement = (
        select(User, Role)
        .join(UserRole, UserRole.user_id == User.id)
        .join(Role, Role.id == UserRole.role_id)
        .join(DocumentRole, DocumentRole.role_id == Role.id)
        .where(DocumentRole.document_id == document_id)
    )

    role_rows = db.execute(role_statement).all()

    for user, role in role_rows:
        if user.id not in access_map:
            access_map[user.id] = {
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "access_type": "role",
                "access_reason": f"{role.name} role",
                "role_id": role.id,
                "role_name": role.name,
            }

    # Direct user access
    direct_statement = (
        select(User)
        .join(
            DocumentUser,
            DocumentUser.user_id == User.id,
        )
        .where(DocumentUser.document_id == document_id)
    )

    direct_users = db.execute(direct_statement).scalars().all()

    for user in direct_users:
        if user.id in access_map:
            access_map[user.id]["access_type"] = "role + direct"
            access_map[user.id]["access_reason"] += "; Direct user access"
        else:
            access_map[user.id] = {
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "access_type": "direct",
                "access_reason": "Direct user access",
                "role_id": None,
                "role_name": None,
            }

    return {
        "document_id": document.id,
        "document_name": document.name,
        "users": list(access_map.values()),
    }


def grant_document_access(
    db: Session,
    user_id: int,
    document_id: int,
) -> bool:
    existing_access = db.scalar(
        select(DocumentUser).where(
            DocumentUser.user_id == user_id,
            DocumentUser.document_id == document_id,
        )
    )

    if existing_access is not None:
        return False

    db.add(
        DocumentUser(
            user_id=user_id,
            document_id=document_id,
        )
    )

    db.commit()

    return True

def revoke_document_access(
    db: Session,
    user_id: int,
    document_id: int,
) -> bool:
    access = db.scalar(
        select(DocumentUser).where(
            DocumentUser.user_id == user_id,
            DocumentUser.document_id == document_id,
        )
    )

    if access is None:
        return False

    db.delete(access)
    db.commit()

    return True
