import urllib.request as url
import database

menu = """
Lista de comandos:

1- !ip-usuario-password                       - Pedir IP de Servidor          
2- !passwd-usuario-old_password-new_password  - Cambiar Password de Usuario:   
"""

commands: list = [
    '!ip', '!passwd', "!commands"
]

# reponse handler


def get_response(user_input: str) -> str:
    incoming: list = user_input.split('-')
    command: str = incoming[0]
    if command in commands:
        if command == "!commands":
            return menu

        # IP command handler
        if command == "!ip" and user_verifiction(incoming):
            return url.urlopen("https://ident.me").read().decode("utf8")
        elif command == "!ip" and user_verifiction(incoming) == False:
            return "User not found"

            # Password Chager command handler
        if command == "!passwd" and user_verifiction(incoming):
            if database.change_password(incoming[1], incoming[3]):
                return "Password changed successfuly"
            else:
                return "Error changing passowrd"


def user_verifiction(message: list) -> bool:
    if message[0] == "!ip":
        return database.verify_sql_user(message[1], message[2])
    return False
