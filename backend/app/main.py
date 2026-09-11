"""
FastAPI backend entrypoint -- Task 5.
Endpoints: document upload/list/delete/reprocess, chat sessions/messages,
dashboard stats.
"""
import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import UPLOAD_DIR
from app import database as db
from app.processing import process_document, reprocess_document
from app.rag import answer_question

app = FastAPI(title="Harborview RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.on_event("startup")
def startup():
    db.init_db()


# ---------------- Dashboard ----------------

@app.get("/api/dashboard/stats")
def dashboard_stats():
    return db.get_dashboard_stats()


# ---------------- Documents ----------------

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


@app.post("/api/documents/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: .{ext}. Allowed: pdf, docx, txt")

    document_id = str(uuid.uuid4())
    saved_path = os.path.join(UPLOAD_DIR, f"{document_id}_{file.filename}")
    with open(saved_path, "wb") as f:
        f.write(await file.read())

    db.insert_document(document_id, file.filename, ext, status="processing")
    background_tasks.add_task(process_document, document_id, saved_path, file.filename, ext)

    return {"document_id": document_id, "filename": file.filename, "status": "processing"}


@app.get("/api/documents")
def list_documents():
    return db.list_documents()


@app.get("/api/documents/{document_id}")
def get_document(document_id: str):
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.delete("/api/documents/{document_id}")
def delete_document(document_id: str):
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    from app.vector_store import delete_document as vs_delete
    vs_delete(document_id)
    db.delete_document_record(document_id)
    # best-effort remove the stored file
    for fname in os.listdir(UPLOAD_DIR):
        if fname.startswith(document_id):
            try:
                os.remove(os.path.join(UPLOAD_DIR, fname))
            except OSError:
                pass
    return {"status": "deleted", "document_id": document_id}


@app.post("/api/documents/{document_id}/reprocess")
def reprocess(document_id: str, background_tasks: BackgroundTasks):
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    file_path = None
    for fname in os.listdir(UPLOAD_DIR):
        if fname.startswith(document_id):
            file_path = os.path.join(UPLOAD_DIR, fname)
            break
    if not file_path:
        raise HTTPException(status_code=404, detail="Original file not found on disk")
    background_tasks.add_task(reprocess_document, document_id, file_path, doc["filename"], doc["file_type"])
    return {"status": "reprocessing", "document_id": document_id}


# ---------------- Chat ----------------

class NewSessionRequest(BaseModel):
    title: str = "New Chat"


class MessageRequest(BaseModel):
    session_id: str
    question: str


@app.post("/api/chat/sessions")
def new_session(req: NewSessionRequest):
    session_id = str(uuid.uuid4())
    db.create_session(session_id, req.title)
    return {"session_id": session_id, "title": req.title}


@app.get("/api/chat/sessions")
def get_sessions():
    return db.list_sessions()


@app.get("/api/chat/sessions/{session_id}/messages")
def get_messages(session_id: str):
    return db.get_messages(session_id)


@app.post("/api/chat/message")
def send_message(req: MessageRequest):
    try:
        db.add_message(req.session_id, "user", req.question)
        result = answer_question(req.question)
        db.add_message(req.session_id, "assistant", result["answer"], result["sources"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@app.get("/")
def root():
    return {"status": "ok", "service": "Harborview RAG Chatbot API"}
