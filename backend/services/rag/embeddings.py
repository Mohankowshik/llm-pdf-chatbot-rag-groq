
from sentence_transformers import SentenceTransformer
from typing import List
import os

# Set HF_HUB_DISABLE_XET to avoid issues
os.environ["HF_HUB_DISABLE_XET"] = "1"

_embedding_model = None


def get_embedding_model():
    """Get singleton embedding model instance (all-MiniLM-L6-v2 for ultra-fast CPU inference and low latency)."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts with batching."""
    model = get_embedding_model()
    return model.encode(texts, show_progress_bar=False, batch_size=64).tolist()


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text."""
    model = get_embedding_model()
    return model.encode(text, show_progress_bar=False).tolist()


def get_query_prefix():
    """Prefix for queries (empty for all-MiniLM-L6-v2)."""
    return ""


def get_document_prefix():
    """Prefix for documents (empty for all-MiniLM-L6-v2)."""
    return ""


