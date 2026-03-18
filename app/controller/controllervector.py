import chromadb
from chromadb.utils import embedding_functions
from app.utils.config import AppConfig

class VectorManager:
    def __init__(self, storage_path="./metadata_vdb", force_reset=False):
        self.config = AppConfig.from_env()
        self.client = chromadb.PersistentClient(path=storage_path)
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2",
          normalize_embeddings=self.config.db_normalize_embeddings,
          device=self.config.device
          )
        self.collection = self.client.get_or_create_collection("db_schema", embedding_function=self.ef)
        
        if force_reset:
            try:
                self.client.delete_collection("db_schema")
                print("--- [INFO] Base de datos de vectores limpiada correctamente ---")
            except:
                pass
        
        self.collection = self.client.get_or_create_collection(
            name="db_schema", 
            embedding_function=self.ef
        )

    def index_tables(self, tables_list):
        """Indexa la lista de tablas en la base de datos, esto permite que la IA pueda buscar las tablas relevantes para una consulta dada, mejorando la capacidad de generar consultas SQL correctas."""
        self.collection.add(
            documents=tables_list,
            ids=[f"t_{i}" for i in range(len(tables_list))]
        )
        

    def search_relevant_tables(self, request, limit=3):
        """Busca las tablas relevantes para una solicitud dada, utilizando el índice vectorial."""
        query = f"{request}. tablas sql relacionadas"
        results = self.collection.query(query_texts=[query], n_results=limit)
        
        final_tables = []
        for doc, dist in zip(results['documents'][0], results['distances'][0]):
            if dist <= 0.8:
                final_tables.append(doc)
                
        return final_tables
    