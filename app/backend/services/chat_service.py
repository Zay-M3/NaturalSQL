
import asyncio
import logging
import os
import sqlite3

from dotenv import load_dotenv
from naturalsql import NaturalSQL
from nolimitai import NolimitAI
from naturalsql.utils import prompt
from naturalsql.sql.sqlquerys import QuerysConsult 
import psycopg2

load_dotenv()

logger = logging.getLogger(__name__)
VECTOR_DB_PATH = "./vector_db"

nsql = NaturalSQL(
    db_url=os.getenv("DB_URL_SPECT"),
    db_type="postgresql",
    vector_backend="sqlite",
    embedding_provider="gemini",
    gemini_api_key=os.getenv("GEMINI_API_KEY"),
    gemini_embedding_model="gemini-embedding-2-preview",
)

def _count_indexed_vectors(storage_path: str) -> int:
    """Return number of indexed vector documents from sqlite store."""
    db_path = os.path.join(storage_path, "vectors.db")
    if not os.path.exists(db_path):
        return 0

    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM vectors")
            return int(cur.fetchone()[0])
    except Exception:
        logger.exception("Error counting vectors in %s", db_path)
        return 0


def _bootstrap_vector_db() -> None:
    """Build or repair vector DB, avoiding partial-cache reuse."""
    before_count = _count_indexed_vectors(VECTOR_DB_PATH)
    force_rebuild = before_count <= 1

    if force_rebuild:
        logger.warning(
            "Detected partial/empty vector index (%s rows). Forcing rebuild.",
            before_count,
        )

    try:
        result = nsql.build_vector_db(
            storage_path=VECTOR_DB_PATH,
            forced_reset=force_rebuild,
        )

        after_count = _count_indexed_vectors(VECTOR_DB_PATH)

        # If a cached index was reused but still looks partial, repair once.
        if result.get("from_cache") and after_count <= 1:
            logger.warning(
                "Cached vector index still partial (%s rows). Rebuilding.",
                after_count,
            )
            nsql.build_vector_db(storage_path=VECTOR_DB_PATH, forced_reset=True)
            after_count = _count_indexed_vectors(VECTOR_DB_PATH)

        logger.warning(
            "Vector DB bootstrap completed. rows_before=%s rows_after=%s from_cache=%s indexed_documents=%s",
            before_count,
            after_count,
            result.get("from_cache"),
            result.get("indexed_documents"),
        )
    except Exception:
        logger.exception("Failed to bootstrap vector DB")


# Build vector DB once at startup (self-heals partial cache states)
_bootstrap_vector_db()

nlai = NolimitAI()

nlai.set_config(
    temperature=0.7,
    max_tokens=2700,
    top_p=0.9,
    keys={
        "openrouter": os.getenv("OPENROUTER_API_KEY"),
    }
)

class ChatService():
    def __init__(self):
        pass

    def search_with_nsql(self, message:str) -> list:
        response = nsql.search(request=message, storage_path=VECTOR_DB_PATH, limit=10)
        return response
    
    async def process_context_with_llm(self, message:str):
        # Aquí iría la lógica para procesar el contexto con un modelo de lenguaje
        context = self.search_with_nsql(message)
                
        # Aquí iría la lógica para generar una respuesta utilizando el contexto y el mensaje
        
        promt = prompt.build_prompt(relevant_tables=context, user_question=message, db_type="postgresql")
        
        sql_query = ""
        
        async for token in nlai.chat(promt, model="openai/gpt-4o-mini"):
            sql_query += token
        
        connec = await asyncio.to_thread(
            psycopg2.connect, 
            os.getenv("DB_URL_SPECT")
        )
        try:
            query = QuerysConsult(connection=connec)
            columns, rows = await asyncio.to_thread(query.execute_query, sql_query)

            promt_response = prompt.prompt_query(message, {"columns": columns, "rows": rows})

            async for token in nlai.chat(promt_response, model="openai/gpt-4o-mini"):
                yield token
        finally:
            connec.close()
            
    
