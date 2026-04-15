
import asyncio
import os 

from dotenv import load_dotenv
from naturalsql import NaturalSQL
from nolimitai import NolimitAI
from naturalsql.utils import prompt
from naturalsql.sql.sqlquerys import QuerysConsult 
import psycopg2

load_dotenv()

nsql = NaturalSQL(
    db_url=os.getenv("DB_URL_SPECT"),
    db_type="postgresql",
    vector_backend="sqlite",
    embedding_provider="gemini",
    gemini_api_key=os.getenv("GEMINI_API_KEY"),
    gemini_embedding_model="gemini-embedding-2-preview",
)

# Build vector DB once at startup
nsql.build_vector_db(storage_path="./vector_db")

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
        response = nsql.search(request=message, storage_path="./vector_db", limit=10)
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
            psycopg2.connect(), 
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
            
    
