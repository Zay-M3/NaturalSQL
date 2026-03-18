import os

import chromadb
from chromadb.utils import embedding_functions
from naturalsql.utils.config import AppConfig


class VectorManager:

    @staticmethod
    def collection_exists(storage_path: str) -> int:
        """Verifica si ya existe una coleccion indexada sin cargar el modelo de embeddings.

        Solo abre el PersistentClient de ChromaDB y cuenta los documentos existentes.
        No inicializa SentenceTransformer.

        Args:
            storage_path: Ruta donde se almacena la base vectorial.

        Returns:
            int: Cantidad de documentos indexados, 0 si no existe la coleccion.
        """
        if not os.path.isdir(storage_path):
            return 0
        try:
            client = chromadb.PersistentClient(path=storage_path)
            collection = client.get_collection("db_schema")
            return collection.count()
        except Exception:
            return 0
        
    def __init__(self, storage_path="./metadata_vdb", force_reset=False, config: AppConfig | None = None):
        if config is None:
            raise ValueError("VectorManager requiere una instancia de AppConfig en config.")
        self.config = config
        self.client = chromadb.PersistentClient(path=storage_path)

        if force_reset:
            try:
                self.client.delete_collection("db_schema")
            except ValueError:
                pass
            except Exception:
                pass

        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2",
            normalize_embeddings=self.config.db_normalize_embeddings,
            device=self.config.device,
        )
        self.collection = self.client.get_or_create_collection(
            name="db_schema",
            embedding_function=self.ef,
        )

    def index_tables(self, tables_list):
        """Indexa la lista de tablas en la base de datos vectorial.

        Args:
            tables_list: Lista de strings con las descripciones de tablas formateadas.
        """
        self.collection.upsert(
            documents=tables_list,
            ids=[f"table::{table_name}" for table_name in tables_list],
        )

    def search_relevant_tables(self, request, limit=3):
        """Busca las tablas relevantes para una solicitud dada, utilizando el indice vectorial.

        Args:
            request: Pregunta o solicitud en lenguaje natural.
            limit: Numero maximo de resultados a retornar.

        Returns:
            list: Lista de descripciones de tablas relevantes (filtradas por distancia <= 0.8).
        """
        query = f"{request}. tablas sql relacionadas"
        results = self.collection.query(query_texts=[query], n_results=limit)

        final_tables = []
        for doc, dist in zip(results["documents"][0], results["distances"][0]):
            if dist <= 0.8:
                final_tables.append(doc)

        return final_tables
