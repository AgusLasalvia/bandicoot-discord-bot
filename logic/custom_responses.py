import urllib.request as url
import httpx
from . import database

async def get_ip(username:str,password:str) -> str:
	if database.verify_sql_user(username,password):
		return url.urlopen("https://ident.me").read().decode("utf8")
	return "User not Found"


async def ollama(query:str,model:str = "llama3")->str:
	ollama_url = "http://localhost:11434/api/generate"
	payload = {
		"model":model,
		"prompt":query,
		"stream":False
	}

	try:
		async with httpx.AsyncClient() as client:
			response = await client.post(ollama_url, json=payload)
			response.raise_for_status()
			data = response.json()
			return data.get("response","No response from the model")
	except Exception as e:
		return "Error connecting to the model"
