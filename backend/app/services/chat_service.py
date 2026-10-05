from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage

def save_message(
    db: Session,
    user_id: int,
    role: str,
    content: str,
) -> ChatMessage:
    message = ChatMessage(
        user_id=user_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_chat_history(
    db: Session,
    user_id: int,
    limit: int = 10,
) -> list[ChatMessage]:
    messages = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    ).all()

    return list(reversed(messages))




def search_chat_history(
    db: Session,
    user_id: int,
    search_terms: list[str],
    limit: int = 30,
) -> list[ChatMessage]:

    conditions = []

    for term in search_terms:
        if not term:
            continue

        pattern = f"%{term}%"

        conditions.append(
            ChatMessage.content.ilike(pattern)
        )

    if not conditions:
        return []

    statement = (
        select(ChatMessage)
        .where(
            ChatMessage.user_id == user_id,
            or_(*conditions),
        )
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )

    return list(db.scalars(statement).all())