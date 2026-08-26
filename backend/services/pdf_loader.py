import fitz  # PyMuPDF
from typing import List, Tuple
import os


def load_pdf(file_path: str) -> List[Tuple[str, int]]:
    """Load a PDF file and extract text with page numbers."""
    if not file_path.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF")
    doc = fitz.open(file_path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages.append((text, page_num + 1))  # page numbers start at 1
    return pages
