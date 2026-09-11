"""
Step 3.1 -- Text extraction for PDF / DOCX / TXT.
Returns a list of (page_number, text) tuples so page-level metadata
can be preserved through to the chunking stage.
"""
from pypdf import PdfReader
import docx


def extract_pdf(file_path: str):
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append((i, text))
    return pages


def extract_docx(file_path: str):
    doc = docx.Document(file_path)
    full_text = "\n".join(p.text for p in doc.paragraphs)
    # DOCX has no native page concept -- treat as a single logical "page"
    return [(None, full_text)]


def extract_txt(file_path: str):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return [(None, f.read())]


def extract_text(file_path: str, file_ext: str):
    """
    file_ext should be one of: 'pdf', 'docx', 'txt'
    Returns list of (page_number_or_None, text)
    """
    file_ext = file_ext.lower().lstrip(".")
    if file_ext == "pdf":
        return extract_pdf(file_path)
    elif file_ext == "docx":
        return extract_docx(file_path)
    elif file_ext == "txt":
        return extract_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
