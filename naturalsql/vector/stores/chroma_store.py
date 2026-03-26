import chromadb
from typing import List, Tuple
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
        
    def upsert(self, documents: List[str], ids: List[str], embeddings: List[List[float]]):
        """Add or update documents with their IDs and embeddings."""
        self.collection.upsert(
            documents=documents,
            ids=ids,
            embeddings=embeddings
        )

    def query(self, query_embedding: List[float], n_results: int) -> Tuple[List[str], List[float]]:
        """Query the vector store using an embedding."""
        results = self.collection.query(
            #query_texts=[query],  # this is the last version of naturalsql
            query_embeddings=[query_embedding],
            n_results=n_results
        )
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
