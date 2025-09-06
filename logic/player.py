import discord
import yt_dlp
from collections import deque
import asyncio
from youtubesearchpython import VideosSearch

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
    # Anti-bot detection measures
    "cookiesfrombrowser": None,
    "extractor_retries": 3,
    "fragment_retries": 3,
    "retries": 3,
    "sleep_interval": 1,
    "max_sleep_interval": 5,
    "sleep_interval_subtitles": 1,
    # User agent and headers to avoid detection
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    },
    # Additional options to handle signature extraction
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


class MusicPlayer:
    def __init__(self):
        self.queue = deque()
        self.current_song = None
        self.is_playing = False
        self.voice_client = None
        self.update_now_playing = None  # callback function

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
                # �� Callback to update the message in the channel
                if self.update_now_playing:
                    await self.update_now_playing(url)

                def after_callback(error):
                    if error:
                        # Only play the next song if there are more in the queue
                        if self.queue:
                            coro = self.play_next(voice_client)
                            fut = asyncio.run_coroutine_threadsafe(
                                coro, voice_client.loop)
                            try:
                                fut.result()
                            except:
                                pass
                        else:
                            self.is_playing = False
                            self.current_song = None
                    else:
                        # Only play the next song if there are more in the queue
                        if self.queue:
                            coro = self.play_next(voice_client)
                            fut = asyncio.run_coroutine_threadsafe(
                                coro, voice_client.loop)
                            try:
                                fut.result()
                            except:
                                pass
                        else:
                            self.is_playing = False
                            self.current_song = None

                voice_client.play(source, after=after_callback)
                self.is_playing = True
            else:
                await self.play_next(voice_client)
        except Exception as e:
            await self.play_next(voice_client)


async def search_video_url(filter_text):
    try:
        search = VideosSearch(str(filter_text), limit=1)
        result = search.result()
        
        if result and 'result' in result and len(result['result']) > 0:
            return result['result'][0]['link']
        else:
            print(f"No search results found for: {filter_text}")
            return None
    except Exception as e:
        print(f"Error searching for '{filter_text}': {str(e)}")
        return None


async def get_audio_source(url: str):
    try:
        # Try to extract info with the updated configuration
        info = ytdl.extract_info(url, download=False)
        
        # Handle different response formats
        if "url" in info:
            url_audio = info["url"]
        elif "formats" in info and len(info["formats"]) > 0:
            # Find the best audio format
            audio_formats = [f for f in info["formats"] if f.get("acodec") != "none"]
            if audio_formats:
                url_audio = audio_formats[0]["url"]
            else:
                url_audio = info["formats"][0]["url"]
        else:
            print(f"No valid audio URL found for: {url}")
            return None

        # pyright: ignore
        return discord.FFmpegPCMAudio(url_audio, **ffmpeg_options)
    except Exception as e:
        print(f"Error extracting audio from {url}: {str(e)}")
        # Try with a fallback configuration if the main one fails
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
                
            return discord.FFmpegPCMAudio(url_audio, **ffmpeg_options)
        except Exception as fallback_error:
            print(f"Fallback extraction also failed for {url}: {str(fallback_error)}")
            return None
