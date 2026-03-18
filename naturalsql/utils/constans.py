CONNECTION_QLS = {
    "postgresql": "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
    "mysql": "mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
    "sqlite": "sqlite:///{database}",
    "sqlserver": "mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server",
}

IGNORE_TABLE = {
    # Migraciones/versionado
    "alembic_version",
    "django_migrations",
    "schema_migrations",
    "flyway_schema_history",
    "__efmigrationshistory",

    # Task queues / jobs
    "celery",
    "celery_taskmeta",
    "celery_tasksetmeta",

    # Tablas comunes de vector stores (no relevantes para SQL de negocio)
    "langchain_pg_collection",
    "langchain_pg_embedding",
    "vector_store",
    "embeddings",

    # Metadata/tuning internas
    "sqlite_sequence",
}

# Alias de compatibilidad para codigo existente.
IGNORE_TABLES = IGNORE_TABLE
