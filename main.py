import os
from typing import Final

from dotenv import load_dotenv

import discord
from discord import app_commands, Intents
from discord.ext import commands

# Logic
from logic.player import MusicPlayer, search_video_url
from logic.custom_responses import *
from logic.api import get_playlists, get_playlist_songs

# UI
from UI.music_view import MusicControlView, PlaylistSelectView

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


@tree.command(name="ip",description="If you use this, you are GAY, except my creator")
async def ip(interaction:discord.Interaction,username:str,password:str):
    await interaction.response.send_message(await get_ip(username,password))

@tree.command(name='gpt',description="CUSTOM Bandicoot GPT based on DeepSeek R1")
async def gpt(interaction:discord.Interaction,prompt:str):
    await interaction.response.defer()
    response = await ollama(prompt)
    await interaction.followup.send(f"🧠 {response}")


@tree.command(name="playlists", description="Mostrar y seleccionar playlists disponibles")
async def playlists(interaction: discord.Interaction):
    await interaction.response.defer()
    
    try:
        # Obtener las playlists de la API
        playlists_data = await get_playlists()
        
        if not playlists_data:
            await interaction.followup.send("❌ No se pudieron obtener las playlists o no hay playlists disponibles.", ephemeral=True)
            return
        
        # Crear la vista con el selector
        view = PlaylistSelectView(playlists_data, handle_playlist_selection)
        
        await interaction.followup.send(
            f"📋 **Playlists disponibles ({len(playlists_data)}):**\nSelecciona una playlist del menú desplegable:",
            view=view
        )
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error al obtener las playlists: {str(e)}", ephemeral=True)
        print(f"Error en comando playlists: {e}")


async def handle_playlist_selection(interaction: discord.Interaction, playlist_id: str, playlist_name: str):
    """
    Función callback que se ejecuta cuando el usuario selecciona una playlist
    """
    try:
        # Mostrar mensaje de confirmación de la playlist seleccionada
        await interaction.followup.send(f"🎵 Playlist seleccionada: **{playlist_name}**", ephemeral=True)
        
        # Obtener las canciones de la playlist
        youtube_ids = await get_playlist_songs(playlist_id)
        
        if not youtube_ids:
            await interaction.followup.send(f"❌ No se encontraron canciones en la playlist **{playlist_name}**", ephemeral=True)
            return
        
        # Convertir los IDs de YouTube a URLs completas
        added_count = 0
        for youtube_id in youtube_ids:
            youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"
            print(f"Agregando URL: {youtube_url}")
            music_player.add_to_queue(youtube_url)
            added_count += 1
        
        print(f"Total de canciones agregadas a la cola: {added_count}")
        print(f"Tamaño actual de la cola: {music_player.get_queue_length()}")
        
        # Verificar si el usuario está en un canal de voz
        if not interaction.user.voice:
            await interaction.followup.send(
                f"✅ **{added_count} canciones** agregadas a la cola de **{playlist_name}**\n"
                f"🎵 Únete a un canal de voz y usa `/play` para comenzar la reproducción",
                ephemeral=True
            )
            return
        
        voice_channel = interaction.user.voice.channel
        
        try:
            # Conectar al canal de voz si no está conectado
            if not interaction.guild.voice_client:
                voice_client = await voice_channel.connect()
            else:
                voice_client = interaction.guild.voice_client
            
            # Iniciar reproducción si no está reproduciendo
            if not music_player.is_playing:
                await music_player.play_next(voice_client)
                
                # Crear la vista de control de música
                view = MusicControlView(music_player, voice_client, interaction)
                
                async def update_now_playing(url):
                    if view.now_playing_message:
                        await view.now_playing_message.edit(content=f"🎶 Playing: {url}", view=view)
                
                music_player.set_update_callback(update_now_playing)
                
                view.now_playing_message = await interaction.channel.send(
                    f"🎶 Playing: {music_player.current_song}",
                    view=view
                )
                
                await interaction.followup.send(
                    f"✅ **{added_count} canciones** agregadas a la cola de **{playlist_name}**\n"
                    f"🎵 Reproducción iniciada automáticamente",
                    ephemeral=True
                )
            else:
                # Si ya está reproduciendo, solo mostrar el mensaje
                await interaction.followup.send(
                    f"✅ **{added_count} canciones** agregadas a la cola de **{playlist_name}**",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(
                f"✅ **{added_count} canciones** agregadas a la cola de **{playlist_name}**\n"
                f"❌ Error al conectar al canal de voz: {str(e)}",
                ephemeral=True
            )
            print(f"Error al conectar al canal de voz: {e}")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error al cargar la playlist: {str(e)}", ephemeral=True)
        print(f"Error en handle_playlist_selection: {e}")


@tree.command(name="sync", description="Sincronizar comandos con Discord (solo para desarrolladores)")
async def sync(interaction: discord.Interaction):
    try:
        await tree.sync()
        await interaction.response.send_message("✅ Comandos sincronizados correctamente!", ephemeral=True)
        print("Comandos sincronizados manualmente")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error al sincronizar: {str(e)}", ephemeral=True)
        print(f"Error en sincronización: {e}")



def main() -> None:
    bot.run(token=TOKEN)


if __name__ == "__main__":
    main()
