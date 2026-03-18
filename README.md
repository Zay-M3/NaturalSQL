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

```python
formatted = []
for table, columns in schema.items():
    column_descriptions = ", ".join(f"{col} ({dtype})" for col, dtype in columns) # Separamos el apartado por las "," que nos indica las tablas, col (Columna) dtypo (Tipo de dato)
    formatted.append(f"{table}: {column_descriptions}")
```











