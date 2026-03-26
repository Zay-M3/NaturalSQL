from typing import List
from naturalsql.vector.providers.base import EmbeddingProvider

class LocalSentenceTransformersProvider(EmbeddingProvider):
    """Local embedding provider using sentence-transformers."""

    def __init__(self, normalize_embeddings: bool = True, device: str = "cpu"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "Could not import sentence_transformers. Please install it with `pip install sentence-transformers`."
            )
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
        self.normalize_embeddings = normalize_embeddings

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = self.model.encode(documents, normalize_embeddings=self.normalize_embeddings)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string."""
        embedding = self.model.encode(query, normalize_embeddings=self.normalize_embeddings)
        return embedding.tolist()
