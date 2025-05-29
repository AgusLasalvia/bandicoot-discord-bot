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


conn = pymysql.connect(
    host=HOST,
    user=USER,
    password=str(PASSWORD),
    database=DATABASE,
    port=int(PORT)
) #pyright:ignore

cursor = conn.cursor()


def verify_sql_user(username: str, password: str) -> bool:
    cursor.execute(
        f"SELECT * FROM User WHERE username='{username}' AND password='{password}';")
    response = list(cursor.fetchall())
    print(response)
    if len(response) > 0:
        return True
    return False


def change_password(username: str, new_passowrd: str) -> bool:
    cursor.execute(
        f"UPDATE User SET password = '{new_passowrd}' WHERE username='{username}'")
    conn.commit()
    return verify_sql_user(username, new_passowrd)
