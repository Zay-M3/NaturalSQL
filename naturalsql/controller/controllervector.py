import os
from typing import Any

from naturalsql.utils.config import AppConfig
from naturalsql.vector.factory import create_embedding_provider, create_vector_store

class VectorManager:

    @staticmethod
    def collection_exists(storage_path: str) -> int:
        """Check if an indexed collection exists (Chroma or SQLite)."""
        # Check Chroma
        try:
            import chromadb
            if os.path.isdir(storage_path):
                # Only check if chroma specific files exist to avoid creating empty db
                if os.path.exists(os.path.join(storage_path, "chroma.sqlite3")):
                    client = chromadb.PersistentClient(path=storage_path)
                    try:
                        collection = client.get_collection("db_schema")
                        count = collection.count()
                        if count > 0: return count
                    except:
                        pass
        except Exception:
            pass
            
        # Check SQLite
        try:
            import sqlite3
            db_path = os.path.join(storage_path, "vectors.db")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT COUNT(*) FROM vectors")
                    count = cursor.fetchone()[0]
                    if count > 0: return count
                except:
                    pass
                finally:
                    conn.close()
        except Exception:
            pass
            
        return 0
        
    def __init__(self, storage_path="./metadata_vdb", force_reset=False, config: AppConfig | None = None):
        if config is None:
            raise ValueError("VectorManager requiere una instancia de AppConfig en config.")
        self.config = config
        
        # Initialize provider and store via factory
        self.provider = create_embedding_provider(config)
        self.store = create_vector_store(config, storage_path, reset=force_reset)

    def index_documents(self, documents_payload: list[dict[str, Any]]):
        """Indexa documentos estructurados (tablas y relaciones) en la base vectorial.

        Args:
            documents_payload: Lista de documentos con llaves:
                - id: Identificador unico del documento.
                - content: Texto para embedding.
                - metadata: Metadatos del documento (incluye kind).
        """
        if not documents_payload:
            return

        documents = [item["content"] for item in documents_payload]
        ids = [item["id"] for item in documents_payload]
        metadatas = [item.get("metadata", {}) for item in documents_payload]

        embeddings = self.provider.embed_documents(documents)
        self.store.upsert(
            documents=documents,
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def index_tables(self, tables_list):
        """Wrapper de compatibilidad para indexacion antigua de solo tablas."""
        payload = [
            {
                "id": f"table::{idx}",
                "content": table_text,
                "metadata": {"kind": "table"},
            }
            for idx, table_text in enumerate(tables_list)
        ]
        self.index_documents(payload)

    def search_relevant_tables(self, request, limit=3):
        """Busca las tablas relevantes para una solicitud dada, utilizando el indice vectorial.

        Args:
            request: Pregunta o solicitud en lenguaje natural.
            limit: Numero maximo de resultados a retornar.

        Returns:
            list: Lista de descripciones de tablas relevantes (filtradas por distancia <= threshold configurado).
        """
        query = request
        query_embedding = self.provider.embed_query(query)
        
        table_docs, table_distances = self.store.query(query_embedding, limit, kind="table")
        rel_docs, rel_distances = self.store.query(query_embedding, max(1, limit), kind="relationship")

        merged = list(zip(table_docs, table_distances)) + list(zip(rel_docs, rel_distances))
        merged.sort(key=lambda item: item[1])

        final_tables = []
        threshold = self.config.vector_distance_threshold
        for doc, dist in merged:
            if dist <= threshold:
                final_tables.append(doc)
                if len(final_tables) >= limit:
                    break

        return final_tables
