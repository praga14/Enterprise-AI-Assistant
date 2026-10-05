from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.users import router as users_router
from app.api.roles import router as roles_router
from app.api.permissions import router as permissions_router
from app.api.user_roles import router as user_roles_router
from app.api.role_permissions import router as role_permissions_router
from app.api.auth import router as auth_router
from app.api.audit_logs import router as audit_logs_router
from app.api.documents import router as documents_router
from app.api.rag import router as rag_router
from app.api.document_access import router as document_access_router
from app.api.access_query import router as access_query_router
from app.api.access_intelligence import router as access_intelligence_router
from app.api.user_document_access import router as user_document_access_router
from app.api.document_access_management import router as document_access_management_router
from app.api.chat import router as chat_router
from app.api.dashboard import router as dashboard_router

app = FastAPI(
    title="Enterprise AI Application Intelligence & Engineering Assistant",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(user_roles_router)
app.include_router(role_permissions_router)
app.include_router(auth_router)
app.include_router(audit_logs_router)
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(document_access_router)
app.include_router(access_query_router)
app.include_router(access_intelligence_router)
app.include_router(user_document_access_router)
app.include_router(document_access_management_router)
app.include_router(chat_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {
        "message": "Enterprise AI Assistant API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
