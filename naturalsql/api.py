from naturalsql.controller.controllervector import VectorManager
from naturalsql.sql.sqlconecctions import Connection
from naturalsql.sql.sqlschema import SQLSchemaExtractor
from naturalsql.utils.config import AppConfig


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

    def __init__(
        self,
        *,
        db_url: str | None = None,
        db_type: str = "",
        db_normalize_embeddings: bool = True,
        device: str = "cpu",
    ) -> None:
        """Crea una instancia de NaturalSQL con la configuracion proporcionada.

        Args:
            db_url: URL de conexion a la base de datos
                    (e.g. postgresql://user:pass@host:port/db).
            db_type: Tipo de motor de base de datos
                     (postgresql, mysql, sqlite, sqlserver).
            api_key_llm: API key para el modelo LLM (opcional, no usado
                         internamente por la libreria).
            db_normalize_embeddings: Si se normalizan los embeddings vectoriales.
            device: Dispositivo para el modelo de embeddings (cpu o cuda).
        """
        self.config = AppConfig(
            db_url=db_url,
            db_type=(db_type or "").strip().lower(),
            db_normalize_embeddings=bool(db_normalize_embeddings),
            device=(device or "cpu").strip().lower(),
        )

        # Cached VectorManager instance — avoids reloading SentenceTransformer
        # on every search call.  Keyed by (storage_path,).
        self._vector_manager: VectorManager | None = None
        self._vm_storage_path: str | None = None

    # ── Private helpers ───────────────────────────────────────────

    def _get_vector_manager(self, storage_path: str) -> VectorManager:
        """Return cached VectorManager, creating one if needed."""
        if (
            self._vector_manager is not None
            and self._vm_storage_path == storage_path
        ):
            return self._vector_manager

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

    # ── Public API ────────────────────────────────────────────────

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
            schema = extractor.extract_schema()
            formatted = extractor.formated_for_ia(schema)

            vm = VectorManager(
                storage_path=storage_path,
                force_reset=forced_reset,
                config=self.config,
            )
            vm.index_tables(formatted)

            # After a forced rebuild, store the new VectorManager in cache
            # so the next search call reuses it immediately.
            self._vector_manager = vm
            self._vm_storage_path = storage_path

            return {
                "storage_path": storage_path,
                "indexed_documents": len(formatted),
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
