from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.document_access_service import get_document_access


def find_document_by_name(
    db: Session,
    document_name: str,
) -> Document | None:
    statement = (
        select(Document)
        .where(Document.name.ilike(f"%{document_name.strip()}%"))
        .limit(1)
    )

    return db.scalar(statement)


def get_document_access_by_name(
    db: Session,
    document_name: str,
) -> dict:
    document = find_document_by_name(
        db=db,
        document_name=document_name,
    )

    if document is None:
        raise ValueError("Document not found")

    return get_document_access(
        db=db,
        document_id=document.id,
    )