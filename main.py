import os
from typing import Final

from dotenv import load_dotenv

from discord import Intents, Message
from discord.ext import commands
from discord.ext.commands import Context

#logic
from logic.responses import get_response
from logic.player import MusicPlayer

#UI
from UI.music_view import MusicControlView


load_dotenv()

TOKEN: Final[str] = str(os.getenv("DISCORD_TOKEN"))

intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Create music player instance
music_player = MusicPlayer()

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        return
    if is_private := user_message[0] == "?":
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        if len(response) != 0:
            await message.author.send(
                response
            ) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


@bot.event
async def on_voice_state_update(member, before, after):
    # Si el bot no está conectado a ningún canal de voz, no hace nada
    voice_client = member.guild.voice_client
    if not voice_client:
        return

    # Verificamos el canal donde está el bot
    voice_channel = voice_client.channel

    # Si alguien salió del canal donde está el bot (antes estaba ahí, ahora no)
    if before.channel == voice_channel and after.channel != voice_channel:
        # Revisar cuántos usuarios quedan en ese canal (excluyendo al bot)
        if len([m for m in voice_channel.members if not m.bot]) == 0:
            # No quedan usuarios humanos, desconectar el bot
            await voice_client.disconnect()
            music_player.clear_queue()
            print(
                f"Bot disconnected from {voice_channel} because the channel is empty."
            )


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


@bot.command(name="skip")
async def skip(ctx: Context):
    if not ctx.voice_client:
        await ctx.send("I'm not playing anything!")
        return

    if ctx.voice_client.is_playing(): #pyright:ignore
        ctx.voice_client.stop() #pyright:ignore
        await ctx.send("⏭️ Skipping to next song...")
    else:
        await ctx.send("Nothing is playing!")


@bot.command(name="queue")
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


@bot.command(name="stop")
async def stop(ctx: Context):
    if not ctx.voice_client:
        await ctx.send("I'm not playing anything!")
        return

    music_player.clear_queue()
    ctx.voice_client.stop() #pyright:ignore
    await ctx.voice_client.disconnect() #pyright:ignore
    await ctx.send("⏹️ Playback stopped and queue cleared")

@bot.command(name="play")
async def play(ctx: Context, *, url: str):
    if not ctx.author.voice:  # pyright:ignore
        await ctx.send("You need to be in a voice channel to use this command!")
        return

    voice_channel = ctx.author.voice.channel  # pyright:ignore

    try:
        if not ctx.voice_client:
            voice_client = await voice_channel.connect()  # pyright:ignore
        else:
            voice_client = ctx.voice_client

        music_player.add_to_queue(url)
        await ctx.send(
            f"🎵 Added to queue. Position: {music_player.get_queue_length()}"
        )

        if not music_player.is_playing:
            await music_player.play_next(voice_client)

        # Aquí creamos la vista y la enviamos con un mensaje interactivo:
        view = MusicControlView(music_player, voice_client, ctx)
        await ctx.send(
            f"🎶 Reproduciendo: {music_player.current_song}",
            view=view
        )

    except Exception as e:
        await ctx.send("Could not connect to the voice channel!")
        print(f"Error connecting to voice channel: {e}")
        return





def main() -> None:
    bot.run(token=TOKEN)


if __name__ == "__main__":
    main()
