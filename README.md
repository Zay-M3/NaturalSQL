# NaturalSQL

<p align="center">
  <img src="assets/naturalsql_logo.png" alt="NaturalSQL Logo" width="600"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/naturalsql/"><img src="https://img.shields.io/pypi/v/naturalsql?color=blue" alt="PyPI version"></a>
  <a href="https://pypi.org/project/naturalsql/"><img src="https://img.shields.io/pypi/pyversions/naturalsql" alt="Python versions"></a>
  <a href="https://pypi.org/project/naturalsql/"><img src="https://img.shields.io/pypi/dm/naturalsql" alt="Downloads"></a>
  <a href="https://github.com/Zay-M3/NaturalSQL/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/naturalsql" alt="License"></a>
</p>

Libreria ligera para convertir el esquema de tu base de datos SQL en una base de datos vectorial, permitiendo que modelos LLM tengan contexto para generar consultas SQL precisas a partir de lenguaje natural.

## Problema

Necesito interactuar con mi base de datos usando un LLM, pero muchas librerias contienen funcionalidades adicionales que las hacen pesadas para proyectos pequenos.

## Solucion

NaturalSQL extrae el esquema de tu base de datos, lo vectoriza con backend configurable (`chroma` o `sqlite`) y embeddings configurables (`local` o `gemini`), y usa busqueda por similitud semantica para proporcionar contexto relevante al LLM.

## Instalacion

```bash
# Instalacion base
pip install naturalsql

# Chroma + embeddings locales
pip install "naturalsql[chroma-local]"

# SQLite + embeddings locales
pip install "naturalsql[sqlite-local]"

# SQLite + Gemini embeddings
pip install "naturalsql[sqlite-gemini]"

# Chroma + Gemini embeddings
pip install "naturalsql[chroma-gemini]"

# Con soporte para PostgreSQL
pip install naturalsql[postgresql]

# Con soporte para MySQL
pip install naturalsql[mysql]

# Con soporte para SQL Server
pip install naturalsql[sqlserver]

# Con soporte para todos los motores
pip install naturalsql[all-db]
```

> SQLite esta incluido en la libreria estandar de Python, no requiere dependencias adicionales.
> Para Gemini, el SDK actual es `google-genai` (import: `google.genai`).
> Usa variables de entorno para llaves API (ej. `GEMINI_API_KEY`), no hardcodees secretos en codigo.

## Motores SQL soportados

- PostgreSQL
- MySQL
- SQL Server
- SQLite

## Uso rapido

```python
from naturalsql import NaturalSQL

# 1. Crear instancia con la configuracion de conexion
nsql = NaturalSQL(
    db_url="postgresql://user:password@localhost:5432/mydb",
    db_type="postgresql",
)

# 2. Construir la base vectorial a partir del esquema de la BD
result = nsql.build_vector_db()
print(f"Tablas indexadas: {result['indexed_documents']}")
print(f"Desde cache: {result['from_cache']}")

# 3. Buscar tablas relevantes para una pregunta
tables = nsql.search("Quiero ver las ventas del ultimo mes")

# 4. Usar las tablas como contexto para tu LLM preferido
for table in tables:
    print(table)
```

### Cache automatico

La primera llamada a `search()` carga el modelo de embeddings (~2-5 segundos). Las llamadas posteriores reutilizan la instancia en memoria y responden en ~10-15ms.

De igual forma, `build_vector_db()` detecta si la base vectorial ya existe. Si `forced_reset=False` (por defecto), reutiliza la coleccion existente sin reconectarse a la BD ni regenerar embeddings.

```python
# Primera busqueda: ~2-5s (carga del modelo)
tables = nsql.search("ventas del ultimo mes")

# Busquedas posteriores: ~10-15ms (modelo en cache)
tables = nsql.search("clientes registrados hoy")
tables = nsql.search("productos con bajo inventario")
```

### Ejemplos E2E

```python
from naturalsql import NaturalSQL

# A) Chroma + local (ajuste practico para Chroma 1.5.x)
nsql = NaturalSQL(
    db_url="postgresql://user:pass@localhost:5432/mydb",
    db_type="postgresql",
    vector_backend="chroma",
    embedding_provider="local",
    vector_distance_threshold=1.6,  # Si `search()` retorna [], prueba 1.4-1.6
)

nsql.build_vector_db(storage_path="./metadata_vdb", forced_reset=False)
tables = nsql.search("ventas del ultimo mes", limit=3)
print(tables)
```

