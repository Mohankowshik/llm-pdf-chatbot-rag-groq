
from sentence_transformers import CrossEncoder
from typing import List, Dict, Any
import os

# Set HF_HUB_DISABLE_XET
os.environ["HF_HUB_DISABLE_XET"] = "1"

_reranker_model = None


def get_reranker_model():
    """Get singleton cross-encoder reranker instance (BAAI/bge-reranker-base for speed and accuracy)."""
    global _reranker_model
    if _reranker_model is None:
        _reranker_model = CrossEncoder('BAAI/bge-reranker-base')
    return _reranker_model


def rerank_chunks(
    query: str,
    chunks: List[Dict[str, Any]],
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Rerank retrieved chunks using a cross-encoder to boost accuracy.
    
    Args:
        query: Original user query
        chunks: List of retrieved chunks with "text" and "metadata"
        top_k: Number of final chunks to keep after reranking
    
    Returns:
        Reranked list of top_k chunks
    """
    if not chunks:
        return []
    
    model = get_reranker_model()
    
    # Prepare pairs for cross-encoder: (query, chunk_text)
    pairs = [(query, chunk["text"]) for chunk in chunks]
    
    # Get scores
    scores = model.predict(pairs)
    
    # Combine chunks with scores and sort
    scored_chunks = []
    for i, chunk in enumerate(chunks):
        scored_chunk = chunk.copy()
        scored_chunk["score"] = float(scores[i])
        scored_chunks.append(scored_chunk)
    
    # Sort in descending order of score
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top_k chunks
    return scored_chunks[:top_k]

