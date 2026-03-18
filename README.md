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

### Ejemplo completo con un LLM (Groq)

```python
from naturalsql import NaturalSQL
from naturalsql.utils.prompt import build_prompt
from groq import Groq

GROQ_API_KEY = "tu_api_key"

nsql = NaturalSQL(
    db_url="postgresql://user:pass@localhost:5432/mydb",
    db_type="postgresql",
)

nsql.build_vector_db(forced_reset=True)

question = "What is the first user to register?"
tables = nsql.search(question)

prompt = build_prompt(tables, question)

client = Groq(api_key=GROQ_API_KEY)
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
)
print(response.choices[0].message.content)
```

## API

### `NaturalSQL(**kwargs)`

Crea una instancia con la configuracion de conexion y embeddings.

| Parametro | Tipo | Default | Descripcion |
|---|---|---|---|
| `db_url` | `str \| None` | `None` | URL de conexion a la BD |
| `db_type` | `str` | `""` | Motor: `postgresql`, `mysql`, `sqlite`, `sqlserver` |
| `db_normalize_embeddings` | `bool` | `True` | Normalizar vectores de embeddings |
| `device` | `str` | `"cpu"` | Dispositivo: `cpu` o `cuda` |

### `nsql.build_vector_db(...) -> dict`

Conecta a la BD, extrae el esquema y lo indexa en ChromaDB.

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

3. **Vectorizacion**: Cada tabla se convierte en un bloque semantico y se indexa con ChromaDB usando el modelo `all-MiniLM-L6-v2` de SentenceTransformer.

4. **Busqueda**: Ante una pregunta del usuario, se buscan las tablas mas relevantes por similitud semantica (distancia <= 0.8) y se retornan como contexto para el LLM.

5. **Cache**: El modelo de embeddings se carga una sola vez por instancia de `NaturalSQL`. Las busquedas posteriores reutilizan la instancia en memoria (~10-15ms vs ~2-5s).

## Licencia

[Apache License 2.0](LICENSE)