```python
import os
from naturalsql import NaturalSQL

# B) SQLite + Gemini (llave por variable de entorno)
nsql = NaturalSQL(
    db_url="sqlite:///./app.db",
    db_type="sqlite",
    vector_backend="sqlite",
    embedding_provider="gemini",
    gemini_api_key=os.environ["GEMINI_API_KEY"],
    gemini_embedding_model="models/text-embedding-004",
)

nsql.build_vector_db(storage_path="./metadata_vdb_sqlite", forced_reset=False)
tables = nsql.search("usuarios con compras recientes", limit=3)
print(tables)
```

> Nota: Si usas Gemini, define `GEMINI_API_KEY` en tu entorno y evita exponerla en repositorios o logs.

## API

### `NaturalSQL(**kwargs)`

Crea una instancia con la configuracion de conexion y embeddings.

| Parametro | Tipo | Default | Descripcion |
|---|---|---|---|
| `db_url` | `str \| None` | `None` | URL de conexion a la BD |
| `db_type` | `str` | `""` | Motor: `postgresql`, `mysql`, `sqlite`, `sqlserver` |
| `db_normalize_embeddings` | `bool` | `True` | Normalizar vectores de embeddings |
| `device` | `str` | `"cpu"` | Dispositivo: `cpu` o `cuda` |
| `vector_backend` | `Literal["chroma", "sqlite"]` | `"chroma"` | Backend vectorial |
| `embedding_provider` | `Literal["local", "gemini"]` | `"local"` | Proveedor de embeddings |
| `gemini_api_key` | `str \| None` | `None` | Requerido si `embedding_provider="gemini"` |
| `gemini_embedding_model` | `str` | `"models/text-embedding-004"` | Modelo de embeddings Gemini |
| `vector_distance_threshold` | `float` | `1.0` | Umbral maximo de distancia en `search()`. Con Chroma 1.5.x, si obtienes `[]`, prueba `1.4-1.6` (validado en e2e con `1.6`). |

### `nsql.build_vector_db(...) -> dict`

Conecta a la BD, extrae el esquema y lo indexa en el backend vectorial configurado (`chroma` o `sqlite`).

| Parametro | Tipo | Default | Descripcion |
|---|---|---|---|
| `storage_path` | `str` | `"./metadata_vdb"` | Ruta de almacenamiento vectorial |
| `forced_reset` | `bool` | `False` | Eliminar coleccion existente antes de reindexar |

Retorna un `dict` con:

| Clave | Tipo | Descripcion |
|---|---|---|
| `storage_path` | `str` | Ruta utilizada |
| `indexed_documents` | `int` | Cantidad de tablas indexadas |
| `from_cache` | `bool` | `True` si reutilizo coleccion existente |

### `nsql.search(...) -> list`

Busca tablas semanticamente relevantes para una consulta en lenguaje natural.

| Parametro | Tipo | Default | Descripcion |
|---|---|---|---|
| `request` | `str` | requerido | Pregunta en lenguaje natural |
| `storage_path` | `str` | `"./metadata_vdb"` | Ruta de la base vectorial |
| `limit` | `int` | `3` | Maximo de tablas a retornar |

### `build_prompt(relevant_tables, user_question) -> str`

Funcion auxiliar en `naturalsql.utils.prompt` que genera un prompt listo para enviar al LLM, combinando las tablas relevantes con la pregunta del usuario.

```python
from naturalsql.utils.prompt import build_prompt

prompt = build_prompt(tables, "Quiero ver las ventas del ultimo mes")
```

## Estrategia tecnica

1. **Conexion**: Se conecta a la BD usando la URL proporcionada con drivers nativos (psycopg2, pymysql, sqlite3, pyodbc).

2. **Extraccion de esquema**: Consulta `information_schema.columns` (PostgreSQL, MySQL, SQL Server) o `PRAGMA table_info` (SQLite) para obtener tablas, columnas y tipos de datos.

3. **Vectorizacion**: Cada tabla se convierte en un bloque semantico y se indexa en el backend configurado (`chroma` o `sqlite`) usando embeddings locales (SentenceTransformer) o Gemini (`google-genai`).

4. **Busqueda**: Ante una pregunta del usuario, se buscan las tablas mas relevantes por similitud semantica y se filtran por `vector_distance_threshold` (default `1.0`; en Chroma 1.5.x puede requerir `1.4-1.6`).

5. **Cache**: El modelo de embeddings se carga una sola vez por instancia de `NaturalSQL`. Las busquedas posteriores reutilizan la instancia en memoria (~10-15ms vs ~2-5s).

## Licencia

[Apache License 2.0](LICENSE)
