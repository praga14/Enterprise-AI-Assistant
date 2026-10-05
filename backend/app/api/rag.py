from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.services.rag_service import ask_rag
from app.schemas.rag import RAGRequest


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


@router.post("/ask")
def ask_question(
    request: RAGRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ask_rag(
        db=db,
        question=request.question,
        user_id=current_user.id,
        top_k=request.top_k,
        similarity_threshold=request.similarity_threshold,
    )