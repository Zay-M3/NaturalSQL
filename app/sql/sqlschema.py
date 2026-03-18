#En este archivo extraemos el esquema de la base de datos a partir conexion a la base de datos, esto es necesario para que el modelo pueda generar consultas SQL correctas.

from app.utils import constans as const

class SQLSchemaExtractor:
    """Inyectmos la conexion de la bd para extraer el esquema de la base de datos"""
    def __init__(self, connection):
        self.connection = connection

    def extract_schema(self):
        """Extraemos el esquema de la base de datos
        Esto mediante una consulta a la informacion del esquema de la base de datos, obteniendo las tablas, columnas y tipos de datos.
        
        return un diccionario con el formato {tabla: [(columna, tipo), ...], ...}
        """
        cursor = self.connection.cursor()
        try:
            # Para PostgreSQL y MySQL, obtenemos las tablas y columnas
            cursor.execute("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
            """)
            schema_info = cursor.fetchall()
            schema = {}
            for table_name, column_name, data_type in schema_info:
                if table_name.lower() in const.IGNORE_TABLE:
                    continue
                if table_name not in schema:
                    schema[table_name] = []
                schema[table_name].append((column_name, data_type))
            return schema
        finally:
            cursor.close()
            
    def formated_for_ia(self, schema):
        """Formateamos el esquema para que sea legible por la IA
        Esto convierte el diccionario del esquema en un formato de texto que describe las tablas y sus columnas, por ejemplo:
        users: id (integer), name (varchar), email (varchar)
        orders: id (integer), user_id (integer), total (decimal)
        
        return un string con el formato descrito anteriormente
        
        """
        formatted = []
        for table, columns in schema.items():
            column_descriptions = ", ".join(f"{col} ({dtype})" for col, dtype in columns)
            # Creamos un bloque semántico por cada tabla
            doc = f"Table name: {table}. It has the following columns: {column_descriptions}"
            formatted.append(doc)
        return formatted
        