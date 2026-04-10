# Test Suite Guide

This project uses `pytest` to validate three core areas: schema extraction, database connection handling, and vector collection checks.

## Prerequisite

- `pytest` must be installed in your active Python environment.

## Test Structure

### `test/schema/test_sqlschema.py`

- Validates `SQLSchemaExtractor` behavior.
- Covers unsupported engine handling, information schema parsing, relationship parsing, SQLite in-memory extraction, and AI-oriented output formatting.
- Scope: schema metadata correctness and relationship normalization.

### `test/connection/test_sqlconnections.py`

- Validates `Connection` URL parsing and driver-specific connect calls.
- Uses monkeypatch/fake modules for `psycopg2`, `pymysql`, and `pyodbc`, and checks SQLite connection path behavior.
- Scope: connection parameter mapping across supported SQL engines.

### `test/vector_manager/test_controllervector.py`

- Validates `VectorManager.collection_exists` decision flow.
- Tests path pre-checks, SQLite file checks, error fallback behavior, and count retrieval when vectors are present.
- Scope: safe collection existence detection and robust failure handling.

## Running Tests

Run commands from the project root (`C:\Users\oscar\Desktop\NaturalSQL`).

### Run all tests

```bash
pytest
```

### Run by folder

```bash
pytest test/schema
pytest test/connection
pytest test/vector_manager
```

### Run a single file

```bash
pytest test/schema/test_sqlschema.py
pytest test/connection/test_sqlconnections.py
pytest test/vector_manager/test_controllervector.py
```
