import numpy as np


class VectorStore:
    """Simple in-memory vector store using cosine similarity."""

    def __init__(self):
        self.chunks = []
        self.embeddings = None

    def add_documents(self, chunks: list[dict], embeddings):
        """Store document chunks and their embeddings."""

        vectors = np.asarray(embeddings, dtype=np.float32)

        if vectors.ndim != 2:
            raise ValueError("Embeddings must be a 2D array")

        if len(chunks) != len(vectors):
            raise ValueError("Number of chunks and embeddings must match")

        self.chunks = chunks
        self.embeddings = vectors

    def search(self, query_embedding, top_k: int = 3) -> list[dict]:
        """Find the most similar chunks."""

        if self.embeddings is None:
            raise ValueError("Vector store is empty")

        if top_k <= 0:
            raise ValueError("top_k must be positive")

        query = np.asarray(query_embedding, dtype=np.float32).reshape(-1)

        if query.shape[0] != self.embeddings.shape[1]:
            raise ValueError("Query embedding dimension mismatch")

        # Cosine similarity
        dot_products = self.embeddings @ query
        document_norms = np.linalg.norm(self.embeddings, axis=1)
        query_norm = np.linalg.norm(query)

        similarities = dot_products / (
            np.maximum(document_norms * query_norm, 1e-12)
        )

        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [
            {
                **self.chunks[index],
                "score": float(similarities[index]),
            }
            for index in top_indices
        ]
