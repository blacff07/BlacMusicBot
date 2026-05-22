# ˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼

### ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴜꜱɪᴄ ꜱᴛʀᴇᴀᴍɪɴɢ ʙᴏᴛ

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://pyrogram.org)
[![PyTgCalls](https://img.shields.io/badge/PyTgCalls-Latest-blueviolet?style=for-the-badge)](https://pytgcalls.github.io)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://cloud.mongodb.com)
[![Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br/>

[**Support Channel**](https://t.me/TechTipsCode) · [**Support Chat**](https://t.me/SarangCafes) · [**Source Code**](https://github.com/blaceff07/BlacMusicBot)

</div>

---

## 📌 Overview

**BlacMusic** is a production-grade Telegram music bot that streams studio-quality audio and video directly into Telegram group voice chats. Built on top of Pyrogram and PyTgCalls, it uses actual Telegram user accounts (assistants) to join and stream — giving it full native voice chat support with zero quality loss.

It requires no external API keys. YouTube search and downloading are handled entirely through `yt-dlp` and `youtubesearchpython`, making it completely self-contained.

---

## ✨ Features

| Category | Details |
|---|---|
| 🎵 **Audio Streaming** | Opus/48kHz studio-quality audio via PyTgCalls |
| 📺 **Video Streaming** | Full video stream support with `/vplay` |
| 🔍 **YouTube Search** | No API key — scrapes YouTube natively |
| 📋 **Queue System** | Per-group queue with position tracking |
| 🔀 **Shuffle & Loop** | Full shuffle, single-track and full-queue loop |
| ⏩ **Seek** | Jump to any timestamp mid-track |
| 🔁 **Autoplay** | Mood-based related track auto-queue when queue empties |
| 💡 **Suggestions** | 3 inline song suggestion buttons when queue ends |
| 👥 **Multi-Assistant** | Up to 3 userbot sessions, load balanced |
| 🛡 **Anti-Freeze** | Dead session detection, FloodWait recovery, auth error skipping |
| 🖼 **Now Playing Cards** | Frosted-glass thumbnail generator with track metadata |
| 📢 **Broadcast** | Sudo-only mass message to all groups and users |
| 🔇 **Channel Play** | Stream in channel voice chats |
| 🗄 **MongoDB** | Full persistence — settings, auth lists, blacklists, queue |
| 🔧 **Configurable** | All branding, images, links and limits via environment variables |
| 🚫 **Moderation** | Global ban, user blacklist, group blacklist, maintenance mode |

---

## 🏗 Architecture

```
BlacMusicBot/
├── BlacMusic/
│   ├── core/
│   │   ├── bot.py          → Pyrogram bot client
│   │   ├── userbot.py      → Assistant session manager (anti-freeze)
│   │   ├── calls.py        → PyTgCalls voice chat handler
│   │   ├── mongo.py        → MongoDB database layer
│   │   ├── youtube.py      → yt-dlp / search wrapper
│   │   ├── lang.py         → Localization system
│   │   ├── telegram.py     → Telegram utility helpers
│   │   └── preload.py      → Background track pre-downloader
│   ├── helpers/
│   │   ├── _autoplay.py    → Autoplay engine & suggestion builder
│   │   ├── _inline.py      → Inline keyboard builder
│   │   ├── _thumbnails.py  → Now Playing card generator
│   │   ├── _queue.py       → Queue management
│   │   └── _play.py        → Play flow helpers
│   ├── plugins/
│   │   ├── playback-controls/  → play, pause, skip, seek, loop, shuffle...
│   │   ├── admin-controles/    → broadcast, sudo, gban, maintenance...
│   │   ├── information/        → start, ping, stats, active
│   │   ├── events/             → callbacks, inline query, autoplay cb
│   │   └── settings/           → auth, blacklist, channel play
│   └── locales/
│       └── en.json         → English string table
├── config.py               → Configuration loader
├── Dockerfile              → Railway / Docker build
├── railway.toml            → Railway deployment config
└── sample.env              → Environment variable template
```

---

## ⚙️ Prerequisites

Before deploying, make sure you have these ready:

| Requirement | Where to get |
|---|---|
| **API ID & Hash** | [my.telegram.org/apps](https://my.telegram.org/apps) — create an app |
| **Bot Token** | [@BotFather](https://t.me/BotFather) — `/newbot` |
| **MongoDB URI** | [MongoDB Atlas](https://cloud.mongodb.com) — free M0 cluster |
| **Owner ID** | [@userinfobot](https://t.me/userinfobot) — your Telegram user ID |
| **Logger Group ID** | Create a private group → add bot as admin → forward a message to [@getmyid_bot](https://t.me/getmyid_bot) |
| **String Session** | [@StringFatherBot](https://t.me/StringFatherBot) — Pyrogram session string for assistant account |

> ⚠️ The assistant account is a **real Telegram user account**, not a bot. Use a secondary account. Do not use your main account.

---

## 🚀 Hosting Guide

### Option 1 — Railway *(Easiest, recommended)*

Railway builds and runs the bot using the included `Dockerfile` — no server knowledge needed.

**Steps:**

**1.** Fork or upload this repo to your GitHub account

**2.** Go to [railway.app](https://railway.app) → Sign in with GitHub → **New Project** → **Deploy from GitHub Repo** → select your repo

**3.** Once the repo is linked, go to your project → **Variables** tab → click **Raw Editor** and paste your environment variables:

```
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_DB_URI=your_mongo_uri
OWNER_ID=your_user_id
LOGGER_ID=your_logger_group_id
STRING_SESSION=your_session_string
```

**4.** Click **Save** — Railway will automatically redeploy with the new variables

**5.** Go to **Deployments** tab and watch the build logs. Once you see `˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼ started successfully!` the bot is live.

> ℹ️ Railway's free Hobby plan includes $5/month credit — enough for a small bot. For heavy usage, upgrade or use a VPS.

---

### Option 2 — VPS *(Ubuntu 22.04 / Debian 12)*

Best for 24/7 uptime and full control.

**Minimum specs:** 1 vCPU · 1 GB RAM · 10 GB storage

#### Step 1 — Install system dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv ffmpeg git curl
```

#### Step 2 — Clone the repository

```bash
git clone https://github.com/blaceff07/BlacMusicBot.git
cd BlacMusicBot
```

#### Step 3 — Set up a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4 — Configure environment variables

```bash
cp sample.env .env
nano .env
```

Fill in all required values, save with `Ctrl+O`, exit with `Ctrl+X`.

#### Step 5 — Test run

```bash
python -m BlacMusic
```

If you see `˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼ started successfully!` — everything is working. Press `Ctrl+C` to stop, then set up the service.

#### Step 6 — Run as a systemd service (auto-start, auto-restart)

```bash
sudo nano /etc/systemd/system/blacmusic.service
```

Paste the following (update paths if your user is not root):

```ini
[Unit]
Description=BlacMusic Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/BlacMusicBot
ExecStart=/root/BlacMusicBot/venv/bin/python -m BlacMusic
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable blacmusic
sudo systemctl start blacmusic
```

Check status and live logs:

```bash
sudo systemctl status blacmusic
sudo journalctl -u blacmusic -f
```

---

### Option 3 — Docker

```bash
# Build the image
docker build -t blacmusic .

# Run with your env file
docker run -d --name blacmusic --env-file .env --restart unless-stopped blacmusic

# View logs
docker logs -f blacmusic
```

---

## 📖 Commands Reference

### 🎵 Playback — available to all users

| Command | Description |
|---|---|
| `/play <query or URL>` | Search YouTube and play audio in voice chat |
| `/vplay <query or URL>` | Search YouTube and play video in voice chat |
| `/queue` | Display the current track queue |
| `/autoplay on/off` | Enable or disable mood-based autoplay |
| `/ping` | Check bot latency and system status |
| `/help` | Show the help menu |

### 🔧 Controls — admin or auth users only

| Command | Description |
|---|---|
| `/pause` | Pause the current stream |
| `/resume` | Resume a paused stream |
| `/skip` | Skip to the next track in queue |
| `/stop` | Stop streaming and clear the queue |
| `/seek <mm:ss>` | Jump to a specific timestamp |
| `/loop` | Cycle loop mode (off → track → queue) |
| `/shuffle` | Shuffle the current queue |
| `/auth <user>` | Authorise a user to use controls |
| `/unauth <user>` | Revoke a user's authorisation |

### 👑 Sudo — sudo users and owner only

| Command | Description |
|---|---|
| `/stats` | Full bot statistics (users, chats, uptime, RAM) |
| `/broadcast <text>` | Send a message to all groups |
| `/broadcast -user <text>` | Send to all users too |
| `/stop_broadcast` | Stop an active broadcast |
| `/addsudo <user>` | Add a sudo user |
| `/rmsudo <user>` | Remove a sudo user |
| `/gban <user>` | Globally ban a user from all bot features |
| `/ungban <user>` | Lift a global ban |
| `/maintenance on/off` | Toggle maintenance mode (blocks non-sudo usage) |
| `/restart` | Restart the bot process |
| `/logs` | Retrieve the current log file |
| `/eval <code>` | Execute arbitrary Python code |

---

## 🔁 Autoplay & Suggestions

When the queue empties, the bot always sends **3 inline song suggestion buttons** based on the mood of the last track played. The user can tap any button to instantly queue and play that song.

If **autoplay is enabled** (`/autoplay on`), the bot additionally auto-queues one related track silently, keeping the voice chat alive without any user input. User requests always take priority — if someone does `/play`, it goes into the queue and plays; autoplay resumes after the user's queue drains.

Autoplay state persists across bot restarts via MongoDB.

---

## 🔒 Security Notes

- Never commit your `.env` file — it is already listed in `.gitignore`
- Rotate your `STRING_SESSION` immediately if you suspect it is compromised
- The bot catches all dead/banned/expired session errors and skips the assistant gracefully — it will never freeze due to a bad session
- MongoDB URI includes your database password — treat it like a password
- The logger group should be private and contain only trusted admins

---

## 🛠 Troubleshooting

| Problem | Fix |
|---|---|
| Bot starts but doesn't join voice chat | Make sure the assistant account is not banned or restricted |
| `ModuleNotFoundError` on start | Run `pip install -r requirements.txt` again inside your venv |
| `FloodWait` errors frequently | Add `STRING_SESSION2` and `STRING_SESSION3` to spread load |
| Songs not downloading | Update yt-dlp: `pip install -U yt-dlp` |
| Thumbnails not generating | Check `ffmpeg` is installed: `ffmpeg -version` |
| Bot crashes on startup | Check `.env` — all 7 required variables must be filled |
| Logger group not receiving messages | Bot must be an **admin** in the logger group |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `pyrogram` / `kurigram` | Telegram MTProto client |
| `py-tgcalls` + `ntgcalls` | WebRTC voice chat streaming |
| `yt-dlp` | YouTube audio/video downloading |
| `youtubesearchpython` | YouTube search without API key |
| `motor` + `pymongo` | Async MongoDB driver |
| `Pillow` | Thumbnail image generation |
| `httpx` | HTTP client (bot name fetch at startup) |
| `python-dotenv` | `.env` file loading |
| `ffmpeg` *(system)* | Audio processing |

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

**˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼**

[Channel](https://t.me/TechTipsCode) · [Support](https://t.me/SarangCafes) · [GitHub](https://github.com/blaceff07/BlacMusicBot)

*Built for quality. Hosted for free.*

</div>