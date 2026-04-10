from naturalsql.sql.sqlschema import SQLSchemaExtractor


def test_extract_schema_rejects_unsupported_engine():
    extractor = SQLSchemaExtractor(connection=object(), db_type="oracle")

    try:
        extractor.extract_schema()
    except ValueError as exc:
        message = str(exc)
        assert "Motor no soportado" in message
        assert "postgresql" in message
        assert "mysql" in message
        assert "sqlserver" in message
        assert "sqlite" in message
    else:
        raise AssertionError("Expected ValueError for unsupported engine")


def test_parse_information_schema_columns_groups_and_ignores_internal_tables():
    extractor = SQLSchemaExtractor(connection=object(), db_type="postgresql")

    rows = [
        ("public", "users", "id", "integer"),
        ("public", "users", "email", "text"),
        ("public", "orders", "id", "integer"),
        ("public", "alembic_version", "version_num", "text"),
    ]

    result = extractor._parse_information_schema_columns(rows)

    assert set(result.keys()) == {"public.users", "public.orders"}
    assert result["public.users"] == {
        "schema": "public",
        "table": "users",
        "columns": [("id", "integer"), ("email", "text")],
    }
    assert result["public.orders"]["columns"] == [("id", "integer")]


def test_parse_relationship_rows_normalizes_schema_and_ignores_internal_tables():
    extractor = SQLSchemaExtractor(connection=object(), db_type="postgresql")

    rows = [
        (None, "orders", "user_id", None, "users", "id"),
        ("public", "users", "id", "public", "alembic_version", "version_num"),
    ]

    result = extractor._parse_relationship_rows(rows)

    assert result == [
        {
            "from_schema": "main",
            "from_table": "orders",
            "from_column": "user_id",
            "to_schema": "main",
            "to_table": "users",
            "to_column": "id",
        }
    ]


def test_extract_schema_sqlite_returns_expected_tables_and_relationships():
    import sqlite3

    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
        connection.execute(
            "CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, "
            "FOREIGN KEY(user_id) REFERENCES users(id))"
        )

        extractor = SQLSchemaExtractor(connection=connection, db_type="sqlite")
        result = extractor.extract_schema()

        assert set(result.keys()) == {"tables", "relationships"}
        assert "main.users" in result["tables"]
        assert "main.orders" in result["tables"]
        assert result["tables"]["main.users"]["columns"] == [
            ("id", "INTEGER"),
            ("email", "TEXT"),
        ]
        assert result["tables"]["main.orders"]["columns"] == [
            ("id", "INTEGER"),
            ("user_id", "INTEGER"),
        ]
        assert result["relationships"] == [
            {
                "from_schema": "main",
                "from_table": "orders",
                "from_column": "user_id",
                "to_schema": "main",
                "to_table": "users",
                "to_column": "id",
            }
        ]
    finally:
        connection.close()


def test_formated_for_ia_returns_plain_dictionary_documents():
    extractor = SQLSchemaExtractor(connection=object(), db_type="sqlite")
    schema_bundle = {
        "tables": {
            "main.users": {
                "schema": "main",
                "table": "users",
                "columns": [("id", "INTEGER"), ("email", "TEXT")],
            }
        },
        "relationships": [
            {
                "from_schema": "main",
                "from_table": "orders",
                "from_column": "user_id",
                "to_schema": "main",
                "to_table": "users",
                "to_column": "id",
            }
        ],
    }

    result = extractor.formated_for_ia(schema_bundle)

    assert isinstance(result, list)
    assert len(result) == 2

    table_doc = result[0]
    relationship_doc = result[1]

    assert table_doc == {
        "id": "table::main.users",
        "content": "Schema: main. Table name: users. It has the following columns: id (INTEGER), email (TEXT)",
        "metadata": {
            "kind": "table",
            "schema": "main",
            "table": "users",
        },
    }

    assert relationship_doc == {
        "id": "rel::main.orders.user_id->main.users.id",
        "content": "Relationship: main.orders.user_id -> main.users.id",
        "metadata": {
            "kind": "relationship",
            "from_schema": "main",
            "from_table": "orders",
            "from_column": "user_id",
            "to_schema": "main",
            "to_table": "users",
            "to_column": "id",
        },
    }
