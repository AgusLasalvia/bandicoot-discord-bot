import urllib.request as url
from . import database

menu = """
!commands - Show this menu
!passwd <username>-<old_password>-<new_password> - Change your password
!play <url> - Play audio from the given URL
!stop - Stop playing audio and disconnect the bot
"""

commands: list = [
		'!ip', '!passwd', "!commands"
]

# reponse handler
def get_response(user_input: str):
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

				# Password Changer command handler
				if command == "!passwd" and database.verify_sql_user(incoming[1], incoming[2]):
						if database.change_password(incoming[1], incoming[3]):
								return "Password changed successfully"
						else:
								return "Error changing password"
		else:
			return "Command not recognized"
