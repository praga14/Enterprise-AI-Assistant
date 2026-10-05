from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import (
    authenticate_user,
    create_user_access_token,
)
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.audit_log_service import create_audit_log


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        login_data.username,
        login_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_user_access_token(user)
    create_audit_log(
        db,
        actor_user_id=user.id,
        action="LOGIN",
        resource_type="AUTH",
        resource_id=user.id,
        target_user_id=user.id,
        details=f"User '{user.username}' logged in",
    )

    db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "department": current_user.department,
    }