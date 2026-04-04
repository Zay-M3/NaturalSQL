# Extraccion del esquema de la base de datos para generar contexto para el LLM.

from typing import Any

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
            dict: Diccionario con tablas y relaciones:
                {
                    "tables": {
                        "schema.table": {
                            "schema": "schema",
                            "table": "table",
                            "columns": [("col", "type"), ...],
                        },
                    },
                    "relationships": [
                        {
                            "from_schema": "schema",
                            "from_table": "table",
                            "from_column": "column",
                            "to_schema": "schema",
                            "to_table": "table",
                            "to_column": "column",
                        },
                    ],
                }
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
                SELECT table_schema, table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY table_schema, table_name, ordinal_position
            """)
            tables = self._parse_information_schema_columns(cursor.fetchall())

            cursor.execute("""
                SELECT
                    tc.table_schema,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY tc.table_schema, tc.table_name, kcu.column_name
            """)
            relationships = self._parse_relationship_rows(cursor.fetchall())
            return {"tables": tables, "relationships": relationships}
        finally:
            cursor.close()

    def _extract_mysql(self) -> dict:
        """Extrae el esquema desde MySQL usando information_schema con DATABASE()."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT table_schema, table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                ORDER BY table_schema, table_name, ordinal_position
            """)
            tables = self._parse_information_schema_columns(cursor.fetchall())

            cursor.execute("""
                SELECT
                    table_schema,
                    table_name,
                    column_name,
                    referenced_table_schema,
                    referenced_table_name,
                    referenced_column_name
                FROM information_schema.key_column_usage
                WHERE table_schema = DATABASE()
                  AND referenced_table_name IS NOT NULL
                ORDER BY table_schema, table_name, column_name
            """)
            relationships = self._parse_relationship_rows(cursor.fetchall())
            return {"tables": tables, "relationships": relationships}
        finally:
            cursor.close()

    def _extract_sqlserver(self) -> dict:
        """Extrae el esquema desde SQL Server usando information_schema."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
            """)
            tables = self._parse_information_schema_columns(cursor.fetchall())

            cursor.execute("""
                SELECT
                    sch_parent.name AS table_schema,
                    t_parent.name AS table_name,
                    c_parent.name AS column_name,
                    sch_ref.name AS foreign_table_schema,
                    t_ref.name AS foreign_table_name,
                    c_ref.name AS foreign_column_name
                FROM sys.foreign_key_columns AS fkc
                JOIN sys.tables AS t_parent
                    ON fkc.parent_object_id = t_parent.object_id
                JOIN sys.schemas AS sch_parent
                    ON t_parent.schema_id = sch_parent.schema_id
                JOIN sys.columns AS c_parent
                    ON fkc.parent_object_id = c_parent.object_id
                    AND fkc.parent_column_id = c_parent.column_id
                JOIN sys.tables AS t_ref
                    ON fkc.referenced_object_id = t_ref.object_id
                JOIN sys.schemas AS sch_ref
                    ON t_ref.schema_id = sch_ref.schema_id
                JOIN sys.columns AS c_ref
                    ON fkc.referenced_object_id = c_ref.object_id
                    AND fkc.referenced_column_id = c_ref.column_id
                ORDER BY sch_parent.name, t_parent.name, c_parent.name
            """)
            relationships = self._parse_relationship_rows(cursor.fetchall())
            return {"tables": tables, "relationships": relationships}
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

            tables_data: dict[str, dict[str, Any]] = {}
            relationships = []
            for table_name in tables:
                if table_name.lower() in const.IGNORE_TABLE:
                    continue
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns = cursor.fetchall()
                # PRAGMA table_info retorna: (cid, name, type, notnull, dflt_value, pk)
                tables_data[f"main.{table_name}"] = {
                    "schema": "main",
                    "table": table_name,
                    "columns": [(col[1], col[2] or "TEXT") for col in columns],
                }

                cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
                for fk in cursor.fetchall():
                    # PRAGMA foreign_key_list retorna:
                    # (id, seq, table, from, to, on_update, on_delete, match)
                    to_table = fk[2]
                    from_column = fk[3]
                    to_column = fk[4]
                    if to_table.lower() in const.IGNORE_TABLE:
                        continue
                    relationships.append(
                        {
                            "from_schema": "main",
                            "from_table": table_name,
                            "from_column": from_column,
                            "to_schema": "main",
                            "to_table": to_table,
                            "to_column": to_column,
                        }
                    )

            return {"tables": tables_data, "relationships": relationships}
        finally:
            cursor.close()

    def _parse_information_schema_columns(self, rows) -> dict:
        """Parsea resultados de information_schema.columns al formato interno.

        Args:
            rows: Lista de tuplas (table_schema, table_name, column_name, data_type).

        Returns:
            dict: {
                "schema.table": {
                    "schema": "schema",
                    "table": "table",
                    "columns": [("columna", "tipo"), ...],
                },
            }
        """
        tables_data: dict[str, dict[str, Any]] = {}
        for table_schema, table_name, column_name, data_type in rows:
            if table_name.lower() in const.IGNORE_TABLE:
                continue
            key = f"{table_schema}.{table_name}"
            if key not in tables_data:
                tables_data[key] = {
                    "schema": table_schema,
                    "table": table_name,
                    "columns": [],
                }
            tables_data[key]["columns"].append((column_name, data_type))
        return tables_data

    def _parse_relationship_rows(self, rows) -> list[dict[str, str]]:
        """Parsea filas de relaciones foraneas al formato interno."""
        relationships: list[dict[str, str]] = []
        for (
            from_schema,
            from_table,
            from_column,
            to_schema,
            to_table,
            to_column,
        ) in rows:
            if from_table.lower() in const.IGNORE_TABLE or to_table.lower() in const.IGNORE_TABLE:
                continue
            relationships.append(
                {
                    "from_schema": from_schema or "main",
                    "from_table": from_table,
                    "from_column": from_column,
                    "to_schema": to_schema or "main",
                    "to_table": to_table,
                    "to_column": to_column,
                }
            )
        return relationships

    def formated_for_ia(self, schema_bundle: dict) -> list[dict[str, Any]]:
        """Formatea tablas y relaciones como documentos separados para indexacion.

        Convierte el diccionario del esquema en bloques semanticos por tabla.

        Args:
            schema_bundle: Diccionario con llaves "tables" y "relationships".

        Returns:
            list: Lista de documentos con estructura:
                {"id": str, "content": str, "metadata": dict}
        """
        formatted: list[dict[str, Any]] = []

        tables = schema_bundle.get("tables", {})
        relationships = schema_bundle.get("relationships", [])

        for table_data in tables.values():
            table_schema = table_data.get("schema", "main")
            table_name = table_data.get("table")
            columns = table_data.get("columns", [])
            column_descriptions = ", ".join(f"{col} ({dtype})" for col, dtype in columns)
            doc = (
                f"Schema: {table_schema}. "
                f"Table name: {table_name}. "
                f"It has the following columns: {column_descriptions}"
            )
            formatted.append(
                {
                    "id": f"table::{table_schema}.{table_name}",
                    "content": doc,
                    "metadata": {
                        "kind": "table",
                        "schema": table_schema,
                        "table": table_name,
                    },
                }
            )

        for rel in relationships:
            from_schema = rel["from_schema"]
            from_table = rel["from_table"]
            from_column = rel["from_column"]
            to_schema = rel["to_schema"]
            to_table = rel["to_table"]
            to_column = rel["to_column"]

            doc = (
                "Relationship: "
                f"{from_schema}.{from_table}.{from_column} "
                f"-> {to_schema}.{to_table}.{to_column}"
            )
            formatted.append(
                {
                    "id": (
                        "rel::"
                        f"{from_schema}.{from_table}.{from_column}"
                        f"->{to_schema}.{to_table}.{to_column}"
                    ),
                    "content": doc,
                    "metadata": {
                        "kind": "relationship",
                        "from_schema": from_schema,
                        "from_table": from_table,
                        "from_column": from_column,
                        "to_schema": to_schema,
                        "to_table": to_table,
                        "to_column": to_column,
                    },
                }
            )

        return formatted
