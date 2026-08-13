# 🦘 Bandicoot Discord Bot

Bandicoot is a music-only Discord bot written in Python. It plays audio from YouTube, manages a per-server queue, and can load playlists straight from the [DashCord](https://github.com/AgusLasalvia/dashcord) API. It's the Discord-facing companion to DashCord.

## 🚀 Features

- **Music Playback:** Play music from YouTube links or search queries, manage the queue, skip, stop, and control playback directly from Discord.
- **Playlist Integration:** Fetch playlists saved in DashCord via its API and queue an entire playlist with one command, with interactive playlist selection via Discord UI components.
- **Modern Discord UI:** Uses Discord's slash commands and interactive UI elements (buttons, selects) for a smooth user experience.
- **Auto-disconnect:** Leaves the voice channel automatically once it's left alone.

## 🛠️ Technology Stack

- **Python 3**
- **discord.py**: For Discord bot framework and UI components.
- **yt-dlp**: For searching, downloading, and streaming audio from YouTube.
- **PyNaCl, ffmpeg-python**: For audio processing and voice support.
- **aiohttp**: For async HTTP requests to the DashCord API.
- **python-dotenv**: For environment variable management.

## 🏗️ Project Structure

```
main.py                # Bot entry point, command and event registration
logic/
  player.py            # Music player logic, queue management, YouTube streaming
  api.py                # DashCord API integration: auth and playlist fetching
UI/
  music_view.py         # Discord UI components for music and playlist control
requirements.txt        # Python dependencies
bot.service              # Example systemd service file for deployment
```

## ⚙️ Setup & Usage

1. **Clone the repository:**
   ```sh
   git clone https://github.com/AgusLasalvia/bandicoot-discord-bot.git
   cd bandicoot-discord-bot
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Create a `.env` file with:
     ```
     DISCORD_TOKEN=your-discord-token
     API_URL=your-dashcord-api-url
     BOT_USERNAME=your-dashcord-service-username
     BOT_PASSWORD=your-dashcord-service-password
     ```
   - `API_URL`, `BOT_USERNAME`, and `BOT_PASSWORD` are only required for the `/playlists` command, which authenticates against the DashCord API (`POST /api/auth/login`) and reads from `/api/playlists/names` and `/api/playlists/songs`.

4. **Run the bot:**
   ```sh
   python main.py
   ```

5. **Usage:**
   - Use `/play`, `/skip`, `/stop`, `/queue`, and `/playlists` in Discord.
   - `/sync` re-syncs slash commands with Discord (intended for developers).
   - Interactive music controls and playlist selection are available via Discord UI.

## 🌍 Deployment

Deployable to:
- Railway, Render, Replit, Heroku, or your own VPS.
- Includes a sample `bot.service` for systemd-based deployment.

## 🙏 Credits

- Developed by AgusLasalvia

## 📄 License

MIT License. See the LICENSE file for details.
