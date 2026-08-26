
import re
from typing import List, Dict, Any


def clean_text(text: str) -> str:
    """Clean and normalize text: normalize whitespace, remove extra lines, etc."""
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Normalize whitespace (replace tabs, multiple spaces with single space)
    text = re.sub(r'[ \t]+', ' ', text)
    # Trim leading/trailing whitespace per line
    lines = [line.strip() for line in text.splitlines()]
    # Remove empty lines
    lines = [line for line in lines if line]
    return '\n'.join(lines)


def clean_document(doc_data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean entire document by applying all cleaning steps."""
    cleaned_elements = []
    for elem in doc_data["pages"]:
        cleaned_elem = elem.copy()
        cleaned_elem["content"] = clean_text(elem["content"])
        cleaned_elements.append(cleaned_elem)
    
    return {
        "filename": doc_data["filename"],
        "total_pages": doc_data["total_pages"],
        "pages": cleaned_elements
    }

