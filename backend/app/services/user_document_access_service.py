from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_role import DocumentRole
from app.models.document_user import DocumentUser
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.document_user import DocumentUser



def get_user_document_access(
    db: Session,
    username: str,
    document_name: str,
) -> dict:

    user = db.scalar(
        select(User).where(User.username == username)
    )

    if user is None:
        raise ValueError("User not found")

    document = db.scalar(
        select(Document).where(
            Document.name.ilike(document_name)
        )
    )

    if document is None:
        raise ValueError("Document not found")

    # Check direct user access
    direct_access = db.scalar(
        select(DocumentUser.document_id).where(
            DocumentUser.document_id == document.id,
            DocumentUser.user_id == user.id,
        )
    )

    if direct_access is not None:
        return {
            "username": user.username,
            "full_name": user.full_name,
            "document_id": document.id,
            "document_name": document.name,
            "access_type": "direct",
            "access_reason": "Direct user access",
            "role_id": None,
            "role_name": None,
        }

    # Check role-based access
    statement = (
        select(Role)
        .join(
            UserRole,
            UserRole.role_id == Role.id,
        )
        .join(
            DocumentRole,
            DocumentRole.role_id == Role.id,
        )
        .where(
            UserRole.user_id == user.id,
            DocumentRole.document_id == document.id,
        )
    )

    role = db.execute(statement).scalars().first()

    if role is None:
        raise ValueError(
            "User does not have access to this document"
        )

    return {
        "username": user.username,
        "full_name": user.full_name,
        "document_id": document.id,
        "document_name": document.name,
        "access_type": "role",
        "access_reason": f"{role.name} role",
        "role_id": role.id,
        "role_name": role.name,
    }






def get_all_user_document_access(
    db: Session,
    username: str,
) -> dict:

    user = db.scalar(
        select(User).where(User.username == username)
    )

    if user is None:
        raise ValueError("User not found")

    documents = {}

    # Role-based access
    role_statement = (
        select(Document, Role)
        .join(
            DocumentRole,
            DocumentRole.document_id == Document.id,
        )
        .join(
            UserRole,
            UserRole.role_id == DocumentRole.role_id,
        )
        .join(
            Role,
            Role.id == UserRole.role_id,
        )
        .where(
            UserRole.user_id == user.id
        )
    )

    role_rows = db.execute(role_statement).all()

    for document, role in role_rows:
        if document.id not in documents:
            documents[document.id] = {
                "document_id": document.id,
                "document_name": document.name,
                "access": [],
            }

        documents[document.id]["access"].append({
            "type": "role",
            "reason": f"{role.name} role",
            "role_id": role.id,
            "role_name": role.name,
        })

    # Direct user access
    direct_statement = (
        select(Document)
        .join(
            DocumentUser,
            DocumentUser.document_id == Document.id,
        )
        .where(
            DocumentUser.user_id == user.id
        )
    )

    direct_documents = (
        db.execute(direct_statement)
        .scalars()
        .all()
    )

    for document in direct_documents:
        if document.id not in documents:
            documents[document.id] = {
                "document_id": document.id,
                "document_name": document.name,
                "access": [],
            }

        documents[document.id]["access"].append({
            "type": "direct",
            "reason": "Direct user access",
            "role_id": None,
            "role_name": None,
        })

    return {
        "username": user.username,
        "full_name": user.full_name,
        "documents": list(documents.values()),
    }