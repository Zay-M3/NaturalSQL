import re


class QuerysConsult:
    def __init__(self, connection):
        self.connection = connection

    def clean_sql(self, raw_query):
        return re.sub(r"```sql|```", "", raw_query, flags=re.IGNORECASE).strip()

    def execute_query(self, query):
        """Ejecuta una consulta SQL de solo lectura y devuelve los resultados.

        Args:
            query: Consulta SQL (puede contener markdown de codigo).

        Returns:
            tuple: (columns, rows) si hay resultados, (None, None) si no.

        Raises:
            ValueError: Si la consulta no es un SELECT o contiene multiples sentencias.
        """
        cleaned_sql = self.clean_sql(query)

        sql = cleaned_sql.strip().rstrip(";")
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
