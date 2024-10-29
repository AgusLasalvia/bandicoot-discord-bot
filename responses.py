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
        if command == "!ip" and database.verify_sql_user(incoming[1], incoming[2]):
            return url.urlopen("https://ident.me").read().decode("utf8")

        elif command == "!ip" and database.verify_sql_user(incoming[1], incoming[2]) == False:
            return "User not found"

        # Password Chager command handler
        if command == "!passwd" and database.verify_sql_user(incoming[1], incoming[2]):
            if database.change_password(incoming[1], incoming[3]):
                return "Password changed successfuly"
            else:
                return "Error changing passowrd"


