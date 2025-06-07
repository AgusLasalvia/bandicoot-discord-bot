import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("SQL_HOST")
USER = os.getenv("SQL_USER")
PASSWORD = os.getenv("SQL_PASSWORD")
DATABASE = os.getenv("SQL_DATABASE")
PORT = os.getenv("SQL_PORT")

print(HOST)

def get_connection():
    return pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        port=int(PORT),
        autocommit=True
    )

def verify_sql_user(username: str, password: str) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM User WHERE username=%s AND password=%s", (username, password))
            return cursor.fetchone() is not None


def change_password(username: str, new_passowrd: str) -> bool:
    cursor.execute(
        f"UPDATE User SET password = '{new_passowrd}' WHERE username='{username}'")
    conn.commit()
    return verify_sql_user(username, new_passowrd)
