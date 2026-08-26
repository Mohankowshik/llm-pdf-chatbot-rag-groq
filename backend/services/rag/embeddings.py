
from sentence_transformers import SentenceTransformer
from typing import List
import os

# Set HF_HUB_DISABLE_XET to avoid issues
os.environ["HF_HUB_DISABLE_XET"] = "1"

_embedding_model = None


def get_embedding_model():
    """Get singleton embedding model instance (BAAI/bge-base-en-v1.5 for good speed and accuracy)."""
    global _embedding_model
    if _embedding_model is None:
        # Use bge-base-en-v1.5 for a good balance of speed and accuracy
        _embedding_model = SentenceTransformer('BAAI/bge-base-en-v1.5')
    return _embedding_model


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts with batching."""
    model = get_embedding_model()
    # Batch size of 32 is good for performance on most systems
    return model.encode(texts, show_progress_bar=False, batch_size=32).tolist()


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text."""
    model = get_embedding_model()
    return model.encode(text, show_progress_bar=False).tolist()


def get_query_prefix():
    """Get the required query prefix for bge models (for better retrieval)."""
    return "Represent this question for retrieving supporting documents: "


def get_document_prefix():
    """Get the required document prefix for bge models."""
    return "Represent this document for retrieval: "

