from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.db.dependencies import get_db
from app.models.user import User
from app.services.document_access_management_service import (
    grant_document_access,
    revoke_document_access,
    grant_document_user_access,
    revoke_document_user_access,
)

router = APIRouter(
    prefix="/document-access",
    tags=["Document Access Management"],
)


@router.post("/grant")
def grant_access(
    username: str,
    document_id: int,
    role_id: int,
    current_user: User = Depends(
        require_permission("access.grant")
    ),
    db: Session = Depends(get_db),
):
    try:
        return grant_document_access(
            db=db,
            actor_user_id=current_user.id,
            username=username,
            document_id=document_id,
            role_id=role_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.delete("/revoke")
def revoke_access(
    document_id: int,
    role_id: int,
    current_user: User = Depends(
        require_permission("access.grant")
    ),
    db: Session = Depends(get_db),
):
    try:
        return revoke_document_access(
            db=db,
            actor_user_id=current_user.id,
            document_id=document_id,
            role_id=role_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/grant-user")
def grant_user_access(
    username: str,
    document_id: int,
    current_user: User = Depends(
        require_permission("access.grant")
    ),
    db: Session = Depends(get_db),
):
    try:
        return grant_document_user_access(
            db=db,
            actor_user_id=current_user.id,
            username=username,
            document_id=document_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))



@router.delete("/revoke-user")
def revoke_user_access(
    username: str,
    document_id: int,
    current_user: User = Depends(
        require_permission("access.grant")
    ),
    db: Session = Depends(get_db),
):
    try:
        return revoke_document_user_access(
            db=db,
            actor_user_id=current_user.id,
            username=username,
            document_id=document_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))