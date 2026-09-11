"""
Lightweight SQLite registry for document metadata and chat history.
(Not the vector store itself -- that's ChromaDB. This just tracks
status/counts/history for the dashboard and chat UI.)
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv("SQLITE_DB_PATH", "./app_data.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            document_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            status TEXT NOT NULL,           -- processing / processed / failed
            chunk_count INTEGER DEFAULT 0,
            uploaded_at TEXT NOT NULL,
            error_message TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            title TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,             -- user / assistant
            content TEXT NOT NULL,
            sources TEXT,                   -- JSON string
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ---------------- Documents ----------------

def insert_document(document_id, filename, file_type, status="processing"):
    conn = get_conn()
    conn.execute(
        "INSERT INTO documents (document_id, filename, file_type, status, uploaded_at) VALUES (?, ?, ?, ?, ?)",
        (document_id, filename, file_type, status, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def update_document_status(document_id, status, chunk_count=None, error_message=None):
    conn = get_conn()
    if chunk_count is not None:
        conn.execute(
            "UPDATE documents SET status=?, chunk_count=?, error_message=? WHERE document_id=?",
            (status, chunk_count, error_message, document_id)
        )
    else:
        conn.execute(
            "UPDATE documents SET status=?, error_message=? WHERE document_id=?",
            (status, error_message, document_id)
        )
    conn.commit()
    conn.close()


def list_documents():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM documents ORDER BY uploaded_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_document(document_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM documents WHERE document_id=?", (document_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_document_record(document_id):
    conn = get_conn()
    conn.execute("DELETE FROM documents WHERE document_id=?", (document_id,))
    conn.commit()
    conn.close()


def get_dashboard_stats():
    conn = get_conn()
    total_docs = conn.execute("SELECT COUNT(*) c FROM documents").fetchone()["c"]
    processed = conn.execute("SELECT COUNT(*) c FROM documents WHERE status='processed'").fetchone()["c"]
    processing = conn.execute("SELECT COUNT(*) c FROM documents WHERE status='processing'").fetchone()["c"]
    failed = conn.execute("SELECT COUNT(*) c FROM documents WHERE status='failed'").fetchone()["c"]
    total_chunks = conn.execute("SELECT COALESCE(SUM(chunk_count),0) c FROM documents WHERE status='processed'").fetchone()["c"]
    total_chats = conn.execute("SELECT COUNT(*) c FROM chat_messages WHERE role='user'").fetchone()["c"]
    conn.close()
    return {
        "total_documents": total_docs,
        "processed": processed,
        "processing": processing,
        "failed": failed,
        "total_indexed_chunks": total_chunks,
        "total_questions": total_chats,
    }


# ---------------- Chat ----------------

def create_session(session_id, title="New Chat"):
    conn = get_conn()
    conn.execute(
        "INSERT INTO chat_sessions (session_id, created_at, title) VALUES (?, ?, ?)",
        (session_id, datetime.utcnow().isoformat(), title)
    )
    conn.commit()
    conn.close()


def list_sessions():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM chat_sessions ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_message(session_id, role, content, sources=None):
    import json
    conn = get_conn()
    conn.execute(
        "INSERT INTO chat_messages (session_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?)",
        (session_id, role, content, json.dumps(sources or []), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_messages(session_id):
    import json
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM chat_messages WHERE session_id=? ORDER BY id ASC", (session_id,)
    ).fetchall()
    conn.close()
    messages = []
    for r in rows:
        d = dict(r)
        d["sources"] = json.loads(d["sources"]) if d["sources"] else []
        messages.append(d)
    return messages
