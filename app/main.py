from app.sql.sqlconecctions import Connection
from app.sql.sqlschema import SQLSchemaExtractor as Schema

def main():
    try:
        conn = Connection.from_env()
        conn.connect()
        
        schema_extractor = Schema(conn.connection)
        schema = schema_extractor.extract_schema()
        #print("Esquema de la base de datos:", schema)
        
        formatted_schema = schema_extractor.formated_for_ia(schema)
        print("Esquema formateado para la IA:")
        print(formatted_schema)
        
    except Exception as e:
        # 2. El código dentro del except también debe estar identado
        print(f"Error al conectar a la base de datos: {e}")

if __name__ == "__main__":
    main()