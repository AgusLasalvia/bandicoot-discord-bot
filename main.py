import os
from typing import Final
from dotenv import load_dotenv
from discord import Intents, Message
from discord.ext import commands
from discord.ext.commands import Context
from responses import get_response
from player import MusicPlayer, get_audio_source


load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")


intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Create music player instance
music_player = MusicPlayer()

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        return
    if is_private := user_message[0] == "?":
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        if (len(response) != 0):
            await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


@bot.event
async def on_ready() -> None:
    print(f"{bot.user} is now running")


@bot.event
async def on_message(message: Message) -> None:
    if message.author == bot.user:
        return
    user_message: str = message.content
    await send_message(message, user_message)
    await bot.process_commands(message)
    
@bot.command(name='play')
async def play(ctx: Context, *, url: str):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to use this command!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    try:
        if not ctx.voice_client:
            voice_client = await voice_channel.connect()
        else:
            voice_client = ctx.voice_client
            
        music_player.add_to_queue(url)
        await ctx.send(f"🎵 Added to queue. Position: {music_player.get_queue_length()}")
        
        if not music_player.is_playing:
            await music_player.play_next(voice_client)
            
    except Exception as e:
        await ctx.send("Could not connect to the voice channel!")
        print(f"Error connecting to voice channel: {e}")
        return

@bot.command(name='skip')
async def skip(ctx: Context):
    if not ctx.voice_client:
        await ctx.send("I'm not playing anything!")
        return
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipping to next song...")
    else:
        await ctx.send("Nothing is playing!")

@bot.command(name='queue')
async def queue(ctx: Context):
    if music_player.get_queue_length() == 0 and not music_player.current_song:
        await ctx.send("Queue is empty")
        return
        
    queue_list = "🎵 **Music Queue:**\n"
    if music_player.current_song:
        queue_list += f"**Now Playing:** {music_player.current_song}\n"
    
    if music_player.get_queue_length() > 0:
        queue_list += "\n**Up Next:**\n"
        for i, song in enumerate(music_player.queue, 1):
            queue_list += f"{i}. {song}\n"
    
    await ctx.send(queue_list)

@bot.command(name='stop')
async def stop(ctx: Context):
    if not ctx.voice_client:
        await ctx.send("I'm not playing anything!")
        return
    
    music_player.clear_queue()
    ctx.voice_client.stop()
    await ctx.voice_client.disconnect()
    await ctx.send("⏹️ Playback stopped and queue cleared")

def main() -> None:
    bot.run(token=TOKEN)


if __name__ == "__main__":
    main()
