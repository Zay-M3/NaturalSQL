# NaturalSQL

English documentation: [README.md](README.md)

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
    gemini_embedding_model="gemini-embedding-2-preview",
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
| `gemini_embedding_model` | `str` | `"gemini-embedding-2-preview"` | Modelo de embeddings Gemini |
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

## Como Funciona Internamente

Piensa en NaturalSQL como un pipeline de 5 pasos:

1. Leer la estructura de la BD con consultas SQL/sistema simples.
2. Normalizar esa estructura a un diccionario Python comun.
3. Convertir ese diccionario en textos semanticos.
4. Convertir esos textos en vectores (embeddings).
5. Guardar vectores en Chroma o SQLite y recuperar los mejores para RAG.

### 1) Estrategia de extraccion de schema por motor

NaturalSQL no parsea scripts SQL. Le pregunta al motor de BD por metadatos.

- PostgreSQL: `information_schema.columns` para columnas + joins entre `information_schema.table_constraints`, `key_column_usage` y `constraint_column_usage` para llaves foraneas.
- MySQL: `information_schema.columns` e `information_schema.key_column_usage` (filtrando con `DATABASE()`).
- SQL Server: `INFORMATION_SCHEMA.COLUMNS` para columnas + `sys.foreign_key_columns` junto con `sys.tables`, `sys.schemas`, `sys.columns` para relaciones FK.
- SQLite: `sqlite_master` (lista de tablas), `PRAGMA table_info('<tabla>')` para columnas, `PRAGMA foreign_key_list('<tabla>')` para relaciones.

Idea esencial: casi todos usan `information_schema`; SQLite usa `PRAGMA`.

### 2) Diccionario unificado del schema (igual para todos los motores)

Despues de extraer, todo se normaliza a una sola forma:

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

Esto permite que el resto del pipeline sea independiente del motor SQL original.

### 3) Del diccionario a documentos semanticos (para embeddings)

El extractor genera documentos para dos tipos de conocimiento:

- `kind=table`: tabla + columnas + tipos
- `kind=relationship`: direccion de llaves foraneas entre tablas

Ejemplo de item en el payload:

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

Ejemplo para relacion:

```python
{
  "id": "rel::public.orders.user_id->public.users.id",
  "content": "Relationship: public.orders.user_id -> public.users.id",
  "metadata": {
    "kind": "relationship"
  }
}
```

### 4) Generacion de embeddings

NaturalSQL soporta dos proveedores:

- `local`: `sentence-transformers` (`all-MiniLM-L6-v2`)
- `gemini`: `google-genai` (`gemini-embedding-2-preview` por defecto)

El sistema embeddea:

- documentos con modo retrieval-document
- consulta del usuario con modo retrieval-query

Resultado: un vector por documento de schema y un vector por pregunta del usuario.

### 5) Estrategia de almacenamiento vectorial (Chroma vs SQLite)

#### Backend Chroma

- Usa `chromadb.PersistentClient(path=storage_path)`.
- Guarda `ids`, `documents`, `embeddings`, `metadatas` en la coleccion `db_schema`.
- La consulta usa busqueda vectorial nativa + filtro por metadata, por ejemplo `where={"kind": "table"}`.

#### Backend SQLite

- Crea `vectors.db` dentro de `storage_path`.
- Estructura de tabla: `id`, `content`, `embedding` (JSON texto), `metadata_json` (JSON texto).
- En consulta, carga filas y calcula distancia coseno en Python (NumPy si existe, fallback puro Python si no).
- Tambien filtra por `kind` leyendo `metadata_json`.

### 6) Flujo de recuperacion para RAG

Cuando llamas `search("...", limit=N)`, sucede esto:

1. Se embebe la pregunta.
2. Se consulta por separado `kind=table` y `kind=relationship`.
3. Se fusionan ambos resultados.
4. Se ordenan por distancia (menor es mejor).
5. Se aplica `vector_distance_threshold`.
6. Se retornan los mejores `N` contextos para el prompt.

Asi el LLM usa contexto real del schema en vez de adivinar nombres de tablas o columnas.

### 7) Vista minima end-to-end interna

```python
from naturalsql.sql.sqlschema import SQLSchemaExtractor
from naturalsql.controller.controllervector import VectorManager

# 1) extraer
extractor = SQLSchemaExtractor(connection, db_type="postgresql")
schema_bundle = extractor.extract_schema()

# 2) normalizar -> documentos semanticos
documents_payload = extractor.formated_for_ia(schema_bundle)

# 3) embed + persistir (chroma o sqlite segun config)
vm = VectorManager(storage_path="./metadata_vdb", force_reset=False, config=config)
vm.index_documents(documents_payload)

# 4) recuperar para RAG
context_docs = vm.search_relevant_tables("ventas del ultimo mes", limit=3)
```

### Comparativa de backends

| Aspecto | Chroma | SQLite |
|---|---|---|
| Archivos de almacenamiento | Directorio persistente de Chroma | Archivo `vectors.db` |
| Consulta vectorial | Query ANN nativa de Chroma | Distancia coseno en Python |
| Filtro por metadatos | `where` nativo | Filtro leyendo JSON de metadata |
| Dependencias | Requiere `chromadb` | Usa `sqlite3` de stdlib + NumPy opcional |
| Estilo operativo | Comportamiento de vector DB dedicada | Store local embebido y ligero |

### Limitaciones actuales

Estos puntos salen del comportamiento actual de implementacion:

- No hay ranking hibrido todavia: recupera por distancia de embeddings (sin BM25/rerank lexico adicional).
- El texto de relaciones es breve (`A.col -> B.col`), por lo que semantica de negocio compleja no queda explicita.
- En backend SQLite, la similitud se calcula en Python; para volumenes muy grandes puede ser mas lento que motores vectoriales nativos.
- `build_vector_db()` devuelve `indexed_documents` como total de documentos indexados (tablas + relaciones), aunque el wording puede interpretarse como solo tablas.
- La extraccion es estructural (tablas/columnas/FKs). No incorpora por defecto definiciones de negocio, comentarios de catalogo u ontologias curadas, a menos que agregues documentos extra.

En la practica, esto sigue siendo muy util para RAG SQL porque columnas y topologia de llaves foraneas son las senales de contexto mas valiosas para grounding.

## Pruebas

Consulta [test/README.md](test/README.md) para instrucciones de pruebas.

## Licencia

[Apache License 2.0](LICENSE)
