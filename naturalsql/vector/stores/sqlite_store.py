import sqlite3
import json
import os
import math
from typing import List, Tuple
from naturalsql.vector.stores.base import VectorStore

class SQLiteVectorStore(VectorStore):
    """Vector store using SQLite with a pure Python fallback for similarity search."""

    def __init__(self, storage_path: str, table_name: str = "vectors", reset_on_start: bool = False):
        # Ensure storage directory exists if it's a directory path
        if not os.path.exists(storage_path):
             os.makedirs(storage_path, exist_ok=True)
             
        db_path = os.path.join(storage_path, "vectors.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.table_name = table_name

        if reset_on_start:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.conn.commit()

        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id TEXT PRIMARY KEY,
                content TEXT,
                embedding TEXT
            )
        """)
        self.conn.commit()

    def upsert(self, documents: List[str], ids: List[str], embeddings: List[List[float]]):
        """Add or update documents."""
        for doc, id, emb in zip(documents, ids, embeddings):
            emb_json = json.dumps(emb)
            self.cursor.execute(f"""
                INSERT OR REPLACE INTO {self.table_name} (id, content, embedding)
                VALUES (?, ?, ?)
            """, (id, doc, emb_json))
        self.conn.commit()

    def query(self, query_embedding: List[float], n_results: int) -> Tuple[List[str], List[float]]:
        """Query using cosine distance (1 - similarity)."""
        self.cursor.execute(f"SELECT content, embedding FROM {self.table_name}")
        rows = self.cursor.fetchall()
        
        if not rows:
            return [], []

        # Simple Python implementation to avoid hard numpy dependency if possible,
        # but for vector ops, numpy is standard. Assuming numpy is present via chromadb/pandas.
        try:
            import numpy as np
            use_numpy = True
        except ImportError:
            use_numpy = False

        results = []
        if use_numpy:
            query_vec = np.array(query_embedding)
            norm_query = np.linalg.norm(query_vec)
            
            for content, emb_json in rows:
                vec = np.array(json.loads(emb_json))
                norm_vec = np.linalg.norm(vec)
                
                if norm_query == 0 or norm_vec == 0:
                    similarity = 0.0
                else:
                    similarity = np.dot(query_vec, vec) / (norm_query * norm_vec)
                
                distance = 1 - similarity
                results.append((content, distance))
        else:
            # Pure Python fallback
            def dot(v1, v2):
                return sum(x*y for x, y in zip(v1, v2))
            def norm(v):
                return math.sqrt(sum(x*x for x in v))
            
            norm_query = norm(query_embedding)
            for content, emb_json in rows:
                vec = json.loads(emb_json)
                norm_vec = norm(vec)
                
                if norm_query == 0 or norm_vec == 0:
                    similarity = 0.0
                else:
                    similarity = dot(query_embedding, vec) / (norm_query * norm_vec)
                
                distance = 1 - similarity
                results.append((content, distance))

        # Sort by distance (ascending)
        results.sort(key=lambda x: x[1])
        
        top_n = results[:n_results]
        return [r[0] for r in top_n], [r[1] for r in top_n]

    def count(self) -> int:
        """Count documents."""
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        return self.cursor.fetchone()[0]

    def reset(self):
        """Clear all data."""
        self.cursor.execute(f"DELETE FROM {self.table_name}")
        self.conn.commit()

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass
