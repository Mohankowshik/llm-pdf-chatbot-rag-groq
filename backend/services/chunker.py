from typing import List, Dict, Any
try:
    from backend.config import settings
except ImportError:
    from config import settings



def create_chunks(pages: List[tuple], filename: str) -> List[Dict[str, Any]]:
    """Split text into chunks with metadata."""
    chunks = []
    chunk_size = settings.CHUNK_SIZE
    chunk_overlap = settings.CHUNK_OVERLAP
    current_chunk = ""
    current_page = 1

    for text, page_num in pages:
        words = text.split()
        for word in words:
            if len(current_chunk.split()) >= chunk_size:
                # Save chunk
                chunks.append({
                    "text": current_chunk.strip(),
                    "metadata": {
                        "filename": filename,
                        "page": current_page
                    }
                })
                # Keep overlap
                words_in_chunk = current_chunk.split()
                overlap = " ".join(words_in_chunk[-chunk_overlap:])
                current_chunk = overlap + " " + word
                current_page = page_num
            else:
                current_chunk += " " + word
                current_page = page_num

    # Add last chunk
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "metadata": {
                "filename": filename,
                "page": current_page
            }
        })

    return chunks
