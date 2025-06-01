import os
from typing import Final

from dotenv import load_dotenv

import discord
from discord import app_commands, Intents
from discord.ext import commands

# Logic
from logic.player import MusicPlayer, search_video_url

# UI
from UI.music_view import MusicControlView

load_dotenv()

TOKEN: Final[str] = str(os.getenv("DISCORD_TOKEN"))

intents: Intents = Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix=commands.when_mentioned)
tree = bot.tree
music_player = MusicPlayer()


@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = member.guild.voice_client
    if not voice_client:
        return

    voice_channel = voice_client.channel
    if before.channel == voice_channel and after.channel != voice_channel:
        if len([m for m in voice_channel.members if not m.bot]) == 0:
            await voice_client.disconnect()
            music_player.clear_queue()
            print(f"Bot disconnected from {voice_channel} because the channel is empty.")


@bot.event
async def on_ready() -> None:
    await tree.sync()
    print(f"{bot.user} is now running and slash commands are synced")


@tree.command(name="play", description="Play a song from a URL or search query")
async def play(interaction: discord.Interaction, query: str):
    if not interaction.user.voice:
        await interaction.response.send_message("You need to be in a voice channel to use this command!", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel

    try:
        if not interaction.guild.voice_client:
            voice_client = await voice_channel.connect()
        else:
            voice_client = interaction.guild.voice_client

        if "https://" in query or "youtube.com" in query:
            music_player.add_to_queue(query)
        else:
            url = await search_video_url(query)
            if not url:
                await interaction.response.send_message("❌ No Song/Video found", ephemeral=True)
                return
            music_player.add_to_queue(url)

        await interaction.response.send_message(f"🎵 Added to queue. Position: {music_player.get_queue_length()}")

        if not music_player.is_playing:
            await music_player.play_next(voice_client)

            view = MusicControlView(music_player, voice_client, interaction)

            async def update_now_playing(url):
                if view.now_playing_message:
                    await view.now_playing_message.edit(content=f"🎶 Playing: {url}", view=view)

            music_player.set_update_callback(update_now_playing)

            view.now_playing_message = await interaction.channel.send(
                f"🎶 Playing: {music_player.current_song}",
                view=view
            )

    except Exception as e:
        await interaction.response.send_message("Could not connect to the voice channel!", ephemeral=True)
        print(f"Error connecting to voice channel: {e}")


@tree.command(name="skip", description="Skip the currently playing song")
async def skip(interaction: discord.Interaction):
    if not interaction.guild.voice_client:
        await interaction.response.send_message("I'm not playing anything!", ephemeral=True)
        return

    if interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏭️ Skipping to next song...")
    else:
        await interaction.response.send_message("Nothing is playing!", ephemeral=True)


@tree.command(name="stop", description="Stop the music and clear the queue")
async def stop(interaction: discord.Interaction):
    if not interaction.guild.voice_client:
        await interaction.response.send_message("I'm not playing anything!", ephemeral=True)
        return

    music_player.clear_queue()
    interaction.guild.voice_client.stop()
    await interaction.guild.voice_client.disconnect()
    await interaction.response.send_message("⏹️ Playback stopped and queue cleared")


@tree.command(name="queue", description="Show the current music queue")
async def queue(interaction: discord.Interaction):
    if music_player.get_queue_length() == 0 and not music_player.current_song:
        await interaction.response.send_message("Queue is empty")
        return

    queue_list = "🎵 **Music Queue:**\n"
    if music_player.current_song:
        queue_list += f"**Now Playing:** {music_player.current_song}\n"

    if music_player.get_queue_length() > 0:
        queue_list += "\n**Up Next:**\n"
        for i, song in enumerate(music_player.queue, 1):
            queue_list += f"{i}. {song}\n"

    await interaction.response.send_message(queue_list)


def main() -> None:
    bot.run(token=TOKEN)


if __name__ == "__main__":
    main()
