from abc import ABC, abstractmethod
from typing import List, Tuple

class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def upsert(self, documents: List[str], ids: List[str], embeddings: List[List[float]]):
        """Add or update documents with their IDs and embeddings."""
        pass

    @abstractmethod
    def query(self, query_embedding: List[float], n_results: int) -> Tuple[List[str], List[float]]:
        """Query the vector store.
        
        Args:
            query_embedding: The embedding of the query.
            n_results: The number of results to return.

        Returns:
            A tuple containing (documents, distances/scores).
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the number of documents in the store."""
        pass

    @abstractmethod
    def reset(self):
        """Clear all data from the store."""
        pass
