Enterprise AI Assistant
An AI-powered enterprise application designed to provide intelligent access to company documents, code, and organizational knowledge using RAG, LLM-based intent classification, role-based access control, permission management, and audit logging.
🚀 Features
- 🤖 AI Chat Assistant — Ask questions using natural language.
- 📚 Document Intelligence — Upload and retrieve information from enterprise documents.
- 🔎 RAG-Based Knowledge Retrieval — Retrieve relevant information before generating responses.
- 🧠 LLM Intent Classification — Understand user queries based on their meaning rather than fixed keywords.
- 💻 Code Intelligence — Support for enterprise codebase knowledge and analysis.
- 👥 User Management — Create and manage enterprise users.
- 🛡️ Role-Based Access Control (RBAC) — Manage roles and user permissions.
- 🔐 Permission Management — Separate system permissions from custom permissions.
- 📄 Document Access Control — Control document access for users and roles.
- 📋 Audit Logging — Track important security and permission-related actions.
- 🔒 Backend Security Boundary — Authorization is enforced on the backend.
- 🗃️ Database Migrations — Managed using Alembic.
- ⚡ FastAPI Backend — REST API architecture.
- ⚛️ React Frontend — Modern web-based user interface.
  
🏗️ Architecture
                    ┌──────────────────────┐
                    │      React UI        │
                    │      Frontend        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI API      │
                    │       Backend        │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
       │ Auth & RBAC │  │ Intent       │  │ Audit Logs   │
       │ Permissions │  │ Classifier   │  │              │
       └─────────────┘  └──────┬───────┘  └──────────────┘
                               │
                               ▼
                       ┌───────────────┐
                       │ RAG Pipeline  │
                       ├───────────────┤
                       │ Chunking      │
                       │ Embeddings    │
                       │ Retrieval     │
                       │ LLM           │
                       └───────┬───────┘
                               │
                               ▼
                       ┌───────────────┐
                       │ PostgreSQL DB │
                       └───────────────┘

🧠 AI Query Flow
User Question
      ↓
LLM Intent Classification
      ↓
Structured Intent + Entities
      ↓
Authentication
      ↓
Permission / Security Check
      ↓
Application Service
      ↓
RAG / Database / Business Logic
      ↓
LLM Response Generation
      ↓
Natural Language Response

The application uses an LLM to understand the meaning of a user's question and convert it into a structured intent instead of depending only on hard-coded keywords.
📚 RAG Pipeline
Document
   ↓
Text Extraction
   ↓
Chunking
   ↓
Embedding Generation
   ↓
Vector Storage
   ↓
Similarity Retrieval
   ↓
Relevant Context
   ↓
LLM
   ↓
Answer

The RAG pipeline allows the assistant to answer questions using enterprise-specific knowledge rather than relying only on the LLM's general knowledge.
🔐 Security & Permissions
The application follows a backend-first security model.
System Permissions
System permissions are protected from accidental modification or deletion.
Custom Permissions
Custom permissions can be created and managed through the application.
Backend Security
The frontend controls the user interface, but the backend remains the actual security boundary. API authorization is enforced independently of frontend visibility.
Audit Logging
Important operations such as permission and access changes are recorded in audit logs.
🛠️ Technology Stack
Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Alembic
- Uvicorn
AI / RAG
- LLM-based intent classification
- Retrieval-Augmented Generation (RAG)
- Text chunking
- Embeddings
- Semantic retrieval
Frontend
- React
- Vite
- JavaScript
- CSS
Database
- PostgreSQL
📁 Project Structure
Enterprise-AI-Assistant/
│
├── backend/
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   └── alembic.ini
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   └── pages/
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── package.json
└── package-lock.json

⚙️ Backend Setup
Navigate to the backend:
cd backend

Create a virtual environment:
python -m venv venv

Activate it on Windows:
venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Create a .env file and configure the required database and LLM environment variables.
Run database migrations:
alembic upgrade head

Start the backend:
python -m uvicorn app.main:app --reload

Backend:
http://127.0.0.1:8000

API documentation:
http://127.0.0.1:8000/docs

⚛️ Frontend Setup
Navigate to the frontend:
cd frontend

Install dependencies:
npm install

Start the development server:
npm run dev

Frontend:
http://localhost:5173

🔑 Environment Variables
Create a .env file inside the backend directory.
Example:
DATABASE_URL=your_database_connection_string
GROQ_API_KEY=your_llm_api_key

Never commit .env files or API keys to GitHub.
🗄️ Database Migrations
Alembic is used for database schema management.
Create a migration:
alembic revision --autogenerate -m "migration message"

Apply migrations:
alembic upgrade head

🔒 Security Principles
This project follows several security principles:
- Authentication before protected operations
- Backend-enforced authorization
- Role-based permissions
- Protected system permissions
- Controlled document access
- Audit logging
- Environment-based secrets
- Separation between frontend UI controls and backend authorization
📌 Current Status
Project Status: Completed
The current implementation includes:
- Authentication
- Users
- Roles
- Permissions
- Document management
- Document access control
- RAG pipeline
- LLM intent classification
- AI chat
- Code intelligence foundation
- Audit logging
- PostgreSQL database
- Alembic migrations
- React frontend
- FastAPI backend
🚀 Future Enhancements
- Advanced codebase indexing
- Multi-document conversational RAG
- Improved vector database integration
- Enterprise SSO integration
- Advanced analytics dashboard
- Fine-grained document permissions
- Production deployment
- Monitoring and observability
- Automated evaluation of RAG responses
👨‍💻 Author
PRAGATHEESH A
