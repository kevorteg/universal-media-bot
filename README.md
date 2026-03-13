# Universal Media discovered Bot (Open Source)

A powerful, autonomous media discovery and download manager. It discovers trending movies, finds high-quality torrents, and manages downloads through qBittorrent, all with a beautiful web dashboard.

## 🌟 Key Features
- **Universal Discovery**: Automatically finds trending movies using TMDB API.
- **Smart Torrent Integration**: Connects directly to qBittorrent Web UI.
- **Interactive Dashboard**: Manage your library, edit metadata, and monitor progress in real-time.
- **Auto-Pilot**: Scrapes and downloads new content every 6 hours automatically.
- **Telegram Notifications**: Get instant updates on your mobile.

## 🚀 Quick Setup

1. **Prerequisites**:
   - Python 3.10+
   - qBittorrent installed
   - TMDB API Key (Free)

2. **Installation**:
   ```bash
   git clone https://github.com/youruser/universal-media-bot.git
   cd universal-media-bot
   pip install -r requirements.txt
   ```

3. **Configuration**:
   - Rename `.env.example` to `.env` and fill in your keys.
   - Enable **Web UI** in qBittorrent (Tools -> Options -> Web UI).

4. **Launch**:
   - Double-click `¡CLIC_AQUI_PARA_INICIAR!.bat` on Windows or run `python main.py`.

## 🛠 Tech Stack
- **Backend**: Python, Flask, SQLite.
- **Download Engines**: yt-dlp, qBittorrent API.
- **Visuals**: Modern CSS (Glassmorphism), Vanilla JS.

## 📄 License
MIT License - Feel free to use and contribute!
