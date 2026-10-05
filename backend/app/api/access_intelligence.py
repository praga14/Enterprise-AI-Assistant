from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_permission
from app.db.dependencies import get_db
from app.models.user import User
from app.services.access_intelligence_service import (
    answer_access_question,
    answer_my_permissions,
    perform_document_access_action,
)

router = APIRouter(
    prefix="/access-intelligence",
    tags=["Access Intelligence"],
)


@router.get("/me/permissions")
def my_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return answer_my_permissions(
        db=db,
        user_id=current_user.id,
    )


@router.get("/document/{document_name}")
def document_access_intelligence(
    document_name: str,
    current_user: User = Depends(
        require_permission("document.access.read")
    ),
    db: Session = Depends(get_db),
):
    try:
        return answer_access_question(
            db=db,
            document_name=document_name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

@router.post("/document/access")
def manage_document_access(
    username: str,
    document_name: str,
    action: str,
    current_user: User = Depends(
        require_permission("access.grant")
    ),
    db: Session = Depends(get_db),
):
    try:
        return perform_document_access_action(
            db=db,
            action=action,
            username=username,
            document_name=document_name,
            actor_user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )