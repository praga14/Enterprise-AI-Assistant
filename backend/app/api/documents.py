import shutil
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db

from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

from app.schemas.document import DocumentResponse
from app.schemas.search import SearchResponse

from app.utils.document_parser import extract_text

from app.services.chunking_service import split_text
from app.services.embedding_service import generate_embedding
from app.services.retrieval_service import search_similar_chunks
from app.services.permission_service import user_has_permission
from app.services.audit_log_service import create_audit_log


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post(
    "/upload",
    response_model=DocumentResponse,
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Permission check
    # --------------------------------------------------------

    if not user_has_permission(
        db,
        current_user.id,
        "document.read",
    ):
        raise HTTPException(
            status_code=403,
            detail="Permission required: document.read",
        )

    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    # --------------------------------------------------------
    # Extract text
    # --------------------------------------------------------

    try:
        extracted_text = extract_text(
            str(file_path),
            extension.replace(".", ""),
        )

    except Exception as e:
        file_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract document text: {str(e)}",
        )

    # --------------------------------------------------------
    # Create document
    # --------------------------------------------------------

    document = Document(
        name=file.filename,
        file_type=extension.replace(".", ""),
        file_path=str(file_path),
        extracted_text=extracted_text,
        uploaded_by=current_user.id,
    )

    db.add(document)
    db.flush()

    # --------------------------------------------------------
    # Create chunks + embeddings
    # --------------------------------------------------------

    chunks = split_text(extracted_text)

    for index, chunk in enumerate(chunks):

        embedding = generate_embedding(chunk)

        document_chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk,
            embedding=embedding,
        )

        db.add(document_chunk)

    # --------------------------------------------------------
    # Audit log
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        actor_user_id=current_user.id,
        action="document.upload",
        resource_type="document",
        resource_id=document.id,
        details=f"Uploaded document '{document.name}'",
    )

    db.commit()
    db.refresh(document)

    return document


# ============================================================
# GET DOCUMENTS
# ============================================================

@router.get(
    "",
    response_model=list[DocumentResponse],
)
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Permission check
    # --------------------------------------------------------

    if not user_has_permission(
        db,
        current_user.id,
        "document.read",
    ):
        raise HTTPException(
            status_code=403,
            detail="Permission required: document.read",
        )

    # --------------------------------------------------------
    # Get documents
    # --------------------------------------------------------

    documents = (
        db.query(Document)
        .order_by(
            Document.created_at.desc()
        )
        .all()
    )

    return documents


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete(
    "/{document_id}"
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Permission check
    # --------------------------------------------------------

    if not user_has_permission(
        db,
        current_user.id,
        "document.delete",
    ):
        raise HTTPException(
            status_code=403,
            detail="Permission required: document.delete",
        )

    # --------------------------------------------------------
    # Find document
    # --------------------------------------------------------

    document = db.get(
        Document,
        document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    document_name = document.name

    # --------------------------------------------------------
    # Delete chunks + embeddings
    # --------------------------------------------------------

    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).delete(
        synchronize_session=False
    )

    # --------------------------------------------------------
    # Delete physical file
    # --------------------------------------------------------

    if document.file_path:

        file_path = Path(
            document.file_path
        )

        if file_path.exists():
            file_path.unlink()

    # --------------------------------------------------------
    # Delete document
    # --------------------------------------------------------

    db.delete(document)

    # --------------------------------------------------------
    # Audit log
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        actor_user_id=current_user.id,
        action="document.delete",
        resource_type="document",
        resource_id=document_id,
        details=f"Deleted document '{document_name}'",
    )

    db.commit()

    return {
        "success": True,
        "message": (
            f"Document '{document_name}' "
            "deleted successfully"
        ),
        "document_id": document_id,
    }


# ============================================================
# SEARCH DOCUMENTS
# ============================================================

@router.get(
    "/search",
    response_model=SearchResponse,
)
def search_documents(
    query: str,
    top_k: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Permission check
    # --------------------------------------------------------

    if not user_has_permission(
        db,
        current_user.id,
        "document.read",
    ):
        raise HTTPException(
            status_code=403,
            detail="Permission required: document.read",
        )

    # --------------------------------------------------------
    # Search authorized documents
    # --------------------------------------------------------

    results = search_similar_chunks(
        db=db,
        query=query,
        user_id=current_user.id,
        top_k=top_k,
    )

    return {
        "query": query,
        "results": [
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "content": chunk.content,
                "similarity": float(score),
            }
            for chunk, score in results
        ],
    }