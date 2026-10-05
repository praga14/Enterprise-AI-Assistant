from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.db.dependencies import get_db
from app.models.user import User
from app.services.user_document_access_service import (
    get_user_document_access,
    get_all_user_document_access as get_all_user_documents,
)

router = APIRouter(
    prefix="/user-access",
    tags=["User Document Access"],
)



@router.get("/{username}")
def get_all_user_document_access(
    username: str,
    current_user: User = Depends(
        require_permission("document.access.read")
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_all_user_documents(
            db=db,
            username=username,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )



@router.get("/{username}/{document_name}")
def user_document_access(
    username: str,
    document_name: str,
    current_user: User = Depends(
        require_permission("document.access.read")
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_user_document_access(
            db=db,
            username=username,
            document_name=document_name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )