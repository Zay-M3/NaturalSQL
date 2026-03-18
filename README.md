# NaturalSQL

Libreria ligera para convertir el esquema de tu base de datos SQL en una base de datos vectorial, permitiendo que modelos LLM tengan contexto para generar consultas SQL precisas a partir de lenguaje natural.

## Problema

Necesito interactuar con mi base de datos usando un LLM, pero muchas librerias contienen funcionalidades adicionales que las hacen pesadas para proyectos pequenos.

## Solucion

NaturalSQL extrae el esquema de tu base de datos, lo vectoriza con ChromaDB + SentenceTransformer (`all-MiniLM-L6-v2`), y usa busqueda por similitud semantica para proporcionar contexto relevante al LLM.

## Instalacion

```bash
# Instalacion base
pip install naturalsql

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

## Motores SQL soportados

- PostgreSQL
- MySQL
- SQL Server
- SQLite

## Uso rapido

```python
from naturalsql import set_config, build_vector_db_from_url, extract_relevant_tables_from_vector_db

# 1. Configurar la conexion
config = set_config(
    db_url="postgresql://user:password@localhost:5432/mydb",
    db_type="postgresql",
)

# 2. Construir la base vectorial a partir del esquema de la BD
result = build_vector_db_from_url(
    storage_path="./metadata_vdb",
    forced_reset=True,
    config=config,
)
print(f"Tablas indexadas: {result['indexed_documents']}")

# 3. Buscar tablas relevantes para una pregunta
tables = extract_relevant_tables_from_vector_db(
    request="Quiero ver las ventas del ultimo mes",
    storage_path="./metadata_vdb",
    limit=3,
    config=config,
)

# 4. Usar las tablas como contexto para tu LLM preferido
for table in tables:
    print(table)
```

### Ejemplo completo con un LLM (Groq)

```python
from naturalsql import set_config, build_vector_db_from_url, extract_relevant_tables_from_vector_db
from naturalsql.utils.prompt import build_prompt
from groq import Groq

config = set_config(
    api_key_llm="tu_api_key",
    db_url="postgresql://user:pass@localhost:5432/mydb",
    db_type="postgresql",
)

build_vector_db_from_url(config=config, forced_reset=True)

question = "What is the first user to register?"
tables = extract_relevant_tables_from_vector_db(request=question, config=config)

prompt = build_prompt(tables, question)

client = Groq(api_key=config.api_key_llm)
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
)
print(response.choices[0].message.content)
```

## API

### `set_config(**kwargs) -> AppConfig`

Crea una configuracion inmutable.

| Parametro | Tipo | Default | Descripcion |
|---|---|---|---|
| `api_key_llm` | `str \| None` | `None` | API key para el LLM (no usado internamente) |
| `db_url` | `str \| None` | `None` | URL de conexion a la BD |
| `db_type` | `str` | `""` | Motor: `postgresql`, `mysql`, `sqlite`, `sqlserver` |
| `db_normalize_embeddings` | `bool` | `True` | Normalizar vectores de embeddings |
| `device` | `str` | `"cpu"` | Dispositivo: `cpu` o `cuda` |

### `build_vector_db_from_url(...) -> dict`

Conecta a la BD, extrae el esquema y lo indexa en ChromaDB.

| Parametro | Tipo | Default | Descripcion |
|---|---|---|---|
| `storage_path` | `str` | `"./metadata_vdb"` | Ruta de almacenamiento vectorial |
| `forced_reset` | `bool` | `False` | Eliminar coleccion existente antes de indexar |
| `config` | `AppConfig` | requerido | Configuracion de conexion |

### `extract_relevant_tables_from_vector_db(...) -> list`

Busca tablas semanticamente relevantes para una consulta.

| Parametro | Tipo | Default | Descripcion |
|---|---|---|---|
| `request` | `str` | requerido | Pregunta en lenguaje natural |
| `storage_path` | `str` | `"./metadata_vdb"` | Ruta de la base vectorial |
| `limit` | `int` | `3` | Maximo de tablas a retornar |
| `config` | `AppConfig` | requerido | Configuracion |

## Estrategia tecnica

1. **Conexion**: Se conecta a la BD usando la URL proporcionada con drivers nativos (psycopg2, pymysql, sqlite3, pyodbc).

2. **Extraccion de esquema**: Consulta `information_schema.columns` (PostgreSQL, MySQL, SQL Server) o `PRAGMA table_info` (SQLite) para obtener tablas, columnas y tipos de datos.

3. **Vectorizacion**: Cada tabla se convierte en un bloque semantico y se indexa con ChromaDB usando el modelo `all-MiniLM-L6-v2` de SentenceTransformer.

4. **Busqueda**: Ante una pregunta del usuario, se buscan las tablas mas relevantes por similitud semantica y se retornan como contexto para el LLM.

## Licencia

[Apache License 2.0](LICENSE)
