import discord
from logic.player import SongInfo


def build_now_playing_embed(song: SongInfo, player) -> discord.Embed:
    embed = discord.Embed(
        title="🎶 Now Playing",
        description=f"**[{song.title}]({song.url})**",
        color=discord.Color.blurple(),
    )
    if song.thumbnail:
        embed.set_thumbnail(url=song.thumbnail)

    embed.add_field(name="Duration", value=song.format_duration(), inline=True)
    embed.add_field(name="Queue", value=f"{player.get_queue_length()} song(s) up next", inline=True)

    flags = []
    if player.loop:
        flags.append("🔁 Loop")
    if player.shuffle:
        flags.append("🔀 Shuffle")
    if flags:
        embed.add_field(name="Mode", value=" | ".join(flags), inline=True)

    embed.set_footer(text="Bandicoot Music")
    return embed


def build_queue_embed(player) -> discord.Embed:
    embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.blurple())

    if player.current_song:
        embed.add_field(
            name="Now Playing",
            value=f"**[{player.current_song.title}]({player.current_song.url})** — {player.current_song.format_duration()}",
            inline=False,
        )

    if player.queue:
        lines = []
        for i, song in enumerate(list(player.queue)[:15], 1):
            lines.append(f"`{i}.` [{song.title}]({song.url}) — {song.format_duration()}")
        if len(player.queue) > 15:
            lines.append(f"*... and {len(player.queue) - 15} more*")
        embed.add_field(name="Up Next", value="\n".join(lines), inline=False)
    else:
        embed.add_field(name="Up Next", value="Queue is empty", inline=False)

    flags = []
    if player.loop:
        flags.append("🔁 Loop ON")
    if player.shuffle:
        flags.append("🔀 Shuffle ON")
    embed.set_footer(text=" | ".join(flags) if flags else "Bandicoot Music")
    return embed


class MusicControlView(discord.ui.View):
    def __init__(self, player, voice_client, ctx):
        super().__init__(timeout=None)
        self.player = player
        self.voice_client = voice_client
        self.ctx = ctx
        self.now_playing_message = None
        self._paused = False

    def _pause_button(self) -> discord.ui.Button:
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.custom_id == "toggle_play":
                return child

    async def _refresh_embed(self, interaction: discord.Interaction):
        if self.player.current_song and self.now_playing_message:
            embed = build_now_playing_embed(self.player.current_song, self.player)
            await self.now_playing_message.edit(embed=embed, view=self)

    @discord.ui.button(label="⏸ Pause", style=discord.ButtonStyle.primary, custom_id="toggle_play")
    async def toggle_play(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.voice_client.is_playing():
            self.voice_client.pause()
            button.label = "▶ Resume"
            button.style = discord.ButtonStyle.success
            await interaction.response.edit_message(view=self)
        elif self.voice_client.is_paused():
            self.voice_client.resume()
            button.label = "⏸ Pause"
            button.style = discord.ButtonStyle.primary
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)

    @discord.ui.button(label="⏭ Skip", style=discord.ButtonStyle.secondary, custom_id="skip")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.voice_client.is_playing() or self.voice_client.is_paused():
            self.voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped.", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing to skip.", ephemeral=True)

    @discord.ui.button(label="🔀 Shuffle", style=discord.ButtonStyle.secondary, custom_id="shuffle")
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        enabled = self.player.toggle_shuffle()
        button.style = discord.ButtonStyle.success if enabled else discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            f"🔀 Shuffle {'enabled' if enabled else 'disabled'}.", ephemeral=True
        )

    @discord.ui.button(label="🔁 Loop", style=discord.ButtonStyle.secondary, custom_id="loop")
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        enabled = self.player.toggle_loop()
        button.style = discord.ButtonStyle.success if enabled else discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            f"🔁 Loop {'enabled' if enabled else 'disabled'}.", ephemeral=True
        )

    @discord.ui.button(label="⏹ Stop", style=discord.ButtonStyle.danger, custom_id="stop")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.clear_queue()
        self.voice_client.stop()
        await self.voice_client.disconnect()
        embed = discord.Embed(
            title="⏹ Stopped",
            description="Playback stopped and queue cleared.",
            color=discord.Color.red(),
        )
        await interaction.response.edit_message(embed=embed, view=None)


class PlaylistSelectView(discord.ui.View):
    def __init__(self, playlists, callback_function):
        super().__init__(timeout=60)
        self.playlists = playlists
        self.callback_function = callback_function

        options = []
        for playlist in playlists:
            song_count = playlist.get("songCount") or playlist.get("song_count") or playlist.get("songs_count")
            description = f"{song_count} songs" if song_count else f"ID: {playlist.get('_id', 'N/A')}"
            options.append(
                discord.SelectOption(
                    label=playlist.get("name", "No name"),
                    value=playlist.get("_id", ""),
                    description=description,
                )
            )

        self.add_item(PlaylistSelect(options, callback_function))


class PlaylistSelect(discord.ui.Select):
    def __init__(self, options, callback_function):
        super().__init__(
            placeholder="Select a playlist...",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.callback_function = callback_function

    async def callback(self, interaction: discord.Interaction):
        selected_id = self.values[0]
        selected_name = next(
            (opt.label for opt in self.options if opt.value == selected_id), selected_id
        )
        await interaction.response.defer(ephemeral=True)
        await self.callback_function(interaction, selected_id, selected_name)
