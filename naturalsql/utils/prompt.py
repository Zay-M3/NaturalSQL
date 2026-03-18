def build_prompt(relevant_tables, user_question):
    """Construye el prompt para la IA utilizando las tablas relevantes y la pregunta del usuario.

    Args:
        relevant_tables: Lista de tablas relevantes obtenidas de la base de datos vectorial.
        user_question: Pregunta del usuario para la cual se desea generar una consulta SQL.

    Returns:
        str: Prompt formateado para la IA.
    """
    context = "\n\n".join(relevant_tables)

    prompt = f"""
    You are an expert SQL assistant. Use the following database schema to write a SQL query.

    ### Schema:
    {context}

    ### Rules:
    - Only return the SQL query, no explanations.
    - Use the table and column names exactly as defined in the schema.

    ### Question:
    {user_question}

    ### SQL Query:
    """
    return prompt
