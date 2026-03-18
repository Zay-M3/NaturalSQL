def build_prompt(relevant_tables, user_question):
    """En esta función se construye el prompt para la IA, utilizando las tablas relevantes encontradas en la base de datos vectorial y la pregunta del usuario. El prompt sigue una estructura clara que incluye el esquema de la base de datos, las reglas para generar la consulta SQL, y la pregunta del usuario, lo que ayuda a la IA a generar una consulta SQL precisa y relevante.
    
    Args:
        relevant_tables (list): Lista de tablas relevantes para la pregunta del usuario, obtenidas de la base de datos vectorial.
        user_question (str): La pregunta del usuario para la cual se desea generar una consulta SQL.
        
    Returns:
        str: El prompt formateado para la IA, listo para ser utilizado en la generación de la consulta SQL.
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