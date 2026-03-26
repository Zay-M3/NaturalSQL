from naturalsql.utils.config import AppConfig
from naturalsql.vector.providers.base import EmbeddingProvider
from naturalsql.vector.stores.base import VectorStore

def create_embedding_provider(config: AppConfig) -> EmbeddingProvider:
    """Create an embedding provider based on configuration."""
    if config.embedding_provider == "local":
        from naturalsql.vector.providers.local import LocalSentenceTransformersProvider
        return LocalSentenceTransformersProvider(
            normalize_embeddings=config.db_normalize_embeddings,
            device=config.device
        )
    elif config.embedding_provider == "gemini":
        from naturalsql.vector.providers.gemini import GeminiEmbeddingProvider
        return GeminiEmbeddingProvider(
            api_key=config.gemini_api_key,
            model=config.gemini_embedding_model
        )
    else:
        raise ValueError(f"Unknown embedding provider: {config.embedding_provider}")

def create_vector_store(config: AppConfig, storage_path: str, reset: bool = False) -> VectorStore:
    """Create a vector store based on configuration."""
    if config.vector_backend == "chroma":
        from naturalsql.vector.stores.chroma_store import ChromaVectorStore
        return ChromaVectorStore(storage_path=storage_path, reset_on_start=reset)
    elif config.vector_backend == "sqlite":
        from naturalsql.vector.stores.sqlite_store import SQLiteVectorStore
        return SQLiteVectorStore(storage_path=storage_path, reset_on_start=reset)
    else:
        raise ValueError(f"Unknown vector backend: {config.vector_backend}")
