"""
Step 3.3 & 3.4 -- Embeddings (local, free) + ChromaDB vector storage.
"""
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.config import CHROMA_DB_PATH, EMBEDDING_MODEL

_embedder = None
_client = None
_collection = None


def get_embedder():
    global _embedder
    if _embedder is None:
        print(f"Loading local embedding model: {EMBEDDING_MODEL} (first load may take a moment)")
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        _collection = _client.get_or_create_collection(name="documents")
    return _collection


def embed_texts(texts):
    embedder = get_embedder()
    return embedder.encode(texts, show_progress_bar=False).tolist()


def add_chunks(chunks):
    """chunks: list of dicts from chunking.build_chunks_with_metadata"""
    if not chunks:
        return
    collection = get_collection()
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [{
        "document_id": c["document_id"],
        "document_name": c["document_name"],
        "page_number": str(c["page_number"]),
    } for c in chunks]
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)


def query_similar(question: str, top_k: int = 4):
    collection = get_collection()
    query_embedding = embed_texts([question])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    matches = []
    if results and results.get("documents") and results["documents"][0]:
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            matches.append({"text": doc, "metadata": meta, "distance": dist})
    return matches


def delete_document(document_id: str):
    collection = get_collection()
    collection.delete(where={"document_id": document_id})


def count_chunks():
    collection = get_collection()
    return collection.count()
