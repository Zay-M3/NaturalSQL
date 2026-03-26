from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        pass
    
    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string."""
        pass
