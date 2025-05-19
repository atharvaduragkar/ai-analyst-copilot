import pandas as pd
import sqlite3

def run_query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})
