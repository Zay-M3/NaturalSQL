# Extraccion del esquema de la base de datos para generar contexto para el LLM.

from naturalsql.utils import constans as const


class SQLSchemaExtractor:
    """Extrae el esquema de una base de datos SQL.

    Soporta PostgreSQL, MySQL, SQL Server y SQLite.

    Args:
        connection: Conexion activa a la base de datos (DB-API 2.0 compatible).
        db_type: Tipo de motor de base de datos (postgresql, mysql, sqlite, sqlserver).
    """

    def __init__(self, connection, db_type: str = "postgresql"):
        self.connection = connection
        self.db_type = db_type.strip().lower()

    def extract_schema(self) -> dict:
        """Extrae el esquema de la base de datos.

        Selecciona automaticamente la estrategia de extraccion segun el motor.

        Returns:
            dict: Diccionario con formato {tabla: [(columna, tipo), ...], ...}
        """
        extractors = {
            "postgresql": self._extract_postgresql,
            "mysql": self._extract_mysql,
            "sqlserver": self._extract_sqlserver,
            "sqlite": self._extract_sqlite,
        }

        extractor = extractors.get(self.db_type)
        if not extractor:
            raise ValueError(
                f"Motor no soportado: '{self.db_type}'. "
                f"Use uno de: {', '.join(extractors.keys())}"
            )

        return extractor()

    def _extract_postgresql(self) -> dict:
        """Extrae el esquema desde PostgreSQL usando information_schema."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)
            return self._parse_information_schema(cursor.fetchall())
        finally:
            cursor.close()

    def _extract_mysql(self) -> dict:
        """Extrae el esquema desde MySQL usando information_schema con DATABASE()."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                ORDER BY table_name, ordinal_position
            """)
            return self._parse_information_schema(cursor.fetchall())
        finally:
            cursor.close()

    def _extract_sqlserver(self) -> dict:
        """Extrae el esquema desde SQL Server usando information_schema."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'dbo'
                ORDER BY TABLE_NAME, ORDINAL_POSITION
            """)
            return self._parse_information_schema(cursor.fetchall())
        finally:
            cursor.close()

    def _extract_sqlite(self) -> dict:
        """Extrae el esquema desde SQLite usando PRAGMA."""
        cursor = self.connection.cursor()
        try:
            # Obtener lista de tablas (excluir tablas internas de SQLite)
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]

            schema = {}
            for table_name in tables:
                if table_name.lower() in const.IGNORE_TABLE:
                    continue
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns = cursor.fetchall()
                # PRAGMA table_info retorna: (cid, name, type, notnull, dflt_value, pk)
                schema[table_name] = [(col[1], col[2] or "TEXT") for col in columns]

            return schema
        finally:
            cursor.close()

    def _parse_information_schema(self, rows) -> dict:
        """Parsea resultados de information_schema.columns al formato interno.

        Args:
            rows: Lista de tuplas (table_name, column_name, data_type).

        Returns:
            dict: {tabla: [(columna, tipo), ...], ...}
        """
        schema = {}
        for table_name, column_name, data_type in rows:
            if table_name.lower() in const.IGNORE_TABLE:
                continue
            if table_name not in schema:
                schema[table_name] = []
            schema[table_name].append((column_name, data_type))
        return schema

    def formated_for_ia(self, schema: dict) -> list:
        """Formatea el esquema para que sea legible por la IA.

        Convierte el diccionario del esquema en bloques semanticos por tabla.

        Args:
            schema: Diccionario con formato {tabla: [(columna, tipo), ...], ...}

        Returns:
            list: Lista de strings, cada uno describiendo una tabla y sus columnas.
        """
        formatted = []
        for table, columns in schema.items():
            column_descriptions = ", ".join(f"{col} ({dtype})" for col, dtype in columns)
            doc = f"Table name: {table}. It has the following columns: {column_descriptions}"
            formatted.append(doc)
        return formatted
