import importlib
import sys
import types

import naturalsql.controller.controllervector as controllervector


def test_collection_exists_checks_paths_before_chroma_client(monkeypatch):
    chroma_calls = {"persistent_client": 0}

    fake_chromadb = types.ModuleType("chromadb")

    def fake_persistent_client(path):
        chroma_calls["persistent_client"] += 1
        return object()

    fake_chromadb.PersistentClient = fake_persistent_client
    monkeypatch.setitem(sys.modules, "chromadb", fake_chromadb)
    monkeypatch.setattr(controllervector.os.path, "isdir", lambda _p: False)
    monkeypatch.setattr(controllervector.os.path, "exists", lambda _p: False)

    result = controllervector.VectorManager.collection_exists("/fake/storage")

    assert result == 0
    assert chroma_calls["persistent_client"] == 0


def test_collection_exists_checks_sqlite_file_before_connect(monkeypatch):
    sqlite_calls = {"connect": 0}

    fake_sqlite3 = types.ModuleType("sqlite3")

    def fake_connect(_db_path):
        sqlite_calls["connect"] += 1
        return object()

    fake_sqlite3.connect = fake_connect
    monkeypatch.setitem(sys.modules, "sqlite3", fake_sqlite3)
    monkeypatch.setattr(controllervector.os.path, "isdir", lambda _p: False)

    def fake_exists(path):
        return str(path).endswith("chroma.sqlite3")

    monkeypatch.setattr(controllervector.os.path, "exists", fake_exists)

    result = controllervector.VectorManager.collection_exists("/fake/storage")

    assert result == 0
    assert sqlite_calls["connect"] == 0


def test_collection_exists_ignores_sqlite_errors_and_returns_zero(monkeypatch):
    fake_sqlite3 = types.ModuleType("sqlite3")

    def fake_connect(_db_path):
        raise RuntimeError("cannot open")

    fake_sqlite3.connect = fake_connect
    monkeypatch.setitem(sys.modules, "sqlite3", fake_sqlite3)
    monkeypatch.setattr(controllervector.os.path, "isdir", lambda _p: False)
    monkeypatch.setattr(controllervector.os.path, "exists", lambda path: str(path).endswith("vectors.db"))

    result = controllervector.VectorManager.collection_exists("/fake/storage")

    assert result == 0


def test_collection_exists_returns_sqlite_row_count_when_vectors_present(monkeypatch):
    class FakeCursor:
        def execute(self, _query):
            return None

        def fetchone(self):
            return (4,)

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def close(self):
            return None

    fake_sqlite3 = types.ModuleType("sqlite3")
    fake_sqlite3.connect = lambda _db_path: FakeConnection()
    monkeypatch.setitem(sys.modules, "sqlite3", fake_sqlite3)
    monkeypatch.setattr(controllervector.os.path, "isdir", lambda _p: False)
    monkeypatch.setattr(controllervector.os.path, "exists", lambda path: str(path).endswith("vectors.db"))

    result = controllervector.VectorManager.collection_exists("/fake/storage")

    assert result == 4
