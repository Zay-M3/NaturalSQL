# NaturalSQL

Documentación en español: [README_SPANISH.md](README_SPANISH.md)

<p align="center">
  <img src="assets/naturalsql_logo.png" alt="NaturalSQL Logo" width="600"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/naturalsql/"><img src="https://img.shields.io/pypi/v/naturalsql?color=blue" alt="PyPI version"></a>
  <a href="https://pypi.org/project/naturalsql/"><img src="https://img.shields.io/pypi/pyversions/naturalsql" alt="Python versions"></a>
  <a href="https://pypi.org/project/naturalsql/"><img src="https://img.shields.io/pypi/dm/naturalsql" alt="Downloads"></a>
  <a href="https://github.com/Zay-M3/NaturalSQL/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/naturalsql" alt="License"></a>
</p>

Lightweight library to convert your SQL database schema into a vector database, so LLMs can use real table/column context to generate more accurate SQL from natural language.

## Problem

I wanted to interact with SQL databases through an LLM without pulling in large frameworks with many unrelated features.

## Solution

NaturalSQL extracts your database schema, vectorizes it using a configurable backend (`chroma` or `sqlite`) and configurable embedding provider (`local` or `gemini`), then performs semantic retrieval to return relevant schema context for your LLM.

## Installation

```bash
# Base installation
pip install naturalsql

# Chroma + local embeddings
pip install "naturalsql[chroma-local]"

# SQLite + local embeddings
pip install "naturalsql[sqlite-local]"

# SQLite + Gemini embeddings
pip install "naturalsql[sqlite-gemini]"

# Chroma + Gemini embeddings
pip install "naturalsql[chroma-gemini]"

# PostgreSQL driver support
pip install naturalsql[postgresql]

# MySQL driver support
pip install naturalsql[mysql]

# SQL Server driver support
pip install naturalsql[sqlserver]

# All DB drivers
pip install naturalsql[all-db]
```

> SQLite is included in the Python standard library.
> For Gemini, the current SDK is `google-genai` (import path: `google.genai`).
> Use environment variables for API keys (e.g. `GEMINI_API_KEY`), never hardcode secrets.

## Supported SQL engines

- PostgreSQL
- MySQL
- SQL Server
- SQLite

## Quick start

```python
from naturalsql import NaturalSQL

# 1) Create an instance
nsql = NaturalSQL(
    db_url="postgresql://user:password@localhost:5432/mydb",
    db_type="postgresql",
)

# 2) Build vector DB from schema
result = nsql.build_vector_db()
print(f"Indexed tables: {result['indexed_documents']}")
print(f"From cache: {result['from_cache']}")

# 3) Retrieve relevant tables for a question
tables = nsql.search("Show me sales from last month")

# 4) Use returned tables as LLM context
for table in tables:
    print(table)
```

### Automatic cache

The first `search()` call loads the embedding model (~2-5s). Subsequent calls reuse the in-memory instance and typically run in ~10-15ms.

Similarly, `build_vector_db()` reuses existing vector storage when available (`forced_reset=False`) to avoid unnecessary reindexing.

## E2E examples

```python
from naturalsql import NaturalSQL

# A) Chroma + local (practical tuning for Chroma 1.5.x)
nsql = NaturalSQL(
    db_url="postgresql://user:pass@localhost:5432/mydb",
    db_type="postgresql",
    vector_backend="chroma",
    embedding_provider="local",
    vector_distance_threshold=1.6,  # If search() returns [], try 1.4-1.6
)

nsql.build_vector_db(storage_path="./metadata_vdb", forced_reset=False)
tables = nsql.search("sales for the last month", limit=3)
print(tables)
```

```python
import os
from naturalsql import NaturalSQL

# B) SQLite + Gemini
nsql = NaturalSQL(
    db_url="sqlite:///./app.db",
    db_type="sqlite",
    vector_backend="sqlite",
    embedding_provider="gemini",
    gemini_api_key=os.environ["GEMINI_API_KEY"],
    gemini_embedding_model="models/text-embedding-004",
)

nsql.build_vector_db(storage_path="./metadata_vdb_sqlite", forced_reset=False)
tables = nsql.search("users with recent purchases", limit=3)
print(tables)
```

## API

### `NaturalSQL(**kwargs)`

Creates an instance with DB and embedding configuration.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `db_url` | `str \| None` | `None` | Database connection URL |
| `db_type` | `str` | `""` | Engine: `postgresql`, `mysql`, `sqlite`, `sqlserver` |
| `db_normalize_embeddings` | `bool` | `True` | Normalize embedding vectors |
| `device` | `str` | `"cpu"` | Embedding device: `cpu` or `cuda` |
| `vector_backend` | `Literal["chroma", "sqlite"]` | `"chroma"` | Vector backend |
| `embedding_provider` | `Literal["local", "gemini"]` | `"local"` | Embedding provider |
| `gemini_api_key` | `str \| None` | `None` | Required when `embedding_provider="gemini"` |
| `gemini_embedding_model` | `str` | `"models/text-embedding-004"` | Gemini embedding model |
| `vector_distance_threshold` | `float` | `1.0` | Max distance threshold used by `search()` filtering. For Chroma 1.5.x, if you get `[]`, try `1.4-1.6` (validated with `1.6`). |

### `nsql.build_vector_db(...) -> dict`

Connects to the DB, extracts schema, and indexes it in the configured vector backend (`chroma` or `sqlite`).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `storage_path` | `str` | `"./metadata_vdb"` | Vector storage path |
| `forced_reset` | `bool` | `False` | Rebuild vector collection from scratch |

Returns:

| Key | Type | Description |
|---|---|---|
| `storage_path` | `str` | Storage path used |
| `indexed_documents` | `int` | Number of indexed tables |
| `from_cache` | `bool` | `True` if existing vector store was reused |

### `nsql.search(...) -> list`

Retrieves semantically relevant tables for a natural-language question.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `request` | `str` | required | Natural-language question |
| `storage_path` | `str` | `"./metadata_vdb"` | Vector storage path |
| `limit` | `int` | `3` | Maximum number of tables to return |

### `build_prompt(relevant_tables, user_question) -> str`

Helper function in `naturalsql.utils.prompt` to create an LLM prompt using relevant tables + user question.

```python
from naturalsql.utils.prompt import build_prompt

prompt = build_prompt(tables, "Show me sales from last month")
```

## Technical strategy

1. **Connection**: connects using native drivers (`psycopg2`, `pymysql`, `sqlite3`, `pyodbc`).
2. **Schema extraction**: uses `information_schema.columns` (PostgreSQL/MySQL/SQL Server) or `PRAGMA table_info` (SQLite).
3. **Vectorization**: each table schema is transformed into a semantic document and indexed in configured backend (`chroma` or `sqlite`) with local or Gemini embeddings.
4. **Retrieval**: semantic nearest-neighbor search + `vector_distance_threshold` filtering.
5. **Caching**: embedding model and vector manager are reused per instance to reduce repeated latency.

## License

[Apache License 2.0](LICENSE)
