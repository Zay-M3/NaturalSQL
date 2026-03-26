from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class AppConfig:
    """Configuracion inmutable de la aplicacion.

    Attributes:
        db_url: URL de conexion a la base de datos.
        db_type: Tipo de motor (postgresql, mysql, sqlite, sqlserver).
        db_normalize_embeddings: Si se normalizan los embeddings vectoriales.
        device: Dispositivo para el modelo de embeddings (cpu o cuda).
        vector_backend: Backend vectorial ("chroma", "sqlite").
        embedding_provider: Proveedor de embeddings ("local", "gemini").
        gemini_api_key: API key para Google Gemini (requerido si provider="gemini").
        gemini_embedding_model: Modelo de embeddings de Gemini a usar.
        vector_distance_threshold: Umbral maximo de distancia para considerar
            una tabla como relevante en la busqueda vectorial.
    """
    db_url: str | None
    db_type: str
    db_normalize_embeddings: bool
    device: str
    vector_backend: Literal["chroma", "sqlite"] = "chroma"
    embedding_provider: Literal["local", "gemini"] = "local"
    gemini_api_key: str | None = None
    gemini_embedding_model: str = "models/text-embedding-004"
    vector_distance_threshold: float = 1.0
