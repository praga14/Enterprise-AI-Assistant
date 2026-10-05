from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.db.dependencies import get_db
from app.models.user import User
from app.services.access_query_service import get_document_access_by_name

router = APIRouter(
    prefix="/access-query",
    tags=["Access Query"],
)


@router.get("/document/{document_name}")
def document_access_query(
    document_name: str,
    current_user: User = Depends(
        require_permission("document.access.read")
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_document_access_by_name(
            db=db,
            document_name=document_name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )