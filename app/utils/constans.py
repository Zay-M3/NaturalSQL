CONNECTION_QLS = {
    "postgresql": "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
    "mysql": "mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
    "sqlite": "sqlite:///{database}",
    "sqlserver": "mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server",
}   