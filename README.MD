# 🦘 Bandicoot Discord Bot

Bandicoot is a feature-rich, extensible Discord bot written in Python. It provides advanced music playback, playlist management, custom AI responses, and more, designed for easy deployment and customization.

## 🚀 Features

- **Music Playback:** Play music from YouTube links or search queries, manage queues, skip, stop, and control playback directly from Discord.
- **Playlist Integration:** Fetch and play playlists from an external API, with interactive playlist selection via Discord UI components.
- **Custom AI Responses:** Integrates with an Ollama model (DeepSeek R1) for custom GPT-like responses.
- **User Verification:** Secure commands (like IP retrieval) that check user credentials against a database.
- **Modern Discord UI:** Uses Discord’s slash commands and interactive UI elements (buttons, selects) for a smooth user experience.
- **Extensible:** Easily add new commands, events, or integrations.

## 🛠️ Technology Stack

- **Python 3**
- **discord.py**: For Discord bot framework and UI components.
- **yt-dlp**: For downloading and streaming audio from YouTube.
- **PyNaCl, ffmpeg-python**: For audio processing and voice support.
- **pymysql**: For database interactions.
- **python-dotenv**: For environment variable management.
- **youtube-search-python**: For YouTube search functionality.
- **langdetect**: For language detection in AI prompts.
- **httpx, aiohttp**: For async HTTP requests to APIs and AI models.

## 🏗️ Project Structure

```
main.py                # Bot entry point, command and event registration
logic/
  player.py            # Music player logic, queue management, YouTube streaming
  api.py               # Playlist API integration, authentication
  custom_responses.py  # Custom commands, AI responses, user verification
  database.py          # Database access and user verification
UI/
  music_view.py        # Discord UI components for music and playlist control
requirements.txt       # Python dependencies
bot.service            # Example systemd service file for deployment
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
   - Create a `.env` file with at least:
     ```
     DISCORD_TOKEN=your-discord-token
     API_URL=your-playlist-api-url
     BOT_USERNAME=your-api-username
     BOT_PASSWORD=your-api-password
     ```

4. **Run the bot:**
   ```sh
   python main.py
   ```

5. **Usage:**
   - Use `/play`, `/skip`, `/stop`, `/queue`, `/playlists`, `/gpt`, and other slash commands in Discord.
   - Interactive music controls and playlist selection are available via Discord UI.

## 🌍 Deployment

Deployable to:
- Railway, Render, Replit, Heroku, or your own VPS.
- Includes a sample `bot.service` for systemd-based deployment.

## 🙏 Credits

- Developed by AgusLasalvia

## 📄 License

MIT License. See the LICENSE file for details.
