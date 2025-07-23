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
    """Create a reusable HTTP session"""
    global session
    if session is None or session.closed:
        timeout = ClientTimeout(total=30)
        session = ClientSession(timeout=timeout)
    return session


async def close_session():
    """Safely close the HTTP session"""
    global session
    if session and not session.closed:
        try:
            await session.close()
        except Exception as e:
            print(f"Error closing session: {e}")


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
                print(f"Error logging in: {await response.json()}")
    except Exception as e:
        print(f"Error in get_token: {e}")


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
        print(f"Error in get_playlists: {e}")
        return []


async def get_playlist_songs(playlist_id: str):
    """
    Gets the songs from a specific playlist
    """
    try:
        if token is None:
            await get_token()

        headers = {"Authorization": f"Bearer {token}"}
        session = await get_session()
        async with session.get(f"{API_URL}/api/playlists/songs?id={playlist_id}", headers=headers) as response:
            if response.status == 200:
                data = await response.json()

                # Extract only the YouTube IDs from the songs
                youtube_ids = []

                # Check if data is a list of songs or a full playlist object
                if isinstance(data, dict) and 'songs' in data:
                    # It's a full playlist object
                    songs = data['songs']
                elif isinstance(data, list):
                    # It's directly a list of songs
                    songs = data
                else:
                    return []

                # Extract the YouTube IDs
                for song in songs:
                    if isinstance(song, dict):
                        youtube_id = song.get('youtube_id') or song.get(
                            'youtubeId') or song.get('id')
                        if youtube_id:
                            youtube_ids.append(youtube_id)

                return youtube_ids
            else:
                print(
                    f"Error getting playlist songs: {response.status}")
                return []
    except Exception as e:
        print(f"Error in get_playlist_songs: {e}")
        return []
