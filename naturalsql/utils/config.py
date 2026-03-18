from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Configuracion inmutable de la aplicacion.

    Attributes:
        api_key_llm: API key para el modelo LLM (opcional, no usado internamente).
        db_url: URL de conexion a la base de datos.
        db_type: Tipo de motor (postgresql, mysql, sqlite, sqlserver).
        db_normalize_embeddings: Si se normalizan los embeddings vectoriales.
        device: Dispositivo para el modelo de embeddings (cpu o cuda).
    """

    api_key_llm: str | None
    db_url: str | None
    db_type: str
    db_normalize_embeddings: bool
    device: str
