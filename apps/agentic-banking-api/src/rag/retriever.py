from pathlib import Path

from src.rag.document_loader import load_documents
from src.rag.chunker import chunk_documents
from src.rag.embeddings import get_embedding_model, generate_embeddings
from src.rag.vector_store import VectorStore


class BankingPolicyRetriever:
    """Retrieve relevant banking policies using semantic search."""

    def __init__(self, knowledge_base_path: str | Path):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.vector_store = VectorStore()
        self.is_initialized = False

    def initialize(self):
        """Load, chunk, and embed all banking policies."""

        documents = load_documents(self.knowledge_base_path)

        if not documents:
            raise ValueError("No banking policy documents found")

        chunks = chunk_documents(documents)
        embeddings = generate_embeddings(chunks)

        self.vector_store.add_documents(chunks, embeddings)
        self.is_initialized = True

        return {
            "documents": len(documents),
            "chunks": len(chunks),
        }

    def retrieve(self, question: str, top_k: int = 3):
        """Return the most relevant policy chunks."""

        if not self.is_initialized:
            raise RuntimeError("Retriever has not been initialized")

        if not question.strip():
            raise ValueError("Question cannot be empty")

        model = get_embedding_model()

        query_embedding = model.encode(
            question,
            normalize_embeddings=True,
        )

        return self.vector_store.search(query_embedding, top_k=top_k)
