import sys
import types

from naturalsql.sql.sqlconecctions import Connection


def test_connect_sqlite_url_uses_sqlite3_without_external_drivers():
    captured = {}

    original_connect_sqlite = Connection._connect_sqlite

    def wrapped_connect_sqlite(self, parsed):
        import sqlite3

        original_connect = sqlite3.connect

        def tracking_connect(path):
            captured["path"] = path
            return original_connect(":memory:")

        sqlite3.connect = tracking_connect
        try:
            return original_connect_sqlite(self, parsed)
        finally:
            sqlite3.connect = original_connect

    conn = None
    Connection._connect_sqlite = wrapped_connect_sqlite
    try:
        conn = Connection("sqlite:///tmp/test_db.sqlite")
        db_conn = conn.connect()
        assert captured["path"] == "tmp/test_db.sqlite"
    finally:
        Connection._connect_sqlite = original_connect_sqlite
        if conn is not None:
            conn.disconnect()


def test_connect_postgresql_calls_psycopg2_with_parsed_fields(monkeypatch):
    captured = {}

    fake_module = types.ModuleType("psycopg2")

    def fake_connect(**kwargs):
        captured.update(kwargs)
        return object()

    fake_module.connect = fake_connect
    monkeypatch.setitem(sys.modules, "psycopg2", fake_module)

    conn = Connection("postgresql://john:secret@db.local:5433/sales")
    result = conn.connect()

    assert result is not None
    assert captured == {
        "host": "db.local",
        "port": 5433,
        "user": "john",
        "password": "secret",
        "dbname": "sales",
    }


def test_connect_mysql_calls_pymysql_with_parsed_fields(monkeypatch):
    captured = {}

    fake_module = types.ModuleType("pymysql")

    def fake_connect(**kwargs):
        captured.update(kwargs)
        return object()

    fake_module.connect = fake_connect
    monkeypatch.setitem(sys.modules, "pymysql", fake_module)

    conn = Connection("mysql://ana:pw@mysql.local:3307/inventory")
    result = conn.connect()

    assert result is not None
    assert captured == {
        "host": "mysql.local",
        "port": 3307,
        "user": "ana",
        "password": "pw",
        "database": "inventory",
        "autocommit": False,
    }


def test_connect_sqlserver_calls_pyodbc_with_driver_and_server(monkeypatch):
    captured = {}

    fake_module = types.ModuleType("pyodbc")

    def fake_connect(conn_str):
        captured["conn_str"] = conn_str
        return object()

    fake_module.connect = fake_connect
    monkeypatch.setitem(sys.modules, "pyodbc", fake_module)

    conn = Connection(
        "mssql://sa:TopSecret@sql.local:1444/warehouse?driver=ODBC+Driver+18+for+SQL+Server"
    )
    result = conn.connect()

    assert result is not None
    conn_str = captured["conn_str"]
    assert "DRIVER={ODBC Driver 18 for SQL Server};" in conn_str
    assert "SERVER=sql.local,1444;" in conn_str
    assert "DATABASE=warehouse;" in conn_str
    assert "UID=sa;" in conn_str
    assert "PWD=TopSecret;" in conn_str
