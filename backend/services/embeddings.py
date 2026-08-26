from sentence_transformers import SentenceTransformer

_model = None


def get_model():
    global _model
    if _model is None:
        import os
        os.environ["HF_HUB_DISABLE_XET"] = "1"
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def generate_embeddings(texts: list):
    """Generate embeddings for a list of texts."""
    return get_model().encode(texts, show_progress_bar=False)


def generate_embedding(text: str):
    """Generate embedding for a single text."""
    return get_model().encode(text, show_progress_bar=False)
