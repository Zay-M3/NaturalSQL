from typing import Dict

def build_prompt(relevant_tables : list, user_question : str, db_type : str) -> str:
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

def prompt_query(question : str, query_response : Dict[list, list]) -> str:
    
    columns = query_response["columns"]
    rows = query_response["rows"]

    data_sample = [dict(zip(columns, row)) for row in rows[:10]]
    
    prompt = f"""
    You are a business-focused data analyst.

    Context:
    - User question: "{question}"
    - SQL result (sample):
    {data_sample}

    Goal:
    Deliver a clear, direct, and actionable response for business decision-making.

    Mandatory rules:
    1. Do not use emojis.
    2. Do not add observations, side notes, or warnings outside the main answer.
    3. If data exists:
        - First, provide a concise summary of the key insights derived from the data (3-4 sentences max).
        - Second, present a Markdown table with relevant columns.
        - Then provide 2 to 4 concrete business insights based only on the data only if applicable.
        - Close with one actionable recommendation in a single sentence if is needed of other mode not.
    4. If no data exists:
        - State in one sentence that no results were found.
        - Suggest one action to refine the query (filter, date range, or segment).
    5. Keep a professional, concise, and no-fluff tone.
    6. Do not invent data or assumptions not present in the SQL result.
    7. Respond in the same language used by the user.
    """
    return prompt