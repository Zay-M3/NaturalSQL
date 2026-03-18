from urllib.parse import parse_qs, unquote, urlparse

from naturalsql.utils import constans as const
from naturalsql.utils.config import AppConfig


class Connection:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None

    @classmethod
    def from_config(cls, config: AppConfig):
        """Create a connection instance using an injected AppConfig object."""

        if (config.db_url is None) or (config.db_type is None):
            raise ValueError("DB_URL y DB_TYPE son requeridos en la configuracion.")

        db_type = config.db_type
        if db_type not in const.CONNECTION_QLS:
            raise ValueError(
                "DB_TYPE no soportado o ausente. Use DB_URL o uno de: "
                f"{', '.join(const.CONNECTION_QLS.keys())}"
            )

        connection_string = config.db_url
        if connection_string:
            return cls(connection_string)

    def connect(self):
        """Open a real DB connection based on the URL scheme."""
        if self.connection:
            return self.connection

        if not self.connection_string:
            raise ValueError("No se proporciono connection_string.")

        parsed = urlparse(self.connection_string)
        scheme = parsed.scheme.lower()
        base_scheme = scheme.split("+", 1)[0]
        if base_scheme == "mssql":
            base_scheme = "sqlserver"

        connector_by_engine = {
            "postgresql": self._connect_postgresql,
            "mysql": self._connect_mysql,
            "sqlite": self._connect_sqlite,
            "sqlserver": self._connect_sqlserver,
        }

        connector = connector_by_engine.get(base_scheme)
        if not connector:
            raise ValueError(f"Motor no soportado en URL: {scheme}")

        self.connection = connector(parsed)
        return self.connection

    def _connect_postgresql(self, parsed):
        import psycopg2

        return psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            dbname=parsed.path.lstrip("/"),
        )

    def _connect_mysql(self, parsed):
        import pymysql

        return pymysql.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=parsed.path.lstrip("/"),
            autocommit=False,
        )

    def _connect_sqlite(self, parsed):
        import sqlite3

        database_path = parsed.path or ""
        if database_path.startswith("/"):
            database_path = database_path[1:]
        if database_path == "":
            database_path = ":memory:"
        return sqlite3.connect(database_path)

    def _connect_sqlserver(self, parsed):
        import pyodbc

        query_params = parse_qs(parsed.query)
        driver = query_params.get("driver", ["ODBC Driver 17 for SQL Server"])[0]
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={parsed.hostname},{parsed.port or 1433};"
            f"DATABASE={parsed.path.lstrip('/')};"
            f"UID={unquote(parsed.username or '')};"
            f"PWD={unquote(parsed.password or '')};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str)

    def disconnect(self):
        """Cierra la conexion a la base de datos."""
        if self.connection:
            self.connection.close()
            self.connection = None
