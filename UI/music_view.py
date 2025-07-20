# music_view.py
import discord

class MusicControlView(discord.ui.View):
    def __init__(self, player, voice_client, ctx):
        super().__init__(timeout=None)
        self.player = player
        self.voice_client = voice_client
        self.ctx = ctx
        self.now_playing_message = None  # para actualizar el mensaje de reproducción

    @discord.ui.button(label="Play/Pause", style=discord.ButtonStyle.primary)
    async def toggle_play(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.voice_client.is_playing():
            self.voice_client.pause()
            await interaction.response.edit_message(content="⏸️ Paused", view=self)
        elif self.voice_client.is_paused():
            self.voice_client.resume()
            await interaction.response.edit_message(content=f"▶️ Playing: {self.player.current_song}", view=self)
        else:
            await interaction.response.send_message("No music left in Queue.", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.voice_client.is_playing() or self.voice_client.is_paused():
            self.voice_client.stop()
            await interaction.response.send_message("⏭️ Skiping...", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing to Skip.", ephemeral=True)


    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.clear_queue()
        self.voice_client.stop()
        await self.voice_client.disconnect()
        await interaction.response.edit_message(content="🛑 Player Stoped.", view=None)


class PlaylistSelectView(discord.ui.View):
    def __init__(self, playlists, callback_function):
        super().__init__(timeout=60)  # 60 segundos de timeout
        self.playlists = playlists
        self.callback_function = callback_function
        
        # Crear las opciones para el select
        options = []
        for playlist in playlists:
            options.append(
                discord.SelectOption(
                    label=playlist.get('name', 'Sin nombre'),
                    value=playlist.get('_id', ''),
                    description=f"ID: {playlist.get('_id', 'N/A')}"
                )
            )
        
        # Agregar el select al view
        self.add_item(PlaylistSelect(options, callback_function))


class PlaylistSelect(discord.ui.Select):
    def __init__(self, options, callback_function):
        super().__init__(
            placeholder="Selecciona una playlist...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.callback_function = callback_function

    async def callback(self, interaction: discord.Interaction):
        selected_playlist_id = self.values[0]
        selected_playlist_name = None
        
        # Encontrar el nombre de la playlist seleccionada
        for option in self.options:
            if option.value == selected_playlist_id:
                selected_playlist_name = option.label
                break
        
        # Deferir la respuesta para que la función callback pueda responder
        await interaction.response.defer(ephemeral=True)
        
        # Llamar a la función callback con el ID de la playlist
        await self.callback_function(interaction, selected_playlist_id, selected_playlist_name)
