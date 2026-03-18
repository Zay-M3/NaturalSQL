from app.sql.sqlconecctions import Connection
from app.sql.sqlschema import SQLSchemaExtractor as Schema
from app.controller.controllervector import VectorManager as Vector
from app.sql.sqlquerys import QuerysConsult as Query
from app.utils.config import AppConfig
from app.utils.prompt import build_prompt
from groq import Groq

def main():
    try:
        #Globalizamos la carga de las .env
        config = AppConfig.from_env()

        client = Groq(
            api_key=config.api_key_llm,
        )

        conn = Connection.from_config(config)
        conn.connect()
        
        schema_extractor = Schema(conn.connection)
        schema = schema_extractor.extract_schema()
        
        formatted_schema = schema_extractor.formated_for_ia(schema)

        question = "Give me the last maintenace, please"      
            
        vector_manager = Vector(force_reset=True)
        vector_manager.index_tables(formatted_schema)
        db_vectorial = vector_manager.search_relevant_tables(question)
        
        prompt = build_prompt(db_vectorial, question)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        print("Generated SQL Query:")
        result = response.choices[0].message.content.strip()
        print(result)
        

        query_executor = Query(conn.connection)
        results = query_executor.execute_query(result)
        print("Query Results:")
        for row in results:
            print(row)

        
    except Exception as e:
        # 2. El código dentro del except también debe estar identado
        print(f"Error al conectar a la base de datos: {e}")

if __name__ == "__main__":
    main()