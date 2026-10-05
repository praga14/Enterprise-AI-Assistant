from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.document_role import DocumentRole
from app.models.user_role import UserRole
from app.models.document_user import DocumentUser

from app.services.embedding_service import generate_embedding


def search_similar_chunks(
    db: Session,
    query: str,
    user_id: int,
    top_k: int = 5,
    similarity_threshold: float = 0.30,
    relevance_threshold: float = 0.40,
):
    """
    Retrieve relevant document chunks that the current user
    is authorized to access.

    Access can come from:
    1. A role assigned to the user
    2. Direct document access assigned to the user

    Retrieval happens in two stages:
    1. Retrieve candidate chunks using similarity_threshold.
    2. Keep only sufficiently relevant candidates using
       relevance_threshold.
    """

    query_embedding = generate_embedding(query)

    similarity = 1 - DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    results = (
        db.query(
            DocumentChunk,
            similarity.label("similarity"),
        )
        .outerjoin(
            DocumentRole,
            DocumentRole.document_id == DocumentChunk.document_id,
        )
        .outerjoin(
            UserRole,
            UserRole.role_id == DocumentRole.role_id,
        )
        .outerjoin(
            DocumentUser,
            DocumentUser.document_id == DocumentChunk.document_id,
        )
        .filter(
            or_(
                UserRole.user_id == user_id,
                DocumentUser.user_id == user_id,
            ),
            DocumentChunk.embedding.is_not(None),
            similarity >= similarity_threshold,
        )
        .distinct()
        .order_by(similarity.desc())
        .limit(top_k)
        .all()
    )

    # Remove weakly relevant results.
    relevant_results = [
        (chunk, score)
        for chunk, score in results
        if float(score) >= relevance_threshold
    ]

    return relevant_results