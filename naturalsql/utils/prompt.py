def build_prompt(relevant_tables, user_question, db_type):
    """
    The function `build_prompt` generates a formatted prompt for an SQL assistant based on relevant
    tables, a user question, and the type of database.
    
    :param relevant_tables: A list of relevant tables in the database schema that are related to the
    user's question
    :param user_question: The `build_prompt` function you provided is a Python function that takes in
    three parameters: `relevant_tables`, `user_question`, and `db_type`. It generates a formatted prompt
    for an SQL assistant based on the provided information
    :param db_type: The `db_type` parameter in the `build_prompt` function represents the type of
    database system being used, such as MySQL, PostgreSQL, SQLite, etc. This information is used to
    customize the prompt message for the specific database system the user is working with
    :return: The function `build_prompt` returns a formatted prompt containing relevant tables, a user
    question, and mandatory instructions for writing a valid SQL query based on the provided schema and
    database type.
    """
        
    context = "\n\n".join(relevant_tables)

    prompt = f"""
    You are an expert SQL {db_type} assistant.

    ## AVAILABLE SCHEMA (SINGLE SOURCE OF TRUTH)
    {context}

    ## USER QUESTION
    {user_question}

    ## MANDATORY INSTRUCTIONS
    1. Return ONLY a valid SQL query; no extra text, no markdown, no comments.
    2. Use ONLY tables and columns that exist in the provided schema.
    3. No DML/DDL allowed: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, REPLACE.
    4. The query must start with SELECT.
    5. If the request is ambiguous, prefer a simple and conservative query using available columns.

    ## EXPECTED OUTPUT
    Raw SQL only.
    """
    
    return prompt