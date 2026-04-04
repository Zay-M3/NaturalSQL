import chromadb
from typing import Any, List, Tuple
from naturalsql.vector.stores.base import VectorStore

class ChromaVectorStore(VectorStore):
    """Vector store using ChromaDB."""

    def __init__(self, storage_path: str, collection_name: str = "db_schema", reset_on_start: bool = False):
        self.client = chromadb.PersistentClient(path=storage_path)
        self.collection_name = collection_name
        
        if reset_on_start:
            self.reset()
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=None  # We provide embeddings manually
        )
        
    def upsert(
        self,
        documents: List[str],
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict[str, Any]] | None = None,
    ):
        """Add or update documents with IDs, embeddings, and optional metadata."""
        payload = {
            "documents": documents,
            "ids": ids,
            "embeddings": embeddings,
        }
        if metadatas is not None:
            payload["metadatas"] = metadatas

        self.collection.upsert(**payload)

    def query(
        self,
        query_embedding: List[float],
        n_results: int,
        kind: str | None = None,
    ) -> Tuple[List[str], List[float]]:
        """Query the vector store using an embedding and optional kind filter."""
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
        }
        if kind:
            kwargs["where"] = {"kind": kind}

        results = self.collection.query(**kwargs)
        # Return first result batch as we query one vector at a time
        return results['documents'][0], results['distances'][0]

    def count(self) -> int:
        """Return the number of documents in the collection."""
        return self.collection.count()

    def reset(self):
        """Delete and recreate the collection."""
        try:
            self.client.delete_collection(self.collection_name)
        except ValueError:
            pass
        except Exception:
            pass
        # Recreate immediately to be ready for use
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=None
        )
