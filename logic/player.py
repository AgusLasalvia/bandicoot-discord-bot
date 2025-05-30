import discord
import yt_dlp
from collections import deque
import asyncio
from youtubesearchpython import VideosSearch
import re

yt_formats_options = {
    "format": "bestaudio/best",
    "quiet": True,
    "default_search": "auto",
    "noplaylist": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

ffmpeg_options = {
    "options": "-vn -b:a 192k",
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
}

ytdl = yt_dlp.YoutubeDL(yt_formats_options)


class MusicPlayer:
    def __init__(self):
        self.queue = deque()
        self.current_song = None
        self.is_playing = False
        self.voice_client = None
        self.update_now_playing = None  # función callback

    def set_voice_client(self, vc):
        self.voice_client = vc

    def set_update_callback(self, callback):
        self.update_now_playing = callback

    def add_to_queue(self, url: str):
        self.queue.append(url)

    def clear_queue(self):
        self.queue.clear()
        self.current_song = None
        self.is_playing = False

    def get_queue_length(self):
        return len(self.queue)

    async def play_next(self, voice_client):
        if not self.queue or not voice_client:
            self.is_playing = False
            self.current_song = None
            return

        if voice_client.is_playing():
            voice_client.stop()

        try:
            url = self.queue.popleft()
            self.current_song = url
            source = await get_audio_source(url)
            if source:
                # 🔄 Callback para actualizar el mensaje en el canal
                if self.update_now_playing:
                    await self.update_now_playing(url)

                def after_callback(error):
                    if error:
                        print(f"Error in playback: {error}")
                    coro = self.play_next(voice_client)
                    fut = asyncio.run_coroutine_threadsafe(coro, voice_client.loop)
                    try:
                        fut.result()
                    except:
                        pass

                voice_client.play(source, after=after_callback)
                self.is_playing = True
            else:
                await self.play_next(voice_client)
        except Exception as e:
            print(f"Error playing next song: {e}")
            await self.play_next(voice_client)


async def search_video_url(filter_text):
    try:
        search = VideosSearch(str(filter_text), limit=1).result()['result'][0]['link']
        print(f"🔍 URL encontrada: {search}")
        return search
    except Exception as e:
        print(f"Error en search_video_url: {e}")
        return None


async def get_audio_source(url: str):
    try:
        info = ytdl.extract_info(url, download=False)
        url_audio = info["url"] if "url" in info else info["formats"][0]["url"]  # pyright: ignore
        return discord.FFmpegPCMAudio(url_audio, **ffmpeg_options)  # pyright: ignore
    except Exception as e:
        print(f"Error getting audio source: {e}")
        return None


