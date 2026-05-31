import discord
import yt_dlp
from collections import deque
import asyncio
import random

yt_formats_options = {
    "format": "bestaudio/best",
    "quiet": True,
    "default_search": "auto",
    "noplaylist": True,
    "extract_flat": False,
    "no_warnings": False,
    "extractaudio": True,
    "audioformat": "mp3",
    "audioquality": "192K",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "cookiesfrombrowser": None,
    "extractor_retries": 3,
    "fragment_retries": 3,
    "retries": 3,
    "sleep_interval": 1,
    "max_sleep_interval": 5,
    "sleep_interval_subtitles": 1,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    },
    "extractor_args": {
        "youtube": {
            "skip": ["dash", "hls"],
            "player_skip": ["configs"],
            "comment_sort": ["top"],
            "max_comments": [0],
        }
    }
}

ffmpeg_options = {
    "options": "-vn -b:a 192k",
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
}

ytdl = yt_dlp.YoutubeDL(yt_formats_options)


class SongInfo:
    """Holds metadata for a queued song."""
    def __init__(self, url: str, title: str = None, thumbnail: str = None, duration: int = None):
        self.url = url
        self.title = title or url
        self.thumbnail = thumbnail
        self.duration = duration

    def format_duration(self) -> str:
        if not self.duration:
            return "Unknown"
        minutes, seconds = divmod(self.duration, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


async def fetch_song_info(url: str) -> SongInfo:
    """Fetch title/thumbnail from YouTube without downloading."""
    try:
        loop = asyncio.get_event_loop()
        def _extract():
            opts = {"quiet": True, "noplaylist": True, "skip_download": True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and "entries" in info:
                    info = info["entries"][0]
                return info
        info = await loop.run_in_executor(None, _extract)
        if info:
            return SongInfo(
                url=url,
                title=info.get("title") or url,
                thumbnail=info.get("thumbnail"),
                duration=info.get("duration"),
            )
    except Exception as e:
        print(f"Error fetching song info for {url}: {e}")
    return SongInfo(url=url)


class MusicPlayer:
    def __init__(self):
        self.queue: deque[SongInfo] = deque()
        self.current_song: SongInfo | None = None
        self.is_playing = False
        self.loop = False
        self.shuffle = False
        self.voice_client = None
        self.update_now_playing = None

    def set_voice_client(self, vc):
        self.voice_client = vc

    def set_update_callback(self, callback):
        self.update_now_playing = callback

    def add_to_queue(self, song: SongInfo):
        self.queue.append(song)

    def clear_queue(self):
        self.queue.clear()
        self.current_song = None
        self.is_playing = False

    def get_queue_length(self):
        return len(self.queue)

    def toggle_loop(self) -> bool:
        self.loop = not self.loop
        return self.loop

    def toggle_shuffle(self) -> bool:
        self.shuffle = not self.shuffle
        if self.shuffle:
            queue_list = list(self.queue)
            random.shuffle(queue_list)
            self.queue = deque(queue_list)
        return self.shuffle

    async def play_next(self, voice_client):
        if voice_client.is_playing():
            voice_client.stop()

        # Loop: re-queue the current song before popping the next
        if self.loop and self.current_song:
            self.queue.appendleft(self.current_song)

        if not self.queue or not voice_client:
            self.is_playing = False
            self.current_song = None
            return

        try:
            song = self.queue.popleft()
            self.current_song = song
            source = await get_audio_source(song.url)
            if source:
                if self.update_now_playing:
                    await self.update_now_playing(song)

                def after_callback(error):
                    if error:
                        print(f"Playback error: {error}")
                    if self.queue:
                        coro = self.play_next(voice_client)
                        fut = asyncio.run_coroutine_threadsafe(coro, voice_client.loop)
                        try:
                            fut.result()
                        except Exception:
                            pass
                    else:
                        self.is_playing = False
                        self.current_song = None

                voice_client.play(source, after=after_callback)
                self.is_playing = True
            else:
                await self.play_next(voice_client)
        except Exception as e:
            print(f"Error in play_next: {e}")
            await self.play_next(voice_client)


async def search_video_url(filter_text: str) -> str | None:
    try:
        loop = asyncio.get_event_loop()
        def search():
            with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
                info = ydl.extract_info(f"ytsearch1:{filter_text}", download=False)
                if info and "entries" in info and len(info["entries"]) > 0:
                    return info["entries"][0]["webpage_url"]
                return None
        return await loop.run_in_executor(None, search)
    except Exception as e:
        print(f"Error searching for '{filter_text}': {str(e)}")
        return None


async def get_audio_source(url: str):
    try:
        info = ytdl.extract_info(url, download=False)
        if "url" in info:
            url_audio = info["url"]
        elif "formats" in info and len(info["formats"]) > 0:
            audio_formats = [f for f in info["formats"] if f.get("acodec") != "none"]
            url_audio = audio_formats[0]["url"] if audio_formats else info["formats"][0]["url"]
        else:
            print(f"No valid audio URL found for: {url}")
            return None
        return discord.FFmpegPCMAudio(url_audio, **ffmpeg_options)  # pyright: ignore
    except Exception as e:
        print(f"Error extracting audio from {url}: {str(e)}")
        try:
            fallback_options = {
                "format": "bestaudio[ext=m4a]/bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            }
            fallback_ytdl = yt_dlp.YoutubeDL(fallback_options)
            info = fallback_ytdl.extract_info(url, download=False)
            if "url" in info:
                url_audio = info["url"]
            elif "formats" in info and len(info["formats"]) > 0:
                url_audio = info["formats"][0]["url"]
            else:
                return None
            return discord.FFmpegPCMAudio(url_audio, **ffmpeg_options)  # pyright: ignore
        except Exception as fallback_error:
            print(f"Fallback extraction also failed for {url}: {str(fallback_error)}")
            return None
