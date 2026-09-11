"""
Orchestrates the full document-side pipeline:
extract -> chunk -> embed -> store, updating the SQLite status registry
as it goes so the dashboard reflects real progress.
"""
import os
from app.text_extraction import extract_text
from app.chunking import build_chunks_with_metadata
from app.vector_store import add_chunks, delete_document as vs_delete_document
from app.database import update_document_status
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def process_document(document_id: str, file_path: str, filename: str, file_ext: str):
    try:
        pages = extract_text(file_path, file_ext)
        chunks = build_chunks_with_metadata(
            pages, document_id, filename, CHUNK_SIZE, CHUNK_OVERLAP
        )
        if not chunks:
            update_document_status(document_id, "failed", error_message="No extractable text found in document")
            return
        add_chunks(chunks)
        update_document_status(document_id, "processed", chunk_count=len(chunks))
    except Exception as e:
        update_document_status(document_id, "failed", error_message=str(e))


def reprocess_document(document_id: str, file_path: str, filename: str, file_ext: str):
    # Remove old chunks for this doc first, then reprocess cleanly
    vs_delete_document(document_id)
    update_document_status(document_id, "processing")
    process_document(document_id, file_path, filename, file_ext)
