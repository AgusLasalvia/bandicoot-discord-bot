import urllib.request as url
import database

menu = """
Lista de comandos:
1- id-usuario-password
2- puto
"""

def get_response(user_input: str) -> str:
    if user_verifiction(user_input):
        return url.urlopen("https://ident.me").read().decode("utf8")
    elif user_input == "puto":
        return "chupala gil"

    return ""


def user_verifiction(message:str) -> bool:
    
    verify:list = message.split("-")
    print(verify)
    if verify[0] == "ip":
        return database.verify_sql_user(verify[1],verify[2])
    return False