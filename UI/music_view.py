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
