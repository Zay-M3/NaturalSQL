import re

# This class provides methods for cleaning and executing SQL queries, with restrictions on the type of
# queries allowed.
class QuerysConsult:
    
    def __init__(self, connection):
        self.connection = connection

    def clean_sql(self, raw_query):
        """
        The function `clean_sql` removes comments and unnecessary whitespace from a raw SQL query
        string.
        
        :param raw_query: The `clean_sql` function is used to clean up a raw SQL query by removing any
        comments and unnecessary whitespace. The function uses regular expressions to achieve this
        :return: The `clean_sql` function returns the cleaned SQL query after removing any code blocks
        (delimited by ```), single-line comments (starting with --), and multi-line comments (enclosed
        within /* */). Additionally, it removes any extra whitespace by joining the lines and stripping
        any leading or trailing spaces.
        """
        sql = re.sub(r"```sql|```", "", raw_query, flags=re.IGNORECASE)
        
        
        sql = re.sub(r"--.*?\n", " ", sql)
        sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
        
        
        sql = " ".join(sql.split())
        
        return sql.strip()

    def execute_query(self, query):
        """
        The function `execute_query` validates and executes a SQL query, allowing only SELECT statements
        and preventing forbidden keywords.
        
        :param query: The provided code snippet is a method for executing SQL queries with certain
        restrictions in place to prevent potentially harmful operations. The method ensures that the
        query is a SELECT statement, does not contain forbidden keywords (such as INSERT, UPDATE,
        DELETE, etc.), and does not have multiple statements in a single query
        :return: The `execute_query` method returns a tuple containing two elements: `columns` and
        `rows`. If the query is successfully executed and returns results, `columns` will be a list of
        column names and `rows` will be a list of rows fetched from the query result. If the query does
        not return any results, both `columns` and `rows` will be `None`.
        """
        sql = self.clean_sql(query)

        if not sql:
            raise ValueError("the query is empty")

        
        if ";" in sql.rstrip(";"):
            raise ValueError("Is not allowed multiple statements in a single query.")

       
        if not re.match(r"^SELECT\b", sql, re.IGNORECASE):
            raise ValueError("Only SELECT queries are allowed.")
        
        forbidden = [r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b", 
                     r"\bALTER\b", r"\bTRUNCATE\b", r"\bCREATE\b", r"\bREPLACE\b"]
        
        for pattern in forbidden:
            if re.search(pattern, sql, re.IGNORECASE):
                raise ValueError(f"Forbidden keyword detected: {pattern}")

        cursor = self.connection.cursor()
        try:
            cursor.execute(sql)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return columns, rows
            return None, None
        finally:
            cursor.close()
