
import uuid
from typing import List, Dict, Any, Callable
try:
    from backend.config import settings
except ImportError:
    from config import settings


class RecursiveCharacterTextSplitter:
    """
    Custom implementation of recursive character-level text splitting.
    Splits text using a hierarchy of separators, keeping chunks under chunk_size
    while preserving overlap between consecutive chunks.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        length_function: Callable[[str], int] = len,
        separators: List[str] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separators in priority order."""
        chunks = []
        separator = separators[-1]
        new_separators = []

        for i, s in enumerate(separators):
            if s == "":
                separator = s
                break
            if s in text:
                separator = s
                new_separators = separators[i + 1:]
                break

        splits = text.split(separator) if separator else list(text)
        good_splits = []

        for s in splits:
            if self.length_function(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, separator)
                    chunks.extend(merged)
                    good_splits = []
                if not new_separators:
                    chunks.append(s)
                else:
                    other_info = self._split_text(s, new_separators)
                    chunks.extend(other_info)

        if good_splits:
            merged = self._merge_splits(good_splits, separator)
            chunks.extend(merged)

        return chunks

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """Merge smaller splits into chunks of up to chunk_size with overlap."""
        docs = []
        current_doc = []
        current_length = 0
        total = 0

        for split in splits:
            split_length = self.length_function(split)
            total += split_length + (len(separator) if current_doc else 0)

            if total > self.chunk_size:
                if current_doc:
                    doc = separator.join(current_doc).strip()
                    if doc:
                        docs.append(doc)

                    # Keep overlap from end of current chunk
                    overlap_chunks = []
                    overlap_length = 0
                    for chunk in reversed(current_doc):
                        chunk_len = self.length_function(chunk) + (len(separator) if overlap_chunks else 0)
                        if overlap_length + chunk_len > self.chunk_overlap:
                            break
                        overlap_chunks.insert(0, chunk)
                        overlap_length += chunk_len
                    current_doc = overlap_chunks
                    current_length = overlap_length
                    total = current_length + split_length + (len(separator) if current_doc else 0)

                    # If adding this split still exceeds, keep looping
                    while total > self.chunk_size and len(current_doc) > 1:
                        removed = current_doc.pop(0)
                        current_length -= self.length_function(removed) + (len(separator) if current_doc else 0)
                        total = current_length + split_length + (len(separator) if current_doc else 0)

                    if total > self.chunk_size and not current_doc:
                        # Single piece too big, add it as-is
                        if split.strip():
                            docs.append(split.strip())
                        total = 0
                        continue

            current_doc.append(split)
            current_length = total

        if current_doc:
            doc = separator.join(current_doc).strip()
            if doc:
                docs.append(doc)

        return docs

    def split_text(self, text: str) -> List[str]:
        """Split text into chunks using recursive separator-based splitting."""
        return self._split_text(text, self.separators)


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

