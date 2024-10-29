import urllib.request as url
import database

menu = """
Pedir IP de Servidor:
!ip-usuario-password 

Cambiar Password de Usuario:
!passwd-usuario-old_password-new_password    
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


def user_verifiction(incoming: list) -> bool:
    if incoming[0] == "!ip":
        return database.verify_sql_user(incoming[1], incoming[2])
    return False
