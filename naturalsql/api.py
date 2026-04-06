from typing import TYPE_CHECKING, Literal

from naturalsql.sql.sqlconecctions import Connection
from naturalsql.sql.sqlschema import SQLSchemaExtractor
from naturalsql.utils.config import AppConfig

if TYPE_CHECKING:
    from naturalsql.controller.controllervector import VectorManager


class NaturalSQL:
    """Clase principal de la libreria NaturalSQL.

    Encapsula la configuracion, la construccion de la base vectorial
    y la busqueda de tablas relevantes por lenguaje natural.

    Uso tipico::

        from naturalsql import NaturalSQL

        nsql = NaturalSQL(
            db_url="postgresql://user:pass@host:5432/mydb",
            db_type="postgresql",
        )

        result = nsql.build_vector_db()
        tables = nsql.search("customers who made purchases")
    """

    COMBINATION_REQUIREMENTS = {
        ("chroma", "local"): {
            "extra": "chroma-local",
            "imports": ("chromadb", "sentence_transformers"),
            "missing": ("chromadb", "sentence-transformers"),
        },
        ("sqlite", "local"): {
            "extra": "sqlite-local",
            "imports": ("sentence_transformers",),
            "missing": ("sentence-transformers",),
        },
        ("sqlite", "gemini"): {
            "extra": "sqlite-gemini",
            "imports": ("google.genai",),
            "missing": ("google-genai",),
        },
        ("chroma", "gemini"): {
            "extra": "chroma-gemini",
            "imports": ("chromadb", "google.genai"),
            "missing": ("chromadb", "google-genai"),
        },
    }
    SUPPORTED_COMBINATIONS = frozenset(COMBINATION_REQUIREMENTS)

    def __init__(
        self,
        *,
        db_url: str | None = None,
        db_type: str = "",
        db_normalize_embeddings: bool = True,
        device: str = "cpu",
        vector_backend: Literal["chroma", "sqlite"] = "chroma",
        embedding_provider: Literal["local", "gemini"] = "local",
        gemini_api_key: str | None = None,
        gemini_embedding_model: str = "gemini-embedding-2-preview",
        vector_distance_threshold: float = 1.0,
    ) -> None:
        """Crea una instancia de NaturalSQL con la configuracion proporcionada.

        Args:
            db_url: URL de conexion a la base de datos (e.g. postgresql://...).
            db_type: Tipo de motor de base de datos (postgresql, mysql, sqlite, sqlserver).
            db_normalize_embeddings: Si se normalizan los embeddings vectoriales.
            device: Dispositivo para el modelo de embeddings (cpu o cuda).
            vector_backend: Backend para vectores ("chroma" o "sqlite").
            embedding_provider: Proveedor de embeddings ("local" o "gemini").
            gemini_api_key: API key para Google Gemini (requerido si provider="gemini").
            gemini_embedding_model: Modelo de embeddings de Gemini a usar.
            vector_distance_threshold: Umbral maximo de distancia para filtrar
                tablas relevantes en la busqueda vectorial.
        """
        # 1. Normalize inputs
        vector_backend = vector_backend.strip().lower()
        embedding_provider = embedding_provider.strip().lower()

        # 2. Validate supported combinations
        if (vector_backend, embedding_provider) not in self.SUPPORTED_COMBINATIONS:
            raise ValueError(
                f"Combinacion no soportada: ({vector_backend}, {embedding_provider}). "
                f"Soportadas: {self.SUPPORTED_COMBINATIONS}"
            )

        # 3. Validate API key availability
        if embedding_provider == "gemini" and not gemini_api_key:
            raise ValueError("gemini_api_key es requerido cuando embedding_provider='gemini'")
        if embedding_provider != "gemini" and gemini_api_key:
            raise ValueError("gemini_api_key solo debe enviarse cuando embedding_provider='gemini'")

        # 4. Validate retrieval threshold
        if not isinstance(vector_distance_threshold, (int, float)):
            raise ValueError("vector_distance_threshold debe ser numerico (int o float).")
        if vector_distance_threshold <= 0:
            raise ValueError("vector_distance_threshold debe ser mayor que 0.")

        # 5. Validate dependencies for the selected combination
        self._validate_dependencies(vector_backend, embedding_provider)

        self.config = AppConfig(
            db_url=db_url,
            db_type=(db_type or "").strip().lower(),
            db_normalize_embeddings=bool(db_normalize_embeddings),
            device=(device or "cpu").strip().lower(),
            vector_backend=vector_backend,
            embedding_provider=embedding_provider,
            gemini_api_key=gemini_api_key,
            gemini_embedding_model=gemini_embedding_model,
            vector_distance_threshold=float(vector_distance_threshold),
        )

        # Cached VectorManager instance — avoids reloading SentenceTransformer
        # on every search call.  Keyed by (storage_path,).
        self._vector_manager: "VectorManager | None" = None
        self._vm_storage_path: str | None = None

    def _validate_dependencies(
        self,
        backend: Literal["chroma", "sqlite"],
        provider: Literal["local", "gemini"],
    ) -> None:
        """Check if required packages are installed for the selected config."""
        combo = (backend, provider)
        requirements = self.COMBINATION_REQUIREMENTS[combo]

        missing: list[str] = []
        for module_name, package_name in zip(
            requirements["imports"], requirements["missing"],
        ):
            try:
                __import__(module_name)
            except ImportError:
                missing.append(package_name)

        if missing:
            extra_name = requirements["extra"]
            raise ImportError(
                f"Missing dependencies for ({backend}, {provider}): {', '.join(missing)}. "
                f"Install with: pip install \"naturalsql[{extra_name}]\""
            )


    def _get_vector_manager(self, storage_path: str) -> "VectorManager":
        """Return cached VectorManager, creating one if needed."""
        if (
            self._vector_manager is not None
            and self._vm_storage_path == storage_path
        ):
            return self._vector_manager

        from naturalsql.controller.controllervector import VectorManager
        self._vector_manager = VectorManager(
            storage_path=storage_path,
            force_reset=False,
            config=self.config,
        )
        self._vm_storage_path = storage_path
        return self._vector_manager

    def _invalidate_cache(self) -> None:
        """Clear the cached VectorManager so the next call creates a fresh one."""
        self._vector_manager = None
        self._vm_storage_path = None

    def build_vector_db(
        self,
        storage_path: str = "./metadata_vdb",
        forced_reset: bool = False,
    ) -> dict:
        """Construye e indexa la base vectorial a partir de la URL de base de datos.

        Si la base vectorial ya existe en *storage_path* y *forced_reset* es
        ``False``, reutiliza la coleccion existente sin reconectarse a la BD
        ni regenerar embeddings.

        Args:
            storage_path: Ruta donde se almacena la base vectorial.
            forced_reset: Si es True, elimina la coleccion existente y la
                          reconstruye desde cero.

        Returns:
            dict con:
                - ``storage_path``: Ruta de almacenamiento utilizada.
                - ``indexed_documents``: Cantidad de tablas indexadas.
                - ``from_cache``: True si se reutilizo una coleccion existente.

        Raises:
            ValueError: Si db_url no fue proporcionada en el constructor.
        """
        if not self.config.db_url:
            raise ValueError(
                "build_vector_db requiere db_url. "
                "Proporcionala al crear la instancia de NaturalSQL."
            )

        # Invalidate cache when rebuilding so subsequent searches use
        # the fresh collection.
        if forced_reset:
            self._invalidate_cache()

        from naturalsql.controller.controllervector import VectorManager
        if not forced_reset:
            existing_count = VectorManager.collection_exists(storage_path)
            if existing_count > 0:
                return {
                    "storage_path": storage_path,
                    "indexed_documents": existing_count,
                    "from_cache": True,
                }

        conn = Connection.from_config(self.config)
        conn.connect()

        try:
            extractor = SQLSchemaExtractor(
                conn.connection, db_type=self.config.db_type,
            )
            schema_bundle = extractor.extract_schema()
            documents_payload = extractor.formated_for_ia(schema_bundle)

            vm = VectorManager(
                storage_path=storage_path,
                force_reset=forced_reset,
                config=self.config,
            )
            vm.index_documents(documents_payload)

            # After a forced rebuild, store the new VectorManager in cache
            # so the next search call reuses it immediately.
            self._vector_manager = vm
            self._vm_storage_path = storage_path

            return {
                "storage_path": storage_path,
                "indexed_documents": len(documents_payload),
                "from_cache": False,
            }
        finally:
            conn.disconnect()


    def search(
        self,
        request: str,
        storage_path: str = "./metadata_vdb",
        limit: int = 3,
    ) -> list:
        """Busca tablas relevantes para una solicitud en lenguaje natural.

        Utiliza la base vectorial previamente construida con
        :meth:`build_vector_db`.

        Args:
            request: Pregunta o solicitud en lenguaje natural.
            storage_path: Ruta donde se almacena la base vectorial.
            limit: Numero maximo de tablas a retornar.

        Returns:
            list: Descripciones de tablas relevantes.
        """
        vm = self._get_vector_manager(storage_path)
        return vm.search_relevant_tables(request, limit=limit)
