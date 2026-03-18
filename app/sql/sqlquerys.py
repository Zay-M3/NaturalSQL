
import re

class QuerysConsult:
    def __init__(self, connection):
        self.connection = connection
    
    def clean_sql(self, raw_query):
        cleaned = re.sub(r'```sql|```', '', raw_query).strip()
        self.query = cleaned

    def execute_query(self, query):
        """Ejecuta una consulta SQL y devuelve los resultados, esto es necesario para que la IA pueda ejecutar las consultas SQL generadas y obtener los resultados para mostrarlos al usuario."""
        
        #limpiamos la query de posibles markdown
        self.clean_sql(query)
        
        #Verificamos que comience con SELECT para evitar consultas de modificación de datos
        sql = query.strip().rstrip(";")
        if ";" in sql:
            raise ValueError("Multiple SQL statements are not allowed.")
        if not re.match(r"(?is)^\s*select\b", sql):
            raise ValueError("Only read-only SELECT queries are allowed.")
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql)
            if cursor.description:  
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return columns, rows
            else:
                self.connection.commit()  
                return None, None
        finally:
            cursor.close()
    
    