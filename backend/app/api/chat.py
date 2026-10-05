from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.chat import ChatMessageResponse
from app.services.chat_service import get_chat_history


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.get(
    "/history",
    response_model=list[ChatMessageResponse],
)
def chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_chat_history(
        db=db,
        user_id=current_user.id,
        limit=50,
    )