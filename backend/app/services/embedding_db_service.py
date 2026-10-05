from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


def generate_chunk_embedding(
    db: Session,
    chunk_id: int,
) -> DocumentChunk | None:
    chunk = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.id == chunk_id)
        .first()
    )

    if chunk is None:
        return None

    chunk.embedding = generate_embedding(chunk.content)

    db.commit()
    db.refresh(chunk)

    return chunk