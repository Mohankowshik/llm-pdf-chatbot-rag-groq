
import uuid
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
try:
    from backend.config import settings
except ImportError:
    from config import settings


def create_chunks(cleaned_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create chunks from cleaned document with metadata."""
    chunk_size = settings.CHUNK_SIZE
    chunk_overlap = settings.CHUNK_OVERLAP
    filename = cleaned_doc["filename"]
    
    # Group elements by page number
    pages_grouped = {}
    for elem in cleaned_doc["pages"]:
        page_num = elem["page"]
        if page_num not in pages_grouped:
            pages_grouped[page_num] = []
        pages_grouped[page_num].append(elem)
    
    final_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    # Process each page
    for page_num, elements in sorted(pages_grouped.items()):
        # Combine all elements on the page into a single text
        page_text_parts = []
        current_heading = "No Heading"
        
        for elem in elements:
            if elem["type"] == "heading":
                current_heading = elem["content"]
            page_text_parts.append(elem["content"])
        
        page_text = "\n".join(page_text_parts)
        
        # Split into chunks
        if page_text.strip():
            splits = text_splitter.split_text(page_text)
            
            for split in splits:
                if split.strip():
                    chunk_id = str(uuid.uuid4())
                    final_chunks.append({
                        "id": chunk_id,
                        "text": split.strip(),
                        "metadata": {
                            "filename": filename,
                            "page": page_num,
                            "section_heading": current_heading,
                            "chunk_id": chunk_id
                        }
                    })
    
    return final_chunks

