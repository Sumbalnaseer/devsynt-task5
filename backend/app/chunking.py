"""
Step 3.2 -- Chunking with metadata.
Each chunk carries: document_id, document_name, page_number, chunk_id.
"""
import uuid


def chunk_text(text: str, chunk_size: int, overlap: int):
    """Simple sliding-window character chunker with overlap."""
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def build_chunks_with_metadata(pages, document_id: str, document_name: str,
                                 chunk_size: int, overlap: int):
    """
    pages: list of (page_number_or_None, text)
    Returns list of dicts: {chunk_id, text, document_id, document_name, page_number}
    """
    all_chunks = []
    for page_number, page_text in pages:
        text_chunks = chunk_text(page_text, chunk_size, overlap)
        for chunk in text_chunks:
            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "text": chunk,
                "document_id": document_id,
                "document_name": document_name,
                "page_number": page_number if page_number is not None else "N/A",
            })
    return all_chunks
