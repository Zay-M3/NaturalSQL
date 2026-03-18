from naturalsql.controller.controllervector import VectorManager
from naturalsql.sql.sqlconecctions import Connection
from naturalsql.sql.sqlschema import SQLSchemaExtractor
from naturalsql.utils.config import AppConfig


def set_config(
    *,
    api_key_llm: str | None = None,
    db_url: str | None = None,
    db_type: str = "",
    db_normalize_embeddings: bool = True,
    device: str = "cpu",
) -> AppConfig:
    """Crea y retorna una instancia de AppConfig con la configuracion proporcionada.

    Args:
        api_key_llm: API key para el modelo LLM (opcional, no usado internamente por la libreria).
        db_url: URL de conexion a la base de datos (e.g. postgresql://user:pass@host:port/db).
        db_type: Tipo de motor de base de datos (postgresql, mysql, sqlite, sqlserver).
        db_normalize_embeddings: Si se normalizan los embeddings vectoriales.
        device: Dispositivo para el modelo de embeddings (cpu o cuda).

    Returns:
        AppConfig: Instancia de configuracion inmutable.
    """
    return AppConfig(
        api_key_llm=api_key_llm,
        db_url=db_url,
        db_type=(db_type or "").strip().lower(),
        db_normalize_embeddings=bool(db_normalize_embeddings),
        device=(device or "cpu").strip().lower(),
    )


def build_vector_db_from_url(
    storage_path: str = "./metadata_vdb",
    forced_reset: bool = False,
    config: AppConfig | None = None,
) -> dict:
    """Construye e indexa la base vectorial a partir de una URL de base de datos.

    Conecta a la base de datos, extrae el esquema de tablas y columnas,
    y lo indexa en una base de datos vectorial ChromaDB para busquedas semanticas.

    Args:
        storage_path: Ruta donde se almacena la base vectorial.
        forced_reset: Si es True, elimina la coleccion existente antes de indexar.
        config: Instancia de AppConfig con la configuracion de conexion.

    Returns:
        dict: Diccionario con 'storage_path' y 'indexed_documents' (cantidad de tablas indexadas).

    Raises:
        ValueError: Si config es None.
    """
    if config is None:
        raise ValueError("build_vector_db_from_url requiere una instancia de AppConfig en config.")

    conn = Connection.from_config(config)
    conn.connect()

    try:
        schema_extractor = SQLSchemaExtractor(conn.connection, db_type=config.db_type)
        schema = schema_extractor.extract_schema()
        formatted_schema = schema_extractor.formated_for_ia(schema)

        vector_manager = VectorManager(
            storage_path=storage_path,
            force_reset=forced_reset,
            config=config,
        )
        vector_manager.index_tables(formatted_schema)

        return {
            "storage_path": storage_path,
            "indexed_documents": len(formatted_schema),
        }

    finally:
        conn.disconnect()


def extract_relevant_tables_from_vector_db(
    request: str,
    storage_path: str = "./metadata_vdb",
    limit: int = 3,
    config: AppConfig | None = None,
) -> list:
    """Extrae las tablas relevantes para una solicitud dada desde la base vectorial.

    Busca en la base vectorial las tablas cuyo esquema sea semanticamente
    similar a la solicitud del usuario.

    Args:
        request: Pregunta o solicitud en lenguaje natural.
        storage_path: Ruta donde se almacena la base vectorial.
        limit: Numero maximo de tablas a retornar.
        config: Instancia de AppConfig con la configuracion.

    Returns:
        list: Lista de descripciones de tablas relevantes.

    Raises:
        ValueError: Si config es None.
    """
    if config is None:
        raise ValueError("extract_relevant_tables_from_vector_db requiere una instancia de AppConfig en config.")

    vector_manager = VectorManager(
        storage_path=storage_path,
        force_reset=False,
        config=config,
    )
    relevant_tables = vector_manager.search_relevant_tables(request, limit=limit)

    return relevant_tables
