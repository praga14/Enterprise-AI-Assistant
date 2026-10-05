from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.db.dependencies import get_db
from app.models.user import User
from app.services.document_access_service import get_document_access

router = APIRouter(
    prefix="/documents",
    tags=["Document Access"],
)


@router.get("/{document_id}/access")
def get_document_access_info(
    document_id: int,
    current_user: User = Depends(
        require_permission("document.access.read")
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_document_access(
            db=db,
            document_id=document_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )