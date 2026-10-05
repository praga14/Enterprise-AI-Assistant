from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_role import DocumentRole
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.audit_log import AuditLog
from app.models.document_user import DocumentUser


def grant_document_access(
    db: Session,
    actor_user_id: int,
    username: str,
    document_id: int,
    role_id: int,
) -> dict:
    user = db.scalar(
        select(User).where(User.username == username)
    )

    if user is None:
        raise ValueError("User not found")

    document = db.get(Document, document_id)

    if document is None:
        raise ValueError("Document not found")

    role = db.get(Role, role_id)

    if role is None:
        raise ValueError("Role not found")

    user_has_role = db.scalar(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role_id,
        )
    )

    if user_has_role is None:
        raise ValueError(
            f"User does not have the {role.name} role"
        )

    existing_access = db.scalar(
        select(DocumentRole).where(
            DocumentRole.document_id == document_id,
            DocumentRole.role_id == role_id,
        )
    )

    if existing_access is not None:
        raise ValueError("Document access already exists")

    document_role = DocumentRole(
        document_id=document_id,
        role_id=role_id,
    )

    db.add(document_role)

    audit_log = AuditLog(
        actor_user_id=actor_user_id,
        action="grant",
        resource_type="document",
        resource_id=document.id,
        target_user_id=user.id,
        details=f"Granted {role.name} role access to document {document.name}",
    )

    db.add(audit_log)
    db.commit()

    return {
        "message": "Document access granted",
        "username": user.username,
        "document_id": document.id,
        "document_name": document.name,
        "role_id": role.id,
        "role_name": role.name,
    }


def revoke_document_access(
    db: Session,
    actor_user_id: int,
    document_id: int,
    role_id: int,
) -> dict:
    document = db.get(Document, document_id)

    if document is None:
        raise ValueError("Document not found")

    role = db.get(Role, role_id)

    if role is None:
        raise ValueError("Role not found")

    document_role = db.scalar(
        select(DocumentRole).where(
            DocumentRole.document_id == document_id,
            DocumentRole.role_id == role_id,
        )
    )

    if document_role is None:
        raise ValueError("Document access does not exist")

    db.delete(document_role)

    audit_log = AuditLog(
        actor_user_id=actor_user_id,
        action="revoke",
        resource_type="document",
        resource_id=document.id,
        details=f"Revoked {role.name} role access to document {document.name}",
    )

    db.add(audit_log)
    db.commit()

    return {
        "message": "Document access revoked",
        "document_id": document.id,
        "document_name": document.name,
        "role_id": role.id,
        "role_name": role.name,
    }


def grant_document_user_access(
    db: Session,
    actor_user_id: int,
    username: str,
    document_id: int,
) -> dict:
    user = db.scalar(
        select(User).where(User.username == username)
    )

    if user is None:
        raise ValueError("User not found")

    document = db.get(Document, document_id)

    if document is None:
        raise ValueError("Document not found")

    existing = db.scalar(
        select(DocumentUser).where(
            DocumentUser.document_id == document_id,
            DocumentUser.user_id == user.id,
        )
    )

    if existing is not None:
        raise ValueError(
            "Direct user access already exists"
        )

    document_user = DocumentUser(
        document_id=document.id,
        user_id=user.id,
    )

    db.add(document_user)

    audit_log = AuditLog(
        actor_user_id=actor_user_id,
        action="grant",
        resource_type="document_user",
        resource_id=document.id,
        target_user_id=user.id,
        details=(
            f"Granted direct access to user {user.username} "
            f"for document {document.name}"
        ),
    )

    db.add(audit_log)
    db.commit()

    return {
        "message": "Direct document access granted",
        "username": user.username,
        "document_id": document.id,
        "document_name": document.name,
        "access_type": "direct",
    }


def revoke_document_user_access(
    db: Session,
    actor_user_id: int,
    username: str,
    document_id: int,
) -> dict:
    user = db.scalar(
        select(User).where(User.username == username)
    )

    if user is None:
        raise ValueError("User not found")

    document = db.get(Document, document_id)

    if document is None:
        raise ValueError("Document not found")

    existing = db.scalar(
        select(DocumentUser).where(
            DocumentUser.document_id == document_id,
            DocumentUser.user_id == user.id,
        )
    )

    if existing is None:
        raise ValueError(
            "Direct user access does not exist"
        )

    db.delete(existing)

    audit_log = AuditLog(
        actor_user_id=actor_user_id,
        action="revoke",
        resource_type="document_user",
        resource_id=document.id,
        target_user_id=user.id,
        details=(
            f"Revoked direct access from user {user.username} "
            f"for document {document.name}"
        ),
    )

    db.add(audit_log)
    db.commit()

    return {
        "message": "Direct document access revoked",
        "username": user.username,
        "document_id": document.id,
        "document_name": document.name,
        "access_type": "direct",
    }