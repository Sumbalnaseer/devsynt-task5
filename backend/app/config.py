"""
Central configuration. All secrets/config come from environment
variables (loaded from .env) -- never hardcoded.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_store")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploaded_documents")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "6"))

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY is not set. Chat generation will fail until it is configured in .env")
