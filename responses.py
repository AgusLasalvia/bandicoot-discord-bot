import urllib.request as url
# import database

menu = """
Lista de comandos:
1- id-usuario-password
2- puto
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
        if command == "!ip" and user_verifiction(user_input):
            return url.urlopen("https://ident.me").read().decode("utf8")
        elif command == "!ip" and user_verifiction(user_input) == False:
            return "User not found"

            # Password Chager command handler
        if command == "!passwd" and user_verifiction(incoming):
            # if database.change_password(incoming[1], incoming[3]):
            # return "Password changed successfuly"
            # else:
            # return "Error changing passowrd"
            pass


def user_verifiction(message: list) -> bool:
    if message[0] == "!ip":
        pass
        # return database.verify_sql_user(message[1], message[2])
    return False
