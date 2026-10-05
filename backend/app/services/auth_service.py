from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> User | None:
    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_user_access_token(user: User) -> str:
    return create_access_token(
        {
            "sub": str(user.id),
            "username": user.username,
        }
    )