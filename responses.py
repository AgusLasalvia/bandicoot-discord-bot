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
    
    split_message:list = message.split("-")
    print(split_message)
    if split_message[0] == "ip":
        return database.split_message_sql_user(split_message[1],split_message[2])
    return False