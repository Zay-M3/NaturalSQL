# NaturalSQL

En este repositorio se plantea estudiar el desarrollo de un RGA para bases de datos. El objetivo es crear un sistema que permita extraer el esquema de tu base de datos y formatearlo por tablas. Una vez hecho eso, se pasará a un modelo local que lo transformará en una cadena de vectores para una base de datos vectorial (Pinecone, Milvus, Weaviate o Chroma).

Problema: necesito interactuar con mi base de datos usando un LLM, pero muchas librerías, aunque disponen de esta funcionalidad, contienen funciones adicionales que las hacen pesadas para proyectos pequeños.

Objetivo: convertir bases de datos en bases de datos vectoriales para que los modelos puedan tener contexto al momento de realizar consultas.

### Soporte motores SQL
- SQLServer
- PostgreSQL
- MySQL
- SQLite

## Estrategia

#### Conexión a la base de datos

Dentro del módulo SQL en app, se instancia una clase para realizar la conexión a la base de datos. Esta se determina por una URL en un archivo .env, lo cual permite conectarse a distintos motores de bases de datos mediante dependencias como psycopg2 y pymysql.

```python
return psycopg2.connect(
    host=parsed.hostname,
    port=parsed.port or 5432,
    user=unquote(parsed.username or ""),
    password=unquote(parsed.password or ""),
    dbname=parsed.path.lstrip("/"),
)
```

Dentro de esta misma clase también se incluye la función para la desconexión de la base de datos.


#### Schema de la base de datos

Mediante una consulta de información a la base de datos, extraemos el esquema usando **information_schema**, lo cual retorna tablas, columnas y tipos.

```sql
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
```

Esta consulta se formatea y se guarda en un diccionario.

Después usamos la función **formated_for_ia** para adaptar dicho diccionario para la IA. Esto se logra separando la información por tablas y construyendo un contenido que incluye sus columnas y tipos de datos.

De este modo creamos una lista de documentos, es decir, bloques semánticos por cada tabla de la base de datos.

```python
formatted = []
for table, columns in schema.items():
    column_descriptions = ", ".join(f"{col} ({dtype})" for col, dtype in columns) # Separamos el apartado por las "," que nos indica las tablas, col (Columna) dtypo (Tipo de dato)
    # Creamos un bloque semántico por cada tabla
    doc = f"Table name: {table}. It has the following columns: {column_descriptions}"
    formatted.append(doc)

return formatted
```

#### Vectorizar la base de datos

Para vectorizar la base de datos, usamos el resultado de la función anterior, que formatea el esquema separado por tablas. Añadimos la capa controllers para el manejo de la lógica de este proceso. Para facilitarlo, se delega el trabajo en la librería **ChromaDB**, que permite crear y gestionar una base de datos vectorial para almacenar embeddings y realizar búsquedas semánticas. Lee más en la documentación de Sentence Transformer.

[Documentación ChromaDB - Sentence Transformer](https://docs.trychroma.com/integrations/embedding-models/sentence-transformer)

Usamos la función Sentence Transformer con el modelo recomendado en la documentación: **all-MiniLM-L6-v2**. Este corre de forma local y genera una base de datos que se guardará en [metadata_vdb](/metadata_vdb/). Para ello, primero definimos el cliente y la ruta a utilizar. Esto se puede configurar desde .env; otros parámetros como *device* y *normalize_embedding* también pueden modificarse allí.

- device: define dónde se ejecuta el modelo; tiene dos valores, por defecto: *cpu* y *cuda*.
- normalize_embeddings: es de tipo booleano; permite pedirle al modelo vectores normalizados de tamaño 1. Recomendado: **TRUE**.

```python
self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2",
    normalize_embeddings=self.config.db_normalize_embeddings,
    device=self.config.device
)
```
Indexamos las tablas usando **index_tables**, donde usamos el parámetro que retorna las tablas separadas para rellenar nuestra base de datos vectorial. Después usamos el método **search_relevant_tables**, que mediante la función query permite buscar por índices vectoriales y similitud entre la pregunta del usuario y la base vectorial. Esto retorna 3 posibles opciones, que serán el contexto de la llamada al modelo LLM.












