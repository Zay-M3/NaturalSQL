import os
from urllib.parse import parse_qs, unquote, urlparse

from app.utils import constans as const

class Connection:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None

    @classmethod
    def from_env(cls):
        """Create a connection instance using DB_URL, esto para simplificar la configuracion de la conexion a la base de datos, permitiendo que el usuario solo tenga que configurar las variables de entorno y no preocuparse por el formato de la URL de conexion."""
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except Exception:
            # If python-dotenv is not installed, continue with existing env vars.
            pass

        connection_string = os.getenv("DB_URL")
        if connection_string:
            return cls(connection_string)

        db_type = (os.getenv("DB_TYPE") or "").lower().strip()
        if db_type not in const.CONNECTION_QLS:
            raise ValueError(
                "DB_TYPE no soportado o ausente. Use DB_URL o uno de: "
                f"{', '.join(const.CONNECTION_QLS.keys())}"
            )

        connection_template = const.CONNECTION_QLS[db_type]
        connection_string = connection_template.format(
            user=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", ""),
            database=os.getenv("DB_NAME", ""),
        )
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
        """Cierra la conexion a la base de datos y formatea a None la variable de conexion para evitar conexiones abiertas."""
        if self.connection:
            self.connection.close()
            self.connection = None
