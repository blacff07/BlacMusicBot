<div align="center">

# 🎵 ˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼

**Advanced Telegram Voice Chat Music Streaming Bot**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-Latest-green?style=for-the-badge)](https://pyrogram.org)
[![Railway](https://img.shields.io/badge/Deploy-Railway-purple?style=for-the-badge&logo=railway)](https://railway.app)

</div>

---

## ✨ Features

- 🎵 **Studio-Quality Streaming** — Opus/48kHz audio via PyTgCalls
- 🔍 **YouTube Search** — No API key required
- 📋 **Queue System** — Unlimited queuing with shuffle & loop
- 🎛 **Full Playback Controls** — Seek, skip, pause, resume, replay
- 📺 **Video Mode** — Stream video into voice chats (`/vplay`)
- 👥 **Multi-Assistant** — Up to 3 userbot sessions for more groups
- 🛡 **Anti-Ban Hardened** — Dead session detection, FloodWait recovery
- 🖼 **Custom Thumbnails** — Frosted-glass Now Playing cards
- 🔧 **Fully Configurable** — All branding/images via environment variables
- 🗄 **MongoDB Persistence** — Settings, auth lists, blacklists survive restarts

---

## 🚀 Hosting

### Option A — Railway (Recommended for beginners)

1. Fork/upload this repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
3. Add all environment variables from `sample.env` in the Railway dashboard
4. Railway auto-builds with the included `Dockerfile` — done

> ⚠️ Railway free tier sleeps on inactivity. Use a paid plan or a VPS for 24/7.

### Option B — VPS (Ubuntu/Debian)

```bash
# 1. Install system deps
sudo apt update && sudo apt install -y python3 python3-pip ffmpeg git

# 2. Clone your repo
git clone https://github.com/yourusername/BlacMusicBot && cd BlacMusicBot

# 3. Install Python deps
pip install -r requirements.txt

# 4. Configure
cp sample.env .env
nano .env   # fill in all required values

# 5. Run
python -m BlacMusic
```

**Keep alive with systemd:**
```ini
# /etc/systemd/system/blacmusic.service
[Unit]
Description=BlacMusic Bot
After=network.target

[Service]
WorkingDirectory=/root/BlacMusicBot
ExecStart=/usr/bin/python3 -m BlacMusic
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable blacmusic
sudo systemctl start blacmusic
```

### Option C — Docker

```bash
docker build -t blacmusic .
docker run -d --env-file .env blacmusic
```

---

## ⚙️ Configuration

Copy `sample.env` → `.env` and fill in your values.

### Required

| Variable | Where to get it |
|---|---|
| `API_ID` | [my.telegram.org/apps](https://my.telegram.org/apps) |
| `API_HASH` | [my.telegram.org/apps](https://my.telegram.org/apps) |
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) |
| `MONGO_DB_URI` | [MongoDB Atlas](https://cloud.mongodb.com) free tier |
| `OWNER_ID` | [@userinfobot](https://t.me/userinfobot) |
| `LOGGER_ID` | Create private group → add bot as admin → get chat ID |
| `STRING_SESSION` | [@StringFatherBot](https://t.me/StringFatherBot) |

### Optional Branding (all have defaults)

| Variable | Default | Description |
|---|---|---|
| `BOT_NAME` | `˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼` | Watermark shown in messages |
| `BOT_ABOUT` | *(tagline)* | Bot description |
| `SOURCE_URL` | GitHub link | Source button in /start |
| `SUPPORT_CHANNEL` | `t.me/blacmusic` | Channel button |
| `SUPPORT_CHAT` | `t.me/blacmusicchat` | Support button |
| `START_IMG` | *(default)* | /start command image |
| `PING_IMG` | *(default)* | /ping command image |

See `sample.env` for the full list.

---

## 📖 Commands

### User
| Command | Description |
|---|---|
| `/play [query/url]` | Play audio in voice chat |
| `/vplay [query/url]` | Play video in voice chat |
| `/queue` | Show current queue |
| `/ping` | Bot status & latency |
| `/help` | Help menu |

### Admin
| Command | Description |
|---|---|
| `/pause` | Pause stream |
| `/resume` | Resume stream |
| `/skip` | Skip current track |
| `/stop` | Stop and clear queue |
| `/seek [mm:ss]` | Seek to timestamp |
| `/loop` | Toggle loop mode |

### Sudo
| Command | Description |
|---|---|
| `/stats` | Bot statistics |
| `/broadcast` | Message all chats |
| `/addsudo` / `/rmsudo` | Manage sudo users |
| `/gban` / `/ungban` | Global ban |
| `/maintenance` | Toggle maintenance mode |
| `/restart` | Restart bot |
| `/logs` | Get log file |

---

## 🔒 Security

- Never commit `.env` to git (already in `.gitignore`)
- Generate a fresh `STRING_SESSION` if you suspect compromise
- The bot detects dead/banned sessions and skips them safely

---

## 📝 Notes

- `ffmpeg` must be installed on the host — Railway's Dockerfile handles this automatically
- Your assistant account **must NOT** have 2FA set with an unknown password on its session
- The bot must be an **admin** in the logger group

---

<div align="center">

**Made with 🎵 — BlacMusic**

</div>