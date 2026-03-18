# NaturalSQL

En ese repositoria se piensa estudiar el desarollo de un RGA para bases de datos, el objetivo es crear un sistema que permita extraer el schema de tu base datos, la formatee para separala por tablas, una vez hecho eso, se pasara a un modelo local el cual la formatea a una cadena de vectores para una bd de datos vectoria (Pinecone, Milvus, Weaviate o Chroma)

Problema, necesito interactuar con mi base datos usando un LLM, pero muchas librerias aunque disponen de esto, contiene funciones adiccionales lo que las hace pesadas para proyectos pequeños

Objetivo, convertir bases de datos en bases de datos vectoriales que los modelos puedan tener conexto al momento de hacer tus consultas.

### Soporte motores SQL
- SQLServer
- PostgreSQL
- MySQL
- SQLite

## Estrategia

#### Conexion a la base de datos

Dentro de del modulo sql en app, se instancia una clase para realizar la conexion la base datos, determina por una URL en una .env, esto nos permite conectarlos a diversos modelos de bases de datos, esto mediante de dependencias como psycopg2, pymsql

```python
return psycopg2.connect(
    host=parsed.hostname,
    port=parsed.port or 5432,
    user=unquote(parsed.username or ""),
    password=unquote(parsed.password or ""),
    dbname=parsed.path.lstrip("/"),
)
```

dentro de este misma clase, tenemos la funcion para la desconexion de la base datos.


#### Schema de la base de datos

Mediante una consulta de informacion a la base datos, extraemos el schema, usando **information_schema**, esto nos extrae tablas, columnas y tipos

```sql
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
```

Esta consulta la formateamos y guardamos en un diccionario

Siguiente a esto, usamos la funcion **formated_for_ia**, para formatear dicho diccionario para la IA, esto lo logramos separando la informacion de tal manera que viene nos retorno la anterior funciona, la cual separa las tablas por ",", usamoe sto para formaterar el contenido de la siguiente forma, por las tablas de la base datos, lo cual continua de sus columnas y tipos de datos de cada columna

De este modo creamos un diccionario una lista de todos los documentos, bloques semnanticos por cada tabla de la base de datos.

```python
formatted = []
for table, columns in schema.items():
    column_descriptions = ", ".join(f"{col} ({dtype})" for col, dtype in columns) # Separamos el apartado por las "," que nos indica las tablas, col (Columna) dtypo (Tipo de dato)
    # Creamos un bloque semántico por cada tabla
    doc = f"Table name: {table}. It has the following columns: {column_descriptions}"
    formatted_docs.append(doc)

    return formatted
```

#### Vectorizar la base de datos

Para vectorizar la base de datos, usamos el resultado de la funcion antes vista, que formatea el producto en un schema separado por tablas. Añadimos la capa controllers para el manejo de la logica para este proceso, para facilitar este proceso, se delega el trabajo a la libreria **Chromadb** ChromaDB es una librería que permite crear y gestionar una base de datos vectorial para almacenar embeddings y realizar búsquedas semánticas. Lease mas en la documentacion sobre Sentence Trasnformer

[Documetacion Chromadb - Sentence Transformer](https://docs.trychroma.com/integrations/embedding-models/sentence-transformer)

Usamos la funcion Setence Transformer con el modelo recomendado en la documentacion **all-MiniLM-L6-v2**, corremos este de forma local, nos generara una bd que se guardara en [metada_vdb](/metadata_vdb/), para esto primero definimos el cliente con la path que se usara, esto se puede modificar desde las .env, otros parametros como *device* y *normalize_embedding* se pueden modificar desde las .env mismamente.

- device : Es donde se ejecuta el modelo, tiene dos valores, default = *cpu* y *cuda*
- normalize_embeddings : Tipo boleano, de esta forma podemos decirle al modelo que necesitamos todos nuestros vectores de tamaño 1. recomendado **TRUE**

```python
self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2",
    normalize_embeddings=self.config.db_normalize_embeddings,
    device=self.config.device
)
```
Indexamos las tablas usando **index_tables**, en la cual nos traemos el parametro posterior donde retornamos las tablas separads por ",", usamos esto para rellenar nuestra db vectorial, ya con esto, usamos el metodo **search_relevant_tables**, el cual mediante la funcion reservada query, nos ayuda a buscar usando indixes vectoriales, similutes entra pregunta del usuario y la bd vectorial, esto nos retorna 3 posibles opciones, las cuales seran el contexto de nuestra llamada a nuestro modelo LLM












