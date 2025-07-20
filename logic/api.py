import os
import asyncio
from aiohttp import ClientSession, ClientTimeout
import dotenv

dotenv.load_dotenv()

API_URL = os.getenv("API_URL")
BOT_USERNAME = os.getenv("BOT_USERNAME")
BOT_PASSWORD = os.getenv("BOT_PASSWORD")

token = None
session = None


async def get_session():
    """Crear una sesión HTTP reutilizable"""
    global session
    if session is None or session.closed:
        timeout = ClientTimeout(total=30)
        session = ClientSession(timeout=timeout)
    return session


async def close_session():
    """Cerrar la sesión HTTP de forma segura"""
    global session
    if session and not session.closed:
        try:
            await session.close()
        except Exception as e:
            print(f"Error al cerrar sesión: {e}")


async def get_token():
    global token
    try:
        session = await get_session()
        payload = {"username": BOT_USERNAME, "password": BOT_PASSWORD}
        async with session.post(f"{API_URL}/api/auth/login", json=payload) as response:
            if response.status == 200:
                data = await response.json()
                token = data.get("token")
            else:
                print(f"Error al loguear: {await response.json()}")
    except Exception as e:
        print(f"Error en get_token: {e}")


async def get_playlists():
    try:
        if token is None:
            await get_token()
        headers = {"Authorization": f"Bearer {token}"}
        session = await get_session()
        async with session.get(f"{API_URL}/api/playlists/names", headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []
    except Exception as e:
        print(f"Error en get_playlists: {e}")
        return []


async def get_playlist_songs(playlist_id: str):
    """
    Obtiene las canciones de una playlist específica
    """
    try:
        if token is None:
            await get_token()

        headers = {"Authorization": f"Bearer {token}"}
        session = await get_session()
        async with session.get(f"{API_URL}/api/playlists/songs?id={playlist_id}", headers=headers) as response:
            if response.status == 200:
                data = await response.json()

                # Extraer solo los IDs de YouTube de las canciones
                youtube_ids = []

                # Verificar si data es una lista de canciones o un objeto playlist completo
                if isinstance(data, dict) and 'songs' in data:
                    # Es un objeto playlist completo
                    songs = data['songs']
                elif isinstance(data, list):
                    # Es directamente una lista de canciones
                    songs = data
                else:
                    return []

                # Extraer los IDs de YouTube
                for song in songs:
                    if isinstance(song, dict):
                        youtube_id = song.get('youtube_id') or song.get(
                            'youtubeId') or song.get('id')
                        if youtube_id:
                            youtube_ids.append(youtube_id)

                return youtube_ids
            else:
                print(
                    f"Error al obtener canciones de playlist: {response.status}")
                return []
    except Exception as e:
        print(f"Error en get_playlist_songs: {e}")
        return []
