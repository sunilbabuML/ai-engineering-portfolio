from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load and cache the embedding model."""
    return SentenceTransformer(MODEL_NAME)


def generate_embeddings(chunks: list[dict]):
    """Generate normalized embeddings for document chunks."""

    if not chunks:
        return []

    model = get_embedding_model()

    texts = [chunk["content"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return embeddings
