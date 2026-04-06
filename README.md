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
    gemini_embedding_model="gemini-embedding-2-preview",
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
| `gemini_embedding_model` | `str` | `"gemini-embedding-2-preview"` | Gemini embedding model |
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

## How It Works Internally 

Think of NaturalSQL as a 5-step pipeline:

1. Read DB structure with simple SQL/system queries.
2. Normalize that structure into one common Python dictionary.
3. Convert dictionary entries into semantic text documents.
4. Turn those texts into embedding vectors.
5. Store vectors in Chroma or SQLite and retrieve best matches for RAG.

### 1) Schema extraction strategy by DB engine

NaturalSQL does not parse SQL files. It asks the live database for metadata.

- PostgreSQL: `information_schema.columns` for columns + joins over `information_schema.table_constraints`, `key_column_usage`, `constraint_column_usage` for foreign keys.
- MySQL: `information_schema.columns` and `information_schema.key_column_usage` (scoped by `DATABASE()`).
- SQL Server: `INFORMATION_SCHEMA.COLUMNS` for columns + `sys.foreign_key_columns` with `sys.tables`, `sys.schemas`, `sys.columns` for FK relationships.
- SQLite: `sqlite_master` (table list), `PRAGMA table_info('<table>')` for columns, `PRAGMA foreign_key_list('<table>')` for relationships.

Essential idea: most engines use `information_schema`; SQLite uses `PRAGMA`.

### 2) Unified schema dictionary (same format for all engines)

After extraction, data is normalized to one shape:

```python
{
  "tables": {
    "public.users": {
      "schema": "public",
      "table": "users",
      "columns": [("id", "integer"), ("email", "text")]
    }
  },
  "relationships": [
    {
      "from_schema": "public",
      "from_table": "orders",
      "from_column": "user_id",
      "to_schema": "public",
      "to_table": "users",
      "to_column": "id"
    }
  ]
}
```

This is what makes the next steps backend-agnostic.

### 3) Dictionary to semantic documents (for embedding)

The extractor then generates documents for two kinds of knowledge:

- `kind=table`: table + columns + data types
- `kind=relationship`: FK direction between tables

Example payload item:

```python
{
  "id": "table::public.users",
  "content": "Schema: public. Table name: users. It has the following columns: id (integer), email (text)",
  "metadata": {
    "kind": "table",
    "schema": "public",
    "table": "users"
  }
}
```

Relationship example:

```python
{
  "id": "rel::public.orders.user_id->public.users.id",
  "content": "Relationship: public.orders.user_id -> public.users.id",
  "metadata": {
    "kind": "relationship"
  }
}
```

### 4) Embedding generation

NaturalSQL supports two embedding providers:

- `local`: `sentence-transformers` (`all-MiniLM-L6-v2`)
- `gemini`: `google-genai` (`gemini-embedding-2-preview` by default)

The system embeds:

- documents with retrieval-document mode
- user query with retrieval-query mode

This gives a vector for each schema document and one vector for each user question.

### 5) Vector storage strategy (Chroma vs SQLite)

#### Chroma backend

- Uses `chromadb.PersistentClient(path=storage_path)`.
- Stores `ids`, `documents`, `embeddings`, `metadatas` in collection `db_schema`.
- Retrieval uses native vector query + metadata filter, for example `where={"kind": "table"}`.

#### SQLite backend

- Creates `vectors.db` under `storage_path`.
- Table schema: `id`, `content`, `embedding` (JSON text), `metadata_json` (JSON text).
- Retrieval loads rows and computes cosine distance in Python (NumPy if available, pure Python fallback if not).
- Also filters by `kind` from `metadata_json`.

### 6) Retrieval flow for RAG

When you call `search("...", limit=N)`, the flow is:

1. Embed query text.
2. Query `kind=table` and `kind=relationship` separately.
3. Merge both result sets.
4. Sort by distance (smaller is better).
5. Apply `vector_distance_threshold`.
6. Return top `N` schema contexts for your prompt.

So the LLM receives real schema context instead of guessing table/column names.

### 7) Minimal end-to-end internal view

```python
from naturalsql.sql.sqlschema import SQLSchemaExtractor
from naturalsql.controller.controllervector import VectorManager

# 1) extract
extractor = SQLSchemaExtractor(connection, db_type="postgresql")
schema_bundle = extractor.extract_schema()

# 2) normalize -> semantic docs
documents_payload = extractor.formated_for_ia(schema_bundle)

# 3) embed + persist (chroma or sqlite depending on config)
vm = VectorManager(storage_path="./metadata_vdb", force_reset=False, config=config)
vm.index_documents(documents_payload)

# 4) retrieve for RAG
context_docs = vm.search_relevant_tables("sales from last month", limit=3)
```

### Backend comparison

| Aspect | Chroma | SQLite |
|---|---|---|
| Storage files | Chroma persistent directory | `vectors.db` file |
| Vector query | Native Chroma ANN query | Python cosine distance over stored vectors |
| Metadata filtering | Native `where` filter | JSON metadata filter in Python |
| Dependency profile | Requires `chromadb` | Uses stdlib `sqlite3` + optional NumPy |
| Operational style | Dedicated vector DB behavior | Lightweight embedded local store |

### Current limitations

These points are based on current implementation behavior:

- No hybrid ranking strategy yet: retrieval is distance-based over embeddings only (no lexical/BM25 rerank).
- Relationship text is concise (`A.col -> B.col`), so very complex semantics are not explicitly encoded.
- SQLite backend computes similarity in Python, so very large corpora may be slower than native vector engines.
- `build_vector_db()` returns `indexed_documents` as total indexed documents (tables + relationships), while wording may be interpreted as only tables.
- Schema extraction is structural (tables/columns/FKs). It does not ingest business definitions, comments, or curated ontology unless you add them as extra documents.

In practice, this still provides strong RAG context for SQL generation because table fields and foreign-key topology are the highest-value grounding signals.

## License

[Apache License 2.0](LICENSE)
