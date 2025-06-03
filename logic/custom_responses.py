import re
import httpx
import urllib.request as url
from langdetect import detect
from . import database

async def get_ip(username: str, password: str) -> str:
    """Returns the public IP address if the user is valid in the database."""
    if database.verify_sql_user(username, password):
        return url.urlopen("https://ident.me").read().decode("utf8")
    return "User not found"

async def ollama(query: str) -> str:
    """Sends a prompt to an Ollama model using the /api/generate endpoint."""
    language = detect(query)
    if language == 'es':
        prompt = f"Responde de forma breve y clara:\n{query}"
    else:
        prompt = f"Answer briefly and clearly:\n{query}"

    ollama_url = "http://192.168.68.240:11434/api/generate"
    payload = {
        "model": "deepseek-r1",
        "prompt": prompt,
        "stream": False
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:

        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=payload, headers=headers)


            response.raise_for_status()
            data = response.json()



            if data.get("done_reason") == "load":
                return "The model is still loading. Please try again in a few seconds."


            clean = clean_response(data.get("response",""))
            return clean or "No response received from the model."

    except httpx.HTTPStatusError as http_err:
        return f"HTTP error: {http_err.response.status_code} - {http_err.response.text}"
    except httpx.RequestError as req_err:
        return f"Connection error with Ollama: {str(req_err)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"



def clean_response(text: str) -> str:
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned.strip()
